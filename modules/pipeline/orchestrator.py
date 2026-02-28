"""
PERSEPTOR v2.0 - Pipeline Orchestrator
Shared logic for standard and streaming analysis pipelines.
"""
import json
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import traceback
import os

from modules.logging_config import get_logger
from modules.ai_engine import (
    summarize_threat_report,
    extract_iocs_ttps_gpt,
    safe_json_parse,
    generate_more_sigma_rules_from_article,
    convert_sigma_to_siem_queries,
    generate_atomic_tests_from_sigma,
)
from modules.yara_generator import generate_yara_rules
from modules.sigma_generator import generate_sigma_rules_for_analysis, sigma_rules_to_yaml
from modules.siem_query_generator import generate_siem_queries, siem_queries_to_flat
from modules.mitre_mapping import map_iocs_to_mitre, get_mitre_tags, get_tactic_summary
from modules.sigma_matcher import load_sigma_rules_local, match_sigma_rules_with_report
from modules.database import ReportRepository
from modules.security import sanitize_for_json
from modules.pipeline.output_validator import OutputValidator as OV

logger = get_logger("orchestrator")

def run_analysis_pipeline_sync(
    text_content, images_ocr_text, combined_text, source_url, provider_name, model_name, openai_api_key, parent_dir
):
    """Run the full analysis pipeline synchronously with parallel AI calls."""
    
    # Use ThreadPoolExecutor for parallel AI tasks
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Task 1: Threat Summary
        future_summary = executor.submit(
            summarize_threat_report,
            text=combined_text,
            openai_api_key=openai_api_key,
            provider_name=provider_name,
            model_name=model_name,
        )
        
        # Task 2: IOC/TTP Extraction
        future_ioc = executor.submit(
            extract_iocs_ttps_gpt,
            combined_text,
            openai_api_key=openai_api_key,
            provider_name=provider_name,
            model_name=model_name,
        )
        
        # Task 3: AI Sigma Rules
        future_ai_sigma = executor.submit(
            generate_more_sigma_rules_from_article,
            article_text=text_content,
            images_ocr_text=images_ocr_text,
            openai_api_key=openai_api_key,
            provider_name=provider_name,
            model_name=model_name,
        )
        
        # Collect results with fallbacks
        try:
            threat_summary = future_summary.result(timeout=300)
        except Exception as e:
            logger.error(f"Error generating threat summary: {e}")
            threat_summary = "Error generating threat summary"
            
        try:
            gpt_json_str = future_ioc.result(timeout=300)
            is_valid, parsed = OV.validate_json(gpt_json_str)
            if is_valid and isinstance(parsed, dict):
                analysis_data = parsed
            else:
                analysis_data = safe_json_parse(gpt_json_str)
        except Exception as e:
            logger.error(f"Error in IOC/TTP analysis: {e}")
            analysis_data = {"error": "Error in IOC/TTP analysis"}
            
        try:
            more_sigma_rules = future_ai_sigma.result(timeout=300)
            if more_sigma_rules and not more_sigma_rules.startswith("Error"):
                rules = []
                current_rule = []
                for line in more_sigma_rules.split("\\n"):
                    if line.strip().startswith("title:"):
                        if current_rule:
                            rules.append("\\n".join(current_rule))
                        current_rule = [line]
                    elif not any(skip in line for skip in ["–––––––", "These rules can be further tuned", "Below are two Sigma rules", "This rule detects", "This query searches"]):
                        if current_rule or line.strip():
                            current_rule.append(line)
                if current_rule:
                    rules.append("\\n".join(current_rule))
                more_sigma_rules = "\\n\\n".join(rules)
            else:
                more_sigma_rules = ""
        except Exception as e:
            logger.error(f"Error generating AI Sigma rules: {e}")
            more_sigma_rules = ""

    # Secondary parallel stage for rule generation (depends on analysis_data)
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_yara = executor.submit(generate_yara_rules, analysis_data)
        future_mitre = executor.submit(map_iocs_to_mitre, analysis_data)
        future_ioc_sigma = executor.submit(generate_sigma_rules_for_analysis, analysis_data, article_url=source_url)
        
        try:
            yara_rules = future_yara.result(timeout=120)
        except Exception:
            yara_rules = []
            
        try:
            mitre_techniques = future_mitre.result(timeout=120)
            mitre_tags = get_mitre_tags(mitre_techniques)
            tactic_summary = get_tactic_summary(mitre_techniques)
        except Exception:
            mitre_techniques, mitre_tags, tactic_summary = [], [], {}
            
        try:
            ioc_sigma_rules = future_ioc_sigma.result(timeout=120)
            ioc_sigma_yaml = sigma_rules_to_yaml(ioc_sigma_rules)
        except Exception:
            ioc_sigma_rules, ioc_sigma_yaml = [], ""

    all_sigma_yaml = ioc_sigma_yaml
    if more_sigma_rules:
        all_sigma_yaml = all_sigma_yaml + "\\n---\\n" + more_sigma_rules if all_sigma_yaml else more_sigma_rules

    # SIEM and Atomic tests stage
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_siem = executor.submit(lambda: siem_queries_to_flat(generate_siem_queries(analysis_data)))
        
        def _do_siem_refine():
            if not more_sigma_rules: return None
            return convert_sigma_to_siem_queries(
                sigma_rules=more_sigma_rules,
                openai_api_key=openai_api_key,
                provider_name=provider_name,
                model_name=model_name,
            )
        future_siem_ai = executor.submit(_do_siem_refine)
        
        def _do_atomic():
            if not all_sigma_yaml or len(all_sigma_yaml.strip()) < 20: return []
            return generate_atomic_tests_from_sigma(
                sigma_rules=all_sigma_yaml,
                threat_context=threat_summary,
                openai_api_key=openai_api_key,
                provider_name=provider_name,
                model_name=model_name,
            )
        future_atomic = executor.submit(_do_atomic)

        try:
            siem_queries = future_siem.result(timeout=120)
        except Exception:
            siem_queries = {}

        try:
            ai_siem = future_siem_ai.result(timeout=300)
            if isinstance(ai_siem, dict):
                for platform in ("splunk", "qradar", "elastic", "sentinel"):
                    if platform in ai_siem and platform in siem_queries:
                        existing = siem_queries[platform].get("query", "")
                        ai_query = ai_siem[platform].get("query", "")
                        if ai_query and ai_query != "N/A":
                            siem_queries[platform]["query"] = existing + "\\n\\n/* AI-Refined */\\n" + ai_query
        except Exception:
            pass

        try:
            atomic_tests = future_atomic.result(timeout=300)
        except Exception:
            atomic_tests = []

    # Global Sigma Match
    try:
        sigma_rules_directory = os.path.join(parent_dir, "Global_Sigma_Rules")
        if os.path.exists(sigma_rules_directory):
            all_rules = load_sigma_rules_local(sigma_rules_directory)
            sigma_matches = match_sigma_rules_with_report(
                sigma_rules=all_rules,
                analysis_data=analysis_data,
                report_text=combined_text.lower(),
                root_directory=sigma_rules_directory,
                mitre_techniques=mitre_techniques,
                threshold=25.0,
                max_results=15,
            )
        else:
            sigma_matches = []
    except Exception as e:
        logger.error(f"Error in Sigma matching: {e}")
        sigma_matches = []

    response = {
        "threat_summary": threat_summary,
        "analysis_data": {
            "indicators_of_compromise": analysis_data.get("indicators_of_compromise", {}),
            "ttps": analysis_data.get("ttps", []),
            "threat_actors": analysis_data.get("threat_actors", []),
            "tools_or_malware": analysis_data.get("tools_or_malware", [])
        },
        "mitre_mapping": {
            "techniques": mitre_techniques,
            "tactic_summary": tactic_summary,
            "tags": mitre_tags,
        },
        "yara_rules": yara_rules,
        "ioc_sigma_rules": ioc_sigma_rules,
        "generated_sigma_rules": all_sigma_yaml,
        "siem_queries": siem_queries,
        "atomic_tests": atomic_tests,
        "sigma_matches": sigma_matches,
    }

    response = sanitize_for_json(response)

    # Save to db
    try:
        report_data = {
            "id": str(uuid.uuid4()),
            "url": source_url,
            "timestamp": datetime.now().isoformat(),
            "provider": provider_name,
            "model": model_name,
            **response
        }
        ReportRepository.create(report_data)
        logger.info(f"Saved report with ID: {report_data['id']}")
    except Exception as e:
        logger.error(f"Error saving report: {e}")

    return response


def run_analysis_pipeline_stream(
    text_content, images_ocr_text, combined_text, source_url, provider_name, model_name, openai_api_key, parent_dir, sse
):
    """Run the full analysis pipeline using SSE generator for streaming updates."""
    try:
        # Stage 2b: Parallel AI calls
        yield sse("ai_parallel", 22, "Starting parallel AI analysis...")
        
        threat_summary = "Could not generate threat summary"
        analysis_data = {}
        more_sigma_rules = ""

        def _do_threat_summary():
            return summarize_threat_report(
                text=combined_text,
                openai_api_key=openai_api_key,
                provider_name=provider_name,
                model_name=model_name,
            )

        def _do_ioc_extraction():
            gpt_json_str = extract_iocs_ttps_gpt(
                combined_text,
                openai_api_key=openai_api_key,
                provider_name=provider_name,
                model_name=model_name,
            )
            is_valid, parsed = OV.validate_json(gpt_json_str)
            if is_valid and isinstance(parsed, dict):
                return parsed
            return safe_json_parse(gpt_json_str)

        def _do_ai_sigma():
            return generate_more_sigma_rules_from_article(
                article_text=text_content,
                images_ocr_text=images_ocr_text,
                openai_api_key=openai_api_key,
                provider_name=provider_name,
                model_name=model_name,
            )

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_summary = executor.submit(_do_threat_summary)
            future_ioc = executor.submit(_do_ioc_extraction)
            future_ai_sigma = executor.submit(_do_ai_sigma)

            yield sse("threat_summary", 25, "AI analyzing threat landscape...")
            yield sse("ioc_extraction", 25, "AI extracting IoCs and TTPs...")
            yield sse("ai_sigma", 25, "AI generating Sigma rules...")

            # Wait for threat summary
            try:
                threat_summary = future_summary.result(timeout=300)
                yield sse("threat_summary_done", 40, "Threat summary complete", {"threat_summary": threat_summary})
            except Exception as e:
                logger.error(f"Threat summary error: {e}")
                yield sse("threat_summary_done", 40, f"Threat summary failed: {str(e)[:100]}")

            # Wait for IoC extraction
            try:
                analysis_data = future_ioc.result(timeout=300)
                ioc_count = sum(len(v) for v in analysis_data.get("indicators_of_compromise", {}).values() if isinstance(v, list))
                yield sse("ioc_done", 50, f"Extracted {ioc_count} IoCs", {
                    "analysis_data": {
                        "indicators_of_compromise": analysis_data.get("indicators_of_compromise", {}),
                        "ttps": analysis_data.get("ttps", []),
                        "threat_actors": analysis_data.get("threat_actors", []),
                        "tools_or_malware": analysis_data.get("tools_or_malware", []),
                    }
                })
            except Exception as e:
                logger.error(f"IoC extraction error: {e}")
                yield sse("ioc_done", 50, f"IoC extraction failed: {str(e)[:100]}")

            # Wait for AI Sigma
            try:
                raw_sigma = future_ai_sigma.result(timeout=300)
                if raw_sigma and not raw_sigma.startswith("Error"):
                    rules = []
                    current_rule = []
                    for line in raw_sigma.split("\n"):
                        if line.strip().startswith("title:"):
                            if current_rule:
                                rules.append("\n".join(current_rule))
                            current_rule = [line]
                        elif not any(skip in line for skip in ["–––––––", "These rules can be further tuned", "Below are two Sigma rules", "This rule detects", "This query searches"]):
                            if current_rule or line.strip():
                                current_rule.append(line)
                    if current_rule:
                        rules.append("\n".join(current_rule))
                    more_sigma_rules = "\n\n".join(rules)
            except Exception as e:
                logger.error(f"AI Sigma error: {e}")

        # Stage 3: Parallel rule generation
        yield sse("rules", 55, "Generating detection rules...")
        yara_rules = []
        mitre_techniques = []
        mitre_tags = []
        tactic_summary = {}
        ioc_sigma_rules = []
        ioc_sigma_yaml = ""
        sigma_matches = []

        def _do_yara(): return generate_yara_rules(analysis_data)
        def _do_mitre():
            techs = map_iocs_to_mitre(analysis_data)
            return techs, get_mitre_tags(techs), get_tactic_summary(techs)
        def _do_ioc_sigma():
            rules = generate_sigma_rules_for_analysis(analysis_data, article_url=source_url)
            return rules, sigma_rules_to_yaml(rules)

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_yara = executor.submit(_do_yara)
            future_mitre = executor.submit(_do_mitre)
            future_ioc_sigma = executor.submit(_do_ioc_sigma)

            try:
                yara_rules = future_yara.result(timeout=120)
                yield sse("yara_done", 62, f"Generated {len(yara_rules)} YARA rules")
            except Exception as e:
                yield sse("yara_done", 62, "YARA generation failed")

            try:
                mitre_techniques, mitre_tags, tactic_summary = future_mitre.result(timeout=120)
                yield sse("mitre_done", 68, f"Mapped {len(mitre_techniques)} MITRE techniques", {
                    "mitre_mapping": {"techniques": mitre_techniques, "tactic_summary": tactic_summary, "tags": mitre_tags}
                })
            except Exception as e:
                yield sse("mitre_done", 68, "MITRE mapping failed")

            try:
                ioc_sigma_rules, ioc_sigma_yaml = future_ioc_sigma.result(timeout=120)
                yield sse("sigma_done", 75, f"Generated {len(ioc_sigma_rules)} Sigma rules")
            except Exception as e:
                yield sse("sigma_done", 75, "Sigma generation failed")

        # Global Sigma match
        yield sse("sigma_match", 76, "Matching global Sigma rules with MITRE data...")
        try:
            sigma_rules_directory = os.path.join(parent_dir, "Global_Sigma_Rules")
            if os.path.exists(sigma_rules_directory):
                all_sigma_rules = load_sigma_rules_local(sigma_rules_directory)
                sigma_matches = match_sigma_rules_with_report(
                    sigma_rules=all_sigma_rules,
                    analysis_data=analysis_data,
                    report_text=combined_text.lower(),
                    root_directory=sigma_rules_directory,
                    mitre_techniques=mitre_techniques,
                    threshold=25.0,
                    max_results=15,
                )
            yield sse("sigma_match_done", 80, f"Matched {len(sigma_matches)} global Sigma rules", {"sigma_matches": sigma_matches})
        except Exception as e:
            yield sse("sigma_match_done", 80, "Sigma matching failed")

        # Stage 4: SIEM queries
        yield sse("siem", 82, "Generating SIEM queries...")
        siem_queries = {
            "splunk": {"description": "", "query": "", "notes": ""},
            "qradar": {"description": "", "query": "", "notes": ""},
            "elastic": {"description": "", "query": "", "notes": ""},
            "sentinel": {"description": "", "query": "", "notes": ""},
        }
        
        def _do_siem_structured(): return siem_queries_to_flat(generate_siem_queries(analysis_data))
        def _do_siem_ai():
            if not more_sigma_rules: return None
            return convert_sigma_to_siem_queries(
                sigma_rules=more_sigma_rules, openai_api_key=openai_api_key, provider_name=provider_name, model_name=model_name
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_siem_struct = executor.submit(_do_siem_structured)
            future_siem_ai = executor.submit(_do_siem_ai)

            try:
                siem_queries = future_siem_struct.result(timeout=120)
                yield sse("siem_structured_done", 88, "IoC-based SIEM queries ready")
            except Exception as e:
                logger.error(f"SIEM structured error: {e}")

            try:
                ai_siem = future_siem_ai.result(timeout=300)
                if isinstance(ai_siem, dict):
                    for platform in ("splunk", "qradar", "elastic", "sentinel"):
                        if platform in ai_siem and platform in siem_queries:
                            existing = siem_queries[platform].get("query", "")
                            ai_query = ai_siem[platform].get("query", "")
                            if ai_query and ai_query != "N/A":
                                siem_queries[platform]["query"] = existing + "\n\n/* AI-Refined */\n" + ai_query
                                siem_queries[platform]["notes"] = "Includes both IoC-based and AI-refined queries"
                yield sse("siem_ai_done", 93, "AI-refined SIEM queries ready")
            except Exception as e:
                logger.error(f"SIEM AI error: {e}")

        all_sigma_yaml = ioc_sigma_yaml
        if more_sigma_rules:
            all_sigma_yaml = (all_sigma_yaml + "\n---\n" + more_sigma_rules) if all_sigma_yaml else more_sigma_rules

        # Stage 5: Atomic Red Team
        atomic_tests = []
        if all_sigma_yaml and len(all_sigma_yaml.strip()) > 20:
            yield sse("atomic_tests", 93, "Generating Atomic Red Team test scenarios...")
            try:
                atomic_tests = generate_atomic_tests_from_sigma(
                    sigma_rules=all_sigma_yaml, threat_context=threat_summary, openai_api_key=openai_api_key, provider_name=provider_name, model_name=model_name
                )
                yield sse("atomic_tests_done", 97, f"Generated {len(atomic_tests)} atomic test scenarios", {"atomic_tests": atomic_tests})
            except Exception as e:
                yield sse("atomic_tests_done", 97, "Atomic test generation failed")

        # Finalizing
        yield sse("finalizing", 98, "Compiling final report...")
        response = {
            "threat_summary": threat_summary,
            "analysis_data": {
                "indicators_of_compromise": analysis_data.get("indicators_of_compromise", {}),
                "ttps": analysis_data.get("ttps", []),
                "threat_actors": analysis_data.get("threat_actors", []),
                "tools_or_malware": analysis_data.get("tools_or_malware", [])
            },
            "mitre_mapping": {"techniques": mitre_techniques, "tactic_summary": tactic_summary, "tags": mitre_tags},
            "yara_rules": yara_rules,
            "ioc_sigma_rules": ioc_sigma_rules,
            "generated_sigma_rules": all_sigma_yaml,
            "siem_queries": siem_queries,
            "atomic_tests": atomic_tests,
            "sigma_matches": sigma_matches,
        }
        
        response = sanitize_for_json(response)
        
        try:
            report_data = {
                "id": str(uuid.uuid4()),
                "url": source_url,
                "timestamp": datetime.now().isoformat(),
                "provider": provider_name,
                "model": model_name,
                **response
            }
            ReportRepository.create(report_data)
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            
        yield sse("complete", 100, "Analysis complete!", response)
    
    except Exception as e:
        logger.error(f"Stream analysis error: {e}")
        logger.error(traceback.format_exc())
        yield sse("error", 0, str(e))
