"""
PERSEPTOR v2.0 - AI Engine
Multi-provider threat analysis with CoT prompting, output validation, and caching.
"""

import json
import logging
import os
import re
from typing import Optional
from modules.ai.base_provider import AIProvider, Message
from modules.ai.provider_factory import get_provider
from modules.ai.retry_handler import with_retry
from modules.prompts.templates import PromptTemplates
from modules.prompts.few_shot import FewShotExamples
from modules.pipeline.output_validator import OutputValidator
from modules.pipeline.cache import get_cache, ResponseCache
from modules.logging_config import get_logger

logger = get_logger("ai_engine")


################################################################################
# Token Usage Tracking
################################################################################

def _track_usage(response, endpoint: str = "unknown"):
    """Record AI token usage to the database for the Usage dashboard."""
    try:
        from modules.database import TokenUsageRepository
        if response and hasattr(response, 'usage') and response.usage:
            TokenUsageRepository.record({
                "session_id": None,  # will be enriched if session context available
                "provider": getattr(response, 'provider', 'unknown'),
                "model": getattr(response, 'model', 'unknown'),
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "endpoint": endpoint,
                "latency_ms": getattr(response, 'latency_ms', 0),
            })
    except Exception as e:
        logger.debug(f"Token usage tracking failed (non-critical): {e}")


################################################################################
# Utility Functions
################################################################################

def safe_json_parse(json_str: str) -> dict:
    """Safely parse a JSON string, returning a dictionary or empty {} on error."""
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.warning(f"JSON parse error: {e}")
        return {}


def extract_json_from_response(text: str) -> str:
    """Extract JSON from an AI response that may contain markdown code blocks."""
    text = text.strip()
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
        return text[start:].strip()
    if "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
        return text[start:].strip()
    json_start = text.find("{")
    json_end = text.rfind("}") + 1
    if json_start != -1 and json_end > json_start:
        return text[json_start:json_end]
    return text


################################################################################
# Provider Resolution (backward compatibility)
################################################################################

def _resolve_provider(
    provider: Optional[AIProvider] = None,
    openai_api_key: str = "",
    provider_name: str = "openai",
    model_name: Optional[str] = None,
) -> AIProvider:
    """Resolve an AIProvider from various input patterns."""
    if provider is not None:
        return provider

    if openai_api_key:
        if openai_api_key.startswith("sk-ant-"):
            provider_name = "anthropic"
        elif openai_api_key.startswith("AIza"):
            provider_name = "google"
        else:
            provider_name = "openai"

    return get_provider(
        provider_name=provider_name,
        api_key=openai_api_key,
        model=model_name,
    )


################################################################################
# Summarize Threat Report (CoT)
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def summarize_threat_report(
    text: str,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
) -> str:
    """Summarize threat report using Chain-of-Thought prompting."""
    try:
        cache = get_cache()
        cache_key = ResponseCache._make_key("summarize", text[:500], provider_name, model_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("Returning cached threat summary")
            return cached

        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        messages = [
            Message(role="system", content=PromptTemplates.THREAT_ANALYST_SYSTEM),
            Message(role="user", content=PromptTemplates.THREAT_SUMMARY_COT.format(text=text)),
        ]

        logger.info(f"Generating threat summary using {ai.provider_name}")
        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "summarize_threat_report")
        result = response.content.strip()

        cache.set(cache_key, result)
        logger.info(
            f"Threat summary generated",
            extra={"provider": ai.provider_name, "model": response.model, "tokens": response.usage.total_tokens},
        )
        return result

    except Exception as e:
        logger.error(f"Error summarizing threat report: {e}", exc_info=True)
        return "Could not generate threat summary."


################################################################################
# Extract IoCs and TTPs (CoT + Few-Shot + Validation)
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def extract_iocs_ttps_gpt(
    text: str,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
):
    """Extract IoCs and TTPs with CoT prompting and output validation."""
    try:
        cache = get_cache()
        cache_key = ResponseCache._make_key("ioc_extract", text[:500], provider_name, model_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("Returning cached IoC extraction")
            return cached

        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        messages = [
            Message(role="system", content=PromptTemplates.IOC_EXTRACTOR_SYSTEM),
            # Few-shot example
            Message(role="user", content="Extract IoCs from: 'APT29 used SUNBURST backdoor via trojanized SolarWinds update, C2 at avsvmcloud.com'"),
            Message(role="assistant", content=FewShotExamples.IOC_EXTRACTION_EXAMPLE),
            # Actual request with CoT
            Message(role="user", content=PromptTemplates.IOC_EXTRACTION_COT.format(text=text)),
        ]

        logger.info(f"Extracting IoCs/TTPs using {ai.provider_name}")
        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "extract_iocs_ttps")

        raw_content = response.content
        logger.info(f"IoC raw response length: {len(raw_content)}, first 500: {raw_content[:500]}")

        # Dump raw response only when DEBUG logging is enabled
        if logger.isEnabledFor(logging.DEBUG):
            try:
                debug_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "ioc_raw_response.txt")
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(raw_content)
                logger.debug(f"Raw IoC response dumped to {debug_path} ({len(raw_content)} bytes)")
            except Exception as dump_err:
                logger.debug(f"Failed to dump raw response: {dump_err}")

        # Extract JSON from response (handles thinking blocks, markdown, etc.)
        cleaned = extract_json_from_response(raw_content)

        # Validate and repair output
        parsed_ok = False
        is_valid, parsed = OutputValidator.validate_json(cleaned)
        if is_valid and isinstance(parsed, dict):
            _, validated, warnings = OutputValidator.validate_ioc_response(parsed)
            if warnings:
                logger.warning(f"IoC validation warnings: {warnings}")
            result = json.dumps(validated)
            parsed_ok = True
        else:
            # Second attempt: try the full raw content directly
            is_valid2, parsed2 = OutputValidator.validate_json(raw_content)
            if is_valid2 and isinstance(parsed2, dict):
                _, validated2, warnings2 = OutputValidator.validate_ioc_response(parsed2)
                result = json.dumps(validated2)
                parsed_ok = True
                logger.info("IoC extraction: second-pass JSON parse succeeded")
            else:
                logger.warning(f"IoC extraction returned invalid JSON. Cleaned first 300: {cleaned[:300]}")
                result = "{}"  # Return empty JSON, not raw text

        # Only cache successfully parsed results
        if parsed_ok:
            cache.set(cache_key, result)
        logger.info(
            f"IoC/TTP extraction complete",
            extra={"provider": ai.provider_name, "model": response.model, "tokens": response.usage.total_tokens},
        )
        return result

    except Exception as e:
        logger.error(f"Error in IoC/TTP extraction: {e}", exc_info=True)
        return "{}"


################################################################################
# Refine Sigma Queries
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def refine_sigma_queries_with_gpt(
    sigma_yaml: str,
    splunk_queries: list,
    qradar_queries: list,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "medium",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
):
    """Refine Sigma rules and SIEM queries."""
    try:
        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)
        splunk_str = "\n".join(splunk_queries) if splunk_queries else "(No Splunk Queries)"
        qradar_str = "\n".join(qradar_queries) if qradar_queries else "(No QRadar Queries)"

        messages = [
            Message(role="system", content=PromptTemplates.SIEM_SPECIALIST_SYSTEM),
            Message(role="user", content=f"""Review and refine the following detection rules and queries.

REFINEMENT GOALS:
1. Fix any syntax errors in the Sigma rule
2. Optimize Splunk queries for search performance
3. Ensure QRadar AQL uses correct property names
4. Add missing detection fields or conditions
5. Reduce false positive potential

Output in plain text with these sections:
1) Refined Sigma Rule (valid YAML)
2) Refined Splunk Queries (valid SPL)
3) Refined QRadar Queries (valid AQL)

Sigma YAML:
{sigma_yaml}

Splunk queries:
{splunk_str}

QRadar queries:
{qradar_str}"""),
        ]

        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "mitre_mapping")
        return response.content.strip()

    except Exception as e:
        logger.error(f"Error refining queries: {e}", exc_info=True)
        return "Error refining output."


################################################################################
# Generate Sigma Rules (CoT + Few-Shot)
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def generate_more_sigma_rules_from_article(
    article_text: str,
    images_ocr_text: str,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
) -> str:
    """Generate Sigma rules with CoT prompting and few-shot examples."""
    try:
        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        messages = [
            Message(role="system", content=PromptTemplates.DETECTION_ENGINEER_SYSTEM),
            # Few-shot example
            Message(role="user", content="Generate a Sigma rule for PowerShell download-and-execute behavior"),
            Message(role="assistant", content=FewShotExamples.SIGMA_RULE_EXAMPLE),
            # Actual request with CoT
            Message(role="user", content=PromptTemplates.SIGMA_GENERATION_COT.format(
                article_text=article_text,
                images_ocr_text=images_ocr_text,
            )),
        ]

        logger.info(f"Generating Sigma rules from article using {ai.provider_name}")
        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "generate_sigma_rules")
        result = response.content.strip()

        # Validate Sigma output
        is_valid, warnings = OutputValidator.validate_sigma_yaml(result)
        if warnings:
            logger.warning(f"Sigma validation warnings: {warnings}")

        return result

    except Exception as e:
        logger.error(f"Error generating Sigma rules: {e}", exc_info=True)
        return "Error generating extra Sigma rules."


################################################################################
# Convert Sigma to SIEM Queries (CoT + Few-Shot + Validation)
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def convert_sigma_to_siem_queries(
    sigma_rules: str,
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
) -> dict:
    """Convert Sigma rules to SIEM queries with validation."""
    try:
        cache = get_cache()
        cache_key = ResponseCache._make_key("siem_convert", sigma_rules[:500], provider_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("Returning cached SIEM queries")
            return cached

        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        messages = [
            Message(role="system", content=PromptTemplates.SIEM_SPECIALIST_SYSTEM),
            # Few-shot example
            Message(role="user", content="Convert this Sigma rule to SIEM queries: PowerShell download and execute detection"),
            Message(role="assistant", content=FewShotExamples.SIEM_QUERY_EXAMPLE),
            # Actual request with CoT
            Message(role="user", content=PromptTemplates.SIEM_CONVERSION_COT.format(sigma_rules=sigma_rules)),
        ]

        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "convert_siem_queries")

        # Validate and repair output
        is_valid, parsed = OutputValidator.validate_json(response.content)
        if is_valid and isinstance(parsed, dict):
            _, validated, warnings = OutputValidator.validate_siem_response(parsed)
            if warnings:
                logger.warning(f"SIEM validation warnings: {warnings}")
            siem_queries = validated
        else:
            logger.warning("SIEM conversion returned invalid JSON, using fallback")
            siem_queries = create_fallback_siem_queries(sigma_rules)

        cache.set(cache_key, siem_queries)
        logger.info(
            f"SIEM query conversion complete",
            extra={"provider": ai.provider_name, "model": response.model},
        )
        return siem_queries

    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error in SIEM conversion: {e}")
        return create_fallback_siem_queries(sigma_rules)
    except Exception as e:
        logger.error(f"Error converting Sigma to SIEM: {e}", exc_info=True)
        return create_fallback_siem_queries(sigma_rules)


################################################################################
# Generate Atomic Red Team Test Scenarios
################################################################################

@with_retry(max_retries=2, base_delay=2.0)
def generate_atomic_tests_from_sigma(
    sigma_rules: str,
    threat_context: str = "",
    openai_api_key: str = "",
    model_name: str = None,
    reasoning_effort: str = "high",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
) -> list:
    """Generate Atomic Red Team test scenarios for each Sigma rule."""
    try:
        cache = get_cache()
        cache_key = ResponseCache._make_key("atomic_tests", sigma_rules[:500], provider_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("Returning cached atomic tests")
            return cached

        ai = _resolve_provider(provider, openai_api_key, provider_name, model_name)

        # Build threat context summary (truncate to avoid token overflow)
        ctx = threat_context[:3000] if threat_context else "No additional threat context available."

        messages = [
            Message(role="system", content=PromptTemplates.ATOMIC_TEST_ENGINEER_SYSTEM),
            # Few-shot example
            Message(role="user", content="Generate an atomic test scenario for a Sigma rule detecting PowerShell download and execute behavior"),
            Message(role="assistant", content=FewShotExamples.ATOMIC_TEST_EXAMPLE),
            # Actual request with CoT
            Message(role="user", content=PromptTemplates.ATOMIC_TEST_GENERATION_COT.format(
                sigma_rules=sigma_rules,
                threat_context=ctx,
            )),
        ]

        logger.info(f"Generating atomic test scenarios using {ai.provider_name}")
        response = ai.generate(messages, temperature=0.1)
        _track_usage(response, "generate_atomic_tests")

        # Parse JSON array from response
        raw_content = response.content
        cleaned = extract_json_from_response(raw_content)

        # Try to parse as JSON array
        is_valid, parsed = OutputValidator.validate_json(cleaned)
        if is_valid and isinstance(parsed, list):
            cache.set(cache_key, parsed)
            logger.info(f"Generated {len(parsed)} atomic test scenarios")
            return parsed

        # Fallback: try wrapping in array
        if is_valid and isinstance(parsed, dict):
            result = [parsed]
            cache.set(cache_key, result)
            logger.info("Generated 1 atomic test scenario (wrapped)")
            return result

        # Second attempt on raw content
        is_valid2, parsed2 = OutputValidator.validate_json(raw_content)
        if is_valid2 and isinstance(parsed2, list):
            cache.set(cache_key, parsed2)
            return parsed2

        # Handle "Extra data" — AI returned multiple JSON objects/arrays concatenated
        # Try to find and parse the first complete JSON array [...] in the response
        import re as _re
        bracket_start = cleaned.find('[')
        if bracket_start >= 0:
            depth = 0
            for ci in range(bracket_start, len(cleaned)):
                if cleaned[ci] == '[':
                    depth += 1
                elif cleaned[ci] == ']':
                    depth -= 1
                    if depth == 0:
                        candidate = cleaned[bracket_start:ci+1]
                        try:
                            result = json.loads(candidate)
                            if isinstance(result, list):
                                cache.set(cache_key, result)
                                logger.info(f"Generated {len(result)} atomic tests (bracket extraction)")
                                return result
                        except json.JSONDecodeError:
                            pass
                        break

        # Try fixing common JSON issues: trailing commas, etc.
        try:
            fixed = _re.sub(r',\s*([}\]])', r'\1', cleaned)
            result = json.loads(fixed)
            if isinstance(result, list):
                cache.set(cache_key, result)
                logger.info(f"Generated {len(result)} atomic tests (fixed JSON)")
                return result
        except json.JSONDecodeError:
            pass

        logger.warning(f"Atomic test generation returned invalid JSON. First 300 chars: {cleaned[:300]}")
        return []

    except Exception as e:
        logger.error(f"Error generating atomic tests: {e}", exc_info=True)
        return []


def create_fallback_siem_queries(sigma_rules: str) -> dict:
    """Create basic SIEM queries as fallback when AI conversion fails."""
    try:
        rules_text = sigma_rules.lower()

        splunk_query = "index=* "
        if "process" in rules_text:
            splunk_query += '| search ProcessName=* '
        if "command" in rules_text:
            splunk_query += '| search CommandLine=* '
        if "file" in rules_text:
            splunk_query += '| search FileName=* '

        qradar_query = "SELECT * FROM events WHERE "
        conditions = []
        if "process" in rules_text:
            conditions.append("processname IS NOT NULL")
        if "command" in rules_text:
            conditions.append("commandline IS NOT NULL")
        qradar_query += " AND ".join(conditions) if conditions else "1=1"

        elastic_query = {"query": {"bool": {"must": []}}}
        if "process" in rules_text:
            elastic_query["query"]["bool"]["must"].append({"exists": {"field": "process.name"}})
        if "command" in rules_text:
            elastic_query["query"]["bool"]["must"].append({"exists": {"field": "process.command_line"}})

        sentinel_query = "SecurityEvent | where "
        s_conditions = []
        if "process" in rules_text:
            s_conditions.append('ProcessName contains ""')
        if "command" in rules_text:
            s_conditions.append('CommandLine contains ""')
        sentinel_query += " and ".join(s_conditions) if s_conditions else "1=1"

        fallback_note = "Basic fallback query. Please customize for your environment."
        return {
            "splunk": {"description": "Splunk SPL (fallback)", "query": splunk_query, "notes": fallback_note},
            "qradar": {"description": "QRadar AQL (fallback)", "query": qradar_query, "notes": fallback_note},
            "elastic": {"description": "Elasticsearch (fallback)", "query": str(elastic_query).replace("'", '"'), "notes": fallback_note},
            "sentinel": {"description": "Sentinel KQL (fallback)", "query": sentinel_query, "notes": fallback_note},
        }
    except Exception as e:
        logger.error(f"Error creating fallback SIEM queries: {e}")
        err_entry = {"description": "Error", "query": "Error", "notes": str(e)}
        return {"splunk": err_entry, "qradar": err_entry, "elastic": err_entry, "sentinel": err_entry}
