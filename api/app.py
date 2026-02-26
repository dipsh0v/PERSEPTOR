from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import traceback

# Import PERSEPTOR modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# PERSEPTOR v2.0 - Config and Logging
from modules.config import config
from modules.logging_config import (
    setup_logging,
    get_logger,
    create_flask_request_logger,
)

# Initialize structured logging
setup_logging(
    level=config.logging.level,
    log_format=config.logging.format,
    file_path=config.logging.file_path,
)
logger = get_logger("api")

from modules.quality_analyzer import create_qa_system
from modules.ai_engine import (
    summarize_threat_report,
    extract_iocs_ttps_gpt,
    safe_json_parse,
    generate_more_sigma_rules_from_article,
    convert_sigma_to_siem_queries,
    generate_atomic_tests_from_sigma,
)
from modules.content_fetcher import (
    get_dynamic_image_urls,
    extract_image_urls_static,
    extract_text_from_images,
    fetch_page_content
)

# ─── Smart URL Fetcher ────────────────────────────────────────────────────────

_FETCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

def _smart_fetch_url(url: str) -> tuple:
    """
    Fetch URL content with fallback strategy:
    1. requests + BeautifulSoup with proper headers
    2. If text is too short (<200 chars) or HTTP fails, use Playwright for JS-rendered pages
    Returns (text_content, soup, used_playwright)
    """
    soup = None
    text_content = ""
    http_failed = False

    # Step 1: Try standard HTTP fetch with proper headers
    try:
        session = requests.Session()
        session.headers.update(_FETCH_HEADERS)
        resp = session.get(url, timeout=30, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
    except requests.exceptions.RequestException as e:
        # Retry once with SSL verification disabled (some sites have cert issues)
        logger.warning(f"HTTP fetch failed for {url}: {e} — retrying with verify=False")
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            resp = requests.get(url, timeout=30, headers=_FETCH_HEADERS,
                                allow_redirects=True, verify=False)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")
        except requests.exceptions.RequestException as e2:
            logger.warning(f"HTTP retry also failed for {url}: {e2} — will try Playwright")
            http_failed = True

    if soup is None:
        soup = BeautifulSoup("", "html.parser")

    # Remove script/style/nav/footer noise before extracting text
    if not http_failed:
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
            tag.decompose()

    import re as _re

    # Try multiple strategies to find the main content area (best match wins)
    best_text = ""

    # Strategy 1: Common article body class names
    _content_classes = [
        "articlebody", "article-body", "article-content",
        "entry-content", "post-body", "post-content",
        "story-body", "content-body", "blog-content",
        "article__body", "articleBody",
    ]
    for cls_name in _content_classes:
        el = soup.find(class_=lambda x: x and cls_name in str(x).lower())
        if el:
            candidate = el.get_text(separator="\n", strip=True)
            if len(candidate) > len(best_text):
                best_text = candidate

    # Strategy 2: <article> or <main> tags
    if len(best_text) < 200:
        for tag_name in ["article", "main"]:
            el = soup.find(tag_name)
            if el:
                candidate = el.get_text(separator="\n", strip=True)
                if len(candidate) > len(best_text):
                    best_text = candidate

    # Strategy 3: Largest <div> with significant text (heuristic)
    if len(best_text) < 200:
        for div in soup.find_all("div"):
            div_text = div.get_text(separator="\n", strip=True)
            if len(div_text) > len(best_text) and len(div_text) > 300:
                # Avoid huge wrapper divs — check text density
                html_len = len(str(div))
                if html_len > 0 and len(div_text) / html_len > 0.15:
                    best_text = div_text

    # Strategy 4: Full page text as last resort
    if len(best_text) < 200:
        best_text = soup.get_text(separator="\n", strip=True)

    text_content = _re.sub(r'\n{3,}', '\n\n', best_text).strip()

    # Step 2: If HTTP failed or text is too short, try Playwright for JS-rendered content
    if http_failed or len(text_content) < 200:
        reason = "HTTP failed" if http_failed else f"only {len(text_content)} chars"
        logger.info(f"Static fetch insufficient ({reason}), trying Playwright...")
        try:
            pw_result = fetch_page_content(url, wait_time=12)
            pw_text = pw_result.get("text", "")
            if len(pw_text) > len(text_content):
                logger.info(f"Playwright got {len(pw_text)} chars (vs {len(text_content)} static)")
                text_content = pw_text
                return text_content, soup, True
        except Exception as e:
            logger.warning(f"Playwright fallback failed: {e}")

    return text_content, soup, False
from modules.yara_generator import generate_yara_rules, yara_rules_to_text
from modules.sigma_generator import (
    generate_sigma_rules_for_analysis,
    sigma_rules_to_yaml,
    generate_sigma_rules_for_commands,
)
from modules.siem_query_generator import generate_siem_queries, siem_queries_to_flat
from modules.mitre_mapping import map_iocs_to_mitre, get_mitre_tags, get_tactic_summary
from modules.sigma_matcher import (
    load_sigma_rules_local,
    match_sigma_rules_with_report
)
from modules.ai.provider_factory import get_provider, get_available_providers
from modules.database import init_db, ReportRepository, RuleRepository, TokenUsageRepository
from modules.session_manager import session_manager
from modules.middleware import rate_limit, validate_json_content_type
from modules.security import (
    validate_url,
    validate_api_key,
    validate_prompt,
    sanitize_for_json,
    apply_security_headers,
)
import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

app = Flask(__name__)

# CORS with configurable origins
CORS(app, resources={r"/api/*": {"origins": config.security.cors_origins}}, supports_credentials=True)

# Request/response logging middleware
create_flask_request_logger(app)

# Security headers on all responses
@app.after_request
def add_security_headers(response):
    return apply_security_headers(response)

# Initialize database
init_db()
logger.info("Database initialized")

# Initialize QA system
qa_system = None

def get_qa_system(openai_api_key="", provider_name="openai", model_name=None):
    """Get or create QA system with multi-provider support."""
    global qa_system
    # Always recreate if provider changed
    qa_system = create_qa_system(
        openai_api_key=openai_api_key,
        model_name=model_name or config.default_model,
        provider_name=provider_name,
    )
    return qa_system


def _extract_provider_params(data):
    """
    Extract provider parameters from request data OR session token.
    Priority: session token > request body > defaults.
    """
    api_key = ''
    provider_name = data.get('provider', 'openai')
    model_name = data.get('model', None)

    # 1) Try session token first (from X-Session-Token header)
    session_token = request.headers.get('X-Session-Token')
    if session_token:
        session_data = session_manager.validate_session(session_token)
        if session_data:
            api_key = session_data['api_key']
            # Session provider/model override request body if not explicitly set
            if not data.get('provider'):
                provider_name = session_data.get('provider', 'openai')
            if not data.get('model') and session_data.get('model_preference'):
                model_name = session_data['model_preference']
            logger.info(f"API key resolved from session token (provider: {provider_name})")
        else:
            logger.warning("Invalid or expired session token provided")

    # 2) Fallback to request body
    if not api_key:
        api_key = data.get('api_key') or data.get('openai_api_key', '')

    # Auto-detect provider from key prefix if not specified
    if provider_name == 'openai' and api_key:
        if api_key.startswith('sk-ant-'):
            provider_name = 'anthropic'
        elif api_key.startswith('AIza'):
            provider_name = 'google'

    return api_key, provider_name, model_name

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_url():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        # CORS already handled by Flask-CORS, but add headers for OPTIONS
        return response
    
    try:
        data = request.json
        if not data:
            raise ValueError("No JSON data received")
            
        url = data.get('url')
        if not url:
            raise ValueError("URL is required")

        # Validate URL (SSRF protection)
        url_valid, url_error = validate_url(url)
        if not url_valid:
            return jsonify({"error": url_error}), 400

        # Multi-provider support (backward compatible)
        api_key, provider_name, model_name = _extract_provider_params(data)
        if not api_key:
            raise ValueError("API key is required (api_key or openai_api_key)")

        # Validate API key format
        key_valid, key_error = validate_api_key(api_key)
        if not key_valid:
            return jsonify({"error": key_error}), 400

        # Keep backward compat variable name for downstream calls
        openai_api_key = api_key

        logger.info(f"Starting analysis for URL: {url} (provider: {provider_name})")

        # Fetch content from URL with smart fallback
        try:
            text_content, soup, used_pw = _smart_fetch_url(url)
            logger.info(f"Extracted {len(text_content)} chars from URL (playwright={used_pw})")
        except Exception as e:
            logger.error(f"Error fetching URL: {str(e)}")
            raise ValueError(f"Error fetching URL: {str(e)}")

        # Collect images
        try:
            static_imgs = extract_image_urls_static(soup, url)
            dynamic_imgs = get_dynamic_image_urls(url)
            all_imgs = list(set(static_imgs + dynamic_imgs))
        except Exception as e:
            logger.error(f"Error extracting images: {str(e)}")
            all_imgs = []

        # OCR processing
        try:
            images_ocr_text = extract_text_from_images(all_imgs)
            combined_text = text_content + "\n\n[IMAGE_OCR_SECTION]\n" + images_ocr_text
        except Exception as e:
            logger.error(f"Error in OCR processing: {str(e)}")
            images_ocr_text = ""
            combined_text = text_content

        # Validate extracted text
        if not combined_text or len(combined_text.strip()) < 50:
            raise ValueError(
                f"Could not extract sufficient text from URL ({len(combined_text.strip())} chars). "
                "The page may require JavaScript rendering or may be blocking automated access."
            )

        # Threat summary
        try:
            threat_summary = summarize_threat_report(
                text=combined_text,
                openai_api_key=openai_api_key,
                provider_name=provider_name,
                model_name=model_name,
            )
        except Exception as e:
            logger.error(f"Error generating threat summary: {str(e)}")
            threat_summary = "Error generating threat summary"

        # IOC and TTP analysis (with JSON repair for AI quirks)
        try:
            from modules.pipeline.output_validator import OutputValidator as OV

            gpt_json_str = extract_iocs_ttps_gpt(
                combined_text,
                openai_api_key=openai_api_key,
                provider_name=provider_name,
                model_name=model_name,
            )
            # Use OutputValidator with repair (handles \escape, truncation, etc.)
            is_valid, parsed = OV.validate_json(gpt_json_str)
            if is_valid and isinstance(parsed, dict):
                analysis_data = parsed
                ioc_count = sum(
                    len(v) for v in parsed.get("indicators_of_compromise", {}).values()
                    if isinstance(v, list)
                )
                logger.info(f"IoC analysis parsed OK: {ioc_count} total indicators")
            else:
                logger.warning(f"IoC analysis JSON repair failed, raw length: {len(gpt_json_str)}")
                analysis_data = safe_json_parse(gpt_json_str)
        except Exception as e:
            logger.error(f"Error in IOC/TTP analysis: {str(e)}")
            analysis_data = {"error": "Error in IOC/TTP analysis"}

        # YARA rules (structured output)
        try:
            yara_rules = generate_yara_rules(analysis_data)
        except Exception as e:
            logger.error(f"Error generating YARA rules: {str(e)}")
            yara_rules = []

        # MITRE ATT&CK Mapping
        try:
            mitre_techniques = map_iocs_to_mitre(analysis_data)
            mitre_tags = get_mitre_tags(mitre_techniques)
            tactic_summary = get_tactic_summary(mitre_techniques)
        except Exception as e:
            logger.error(f"Error in MITRE mapping: {str(e)}")
            mitre_techniques = []
            mitre_tags = []
            tactic_summary = {}

        # IoC-based Sigma rules (structured, from analysis data)
        try:
            ioc_sigma_rules = generate_sigma_rules_for_analysis(
                analysis_data, article_url=url
            )
            ioc_sigma_yaml = sigma_rules_to_yaml(ioc_sigma_rules)
        except Exception as e:
            logger.error(f"Error generating IoC Sigma rules: {str(e)}")
            ioc_sigma_rules = []
            ioc_sigma_yaml = ""

        # AI-generated Sigma rules (from article text via AI)
        try:
            more_sigma_rules = generate_more_sigma_rules_from_article(
                article_text=text_content,
                images_ocr_text=images_ocr_text,
                openai_api_key=openai_api_key,
                provider_name=provider_name,
                model_name=model_name,
            )

            if more_sigma_rules and not more_sigma_rules.startswith("Error"):
                rules = []
                current_rule = []
                for line in more_sigma_rules.split('\n'):
                    if line.strip().startswith('title:'):
                        if current_rule:
                            rules.append('\n'.join(current_rule))
                        current_rule = [line]
                    elif not any(skip in line for skip in [
                        '–––––––', 'These rules can be further tuned',
                        'Below are two Sigma rules', 'This rule detects',
                        'This query searches'
                    ]):
                        if current_rule or line.strip():
                            current_rule.append(line)
                if current_rule:
                    rules.append('\n'.join(current_rule))
                more_sigma_rules = '\n\n'.join(rules)
            else:
                more_sigma_rules = ""
        except Exception as e:
            logger.error(f"Error generating AI Sigma rules: {str(e)}")
            more_sigma_rules = ""

        # Combine all Sigma rules
        all_sigma_yaml = ioc_sigma_yaml
        if more_sigma_rules:
            all_sigma_yaml = all_sigma_yaml + "\n---\n" + more_sigma_rules if all_sigma_yaml else more_sigma_rules

        # SIEM Queries (structured, from IoC data directly)
        try:
            siem_structured = generate_siem_queries(analysis_data)
            siem_queries = siem_queries_to_flat(siem_structured)
        except Exception as e:
            logger.error(f"Error generating SIEM queries: {str(e)}")
            siem_queries = {
                "splunk": {"description": "Error", "query": "Error", "notes": str(e)},
                "qradar": {"description": "Error", "query": "Error", "notes": str(e)},
                "elastic": {"description": "Error", "query": "Error", "notes": str(e)},
                "sentinel": {"description": "Error", "query": "Error", "notes": str(e)},
            }

        # AI-refined SIEM queries (if AI-generated Sigma rules exist)
        try:
            if more_sigma_rules:
                ai_siem = convert_sigma_to_siem_queries(
                    sigma_rules=more_sigma_rules,
                    openai_api_key=openai_api_key,
                    provider_name=provider_name,
                    model_name=model_name,
                )
                if isinstance(ai_siem, dict):
                    for platform in ("splunk", "qradar", "elastic", "sentinel"):
                        if platform in ai_siem and platform in siem_queries:
                            existing = siem_queries[platform].get("query", "")
                            ai_query = ai_siem[platform].get("query", "")
                            if ai_query and ai_query != "N/A":
                                siem_queries[platform]["query"] = existing + "\n\n/* AI-Refined */\n" + ai_query
                                siem_queries[platform]["notes"] = "Includes both IoC-based and AI-refined queries"
        except Exception as e:
            logger.error(f"Error in AI SIEM refinement: {str(e)}")

        # Atomic Red Team test scenarios
        atomic_tests = []
        try:
            if all_sigma_yaml and len(all_sigma_yaml.strip()) > 20:
                atomic_tests = generate_atomic_tests_from_sigma(
                    sigma_rules=all_sigma_yaml,
                    threat_context=threat_summary,
                    openai_api_key=openai_api_key,
                    provider_name=provider_name,
                    model_name=model_name,
                )
                logger.info(f"Generated {len(atomic_tests)} atomic test scenarios")
        except Exception as e:
            logger.error(f"Error generating atomic tests: {str(e)}")
            atomic_tests = []

        # Global Sigma matching
        try:
            # Use Global_Sigma_Rules directory within the project
            sigma_rules_directory = os.path.join(parent_dir, "Global_Sigma_Rules")
            
            if os.path.exists(sigma_rules_directory):
                logger.info(f"Loading Sigma rules from: {sigma_rules_directory}")
                sigma_rules = load_sigma_rules_local(sigma_rules_directory)
                logger.info(f"Loaded {len(sigma_rules)} Sigma rules")
                sigma_matches = match_sigma_rules_with_report(
                    sigma_rules=sigma_rules,
                    analysis_data=analysis_data,
                    report_text=combined_text.lower(),
                    root_directory=sigma_rules_directory,
                    mitre_techniques=mitre_techniques if 'mitre_techniques' in dir() else None,
                    threshold=25.0,
                    max_results=15,
                )
                logger.info(f"Found {len(sigma_matches)} Sigma matches")
            else:
                logger.warning(f"Sigma rules directory not found: {sigma_rules_directory}")
                sigma_matches = []
        except Exception as e:
            logger.error(f"Error in Sigma matching: {str(e)}")
            logger.error(traceback.format_exc())
            sigma_matches = []

        # Create response
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

        # Sanitize output
        response = sanitize_for_json(response)

        # Save report to database
        report_data = {
            'id': str(uuid.uuid4()),
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'provider': provider_name,
            'model': model_name,
            **response
        }
        ReportRepository.create(report_data)
        logger.info(f"Saved report with ID: {report_data['id']}")

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in analyze_url: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/api/analyze/stream', methods=['POST', 'OPTIONS'])
def analyze_url_stream():
    """SSE streaming analysis with parallel AI calls for maximum speed."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        data = request.json
        if not data:
            raise ValueError("No JSON data received")

        url = data.get('url')
        if not url:
            raise ValueError("URL is required")

        url_valid, url_error = validate_url(url)
        if not url_valid:
            return jsonify({"error": url_error}), 400

        api_key, provider_name, model_name = _extract_provider_params(data)
        if not api_key:
            raise ValueError("API key is required")

        key_valid, key_error = validate_api_key(api_key)
        if not key_valid:
            return jsonify({"error": key_error}), 400

        openai_api_key = api_key

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    def generate():
        import json as _json

        def sse(stage, progress, message, data=None):
            payload = {"stage": stage, "progress": progress, "message": message}
            if data is not None:
                payload["data"] = data
            return f"data: {_json.dumps(payload, default=str)}\n\n"

        try:
            # ── Stage 1: Fetch URL ────────────────────────────────────
            yield sse("fetching", 5, "Fetching URL content...")

            try:
                text_content, soup, used_pw = _smart_fetch_url(url)
            except Exception as e:
                yield sse("error", 0, f"Error fetching URL: {str(e)}")
                return

            method_label = "Playwright (JS-rendered)" if used_pw else "static HTML"
            yield sse("fetched", 10, f"Fetched {len(text_content)} chars via {method_label}")

            # ── Stage 2a: OCR (must finish before AI calls) ───────────
            yield sse("ocr", 12, "Extracting images and running OCR...")

            images_ocr_text = ""
            try:
                static_imgs = extract_image_urls_static(soup, url)
                dynamic_imgs = get_dynamic_image_urls(url)
                all_imgs = list(set(static_imgs + dynamic_imgs))
                if all_imgs:
                    images_ocr_text = extract_text_from_images(all_imgs)
            except Exception as e:
                logger.error(f"OCR error: {e}")

            combined_text = text_content
            if images_ocr_text:
                combined_text = text_content + "\n\n[IMAGE_OCR_SECTION]\n" + images_ocr_text

            # Validate extracted text
            if not combined_text or len(combined_text.strip()) < 50:
                yield sse("error", 0,
                    f"Could not extract sufficient text from URL ({len(combined_text.strip())} chars). "
                    "The page may require JavaScript rendering or may be blocking automated access.")
                return

            yield sse("ocr_done", 20, f"OCR complete ({len(images_ocr_text)} chars from images)")

            # ── Stage 2b: Parallel AI calls ───────────────────────────
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
                from modules.pipeline.output_validator import OutputValidator as OV
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
                    yield sse("threat_summary_done", 40, "Threat summary complete",
                             {"threat_summary": threat_summary})
                except Exception as e:
                    logger.error(f"Threat summary error: {e}")
                    yield sse("threat_summary_done", 40, f"Threat summary failed: {str(e)[:100]}")

                # Wait for IoC extraction
                try:
                    analysis_data = future_ioc.result(timeout=300)
                    ioc_count = sum(
                        len(v) for v in analysis_data.get("indicators_of_compromise", {}).values()
                        if isinstance(v, list)
                    )
                    yield sse("ioc_done", 50, f"Extracted {ioc_count} IoCs",
                             {"analysis_data": {
                                 "indicators_of_compromise": analysis_data.get("indicators_of_compromise", {}),
                                 "ttps": analysis_data.get("ttps", []),
                                 "threat_actors": analysis_data.get("threat_actors", []),
                                 "tools_or_malware": analysis_data.get("tools_or_malware", []),
                             }})
                except Exception as e:
                    logger.error(f"IoC extraction error: {e}")
                    analysis_data = {}
                    yield sse("ioc_done", 50, f"IoC extraction failed: {str(e)[:100]}")

                # Wait for AI Sigma
                try:
                    raw_sigma = future_ai_sigma.result(timeout=300)
                    if raw_sigma and not raw_sigma.startswith("Error"):
                        rules = []
                        current_rule = []
                        for line in raw_sigma.split('\n'):
                            if line.strip().startswith('title:'):
                                if current_rule:
                                    rules.append('\n'.join(current_rule))
                                current_rule = [line]
                            elif not any(skip in line for skip in [
                                '–––––––', 'These rules can be further tuned',
                                'Below are two Sigma rules', 'This rule detects',
                                'This query searches'
                            ]):
                                if current_rule or line.strip():
                                    current_rule.append(line)
                        if current_rule:
                            rules.append('\n'.join(current_rule))
                        more_sigma_rules = '\n\n'.join(rules)
                except Exception as e:
                    logger.error(f"AI Sigma error: {e}")
                    more_sigma_rules = ""

            # ── Stage 3: Parallel rule generation ─────────────────────
            yield sse("rules", 55, "Generating detection rules...")

            yara_rules = []
            mitre_techniques = []
            mitre_tags = []
            tactic_summary = {}
            ioc_sigma_rules = []
            ioc_sigma_yaml = ""
            sigma_matches = []

            def _do_yara():
                return generate_yara_rules(analysis_data)

            def _do_mitre():
                techs = map_iocs_to_mitre(analysis_data)
                tags = get_mitre_tags(techs)
                tac_sum = get_tactic_summary(techs)
                return techs, tags, tac_sum

            def _do_ioc_sigma():
                rules = generate_sigma_rules_for_analysis(analysis_data, article_url=url)
                yaml_str = sigma_rules_to_yaml(rules)
                return rules, yaml_str

            def _do_global_sigma():
                sigma_rules_directory = os.path.join(parent_dir, "Global_Sigma_Rules")
                if not os.path.exists(sigma_rules_directory):
                    return []
                all_rules = load_sigma_rules_local(sigma_rules_directory)
                return match_sigma_rules_with_report(
                    sigma_rules=all_rules,
                    analysis_data=analysis_data,
                    report_text=combined_text.lower(),
                    root_directory=sigma_rules_directory,
                    mitre_techniques=None,
                    threshold=25.0,
                    max_results=15,
                )

            mitre_techniques = []
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_yara = executor.submit(_do_yara)
                future_mitre = executor.submit(_do_mitre)
                future_ioc_sigma = executor.submit(_do_ioc_sigma)

                try:
                    yara_rules = future_yara.result(timeout=120)
                    yield sse("yara_done", 62, f"Generated {len(yara_rules)} YARA rules")
                except Exception as e:
                    logger.error(f"YARA error: {e}")
                    yield sse("yara_done", 62, "YARA generation failed")

                try:
                    mitre_techniques, mitre_tags, tactic_summary = future_mitre.result(timeout=120)
                    yield sse("mitre_done", 68, f"Mapped {len(mitre_techniques)} MITRE techniques",
                             {"mitre_mapping": {
                                 "techniques": mitre_techniques,
                                 "tactic_summary": tactic_summary,
                                 "tags": mitre_tags,
                             }})
                except Exception as e:
                    logger.error(f"MITRE error: {e}")
                    yield sse("mitre_done", 68, "MITRE mapping failed")

                try:
                    ioc_sigma_rules, ioc_sigma_yaml = future_ioc_sigma.result(timeout=120)
                    yield sse("sigma_done", 75, f"Generated {len(ioc_sigma_rules)} Sigma rules")
                except Exception as e:
                    logger.error(f"IoC Sigma error: {e}")
                    yield sse("sigma_done", 75, "Sigma generation failed")

            # Global Sigma matching — runs AFTER MITRE so it can use technique data
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
                else:
                    sigma_matches = []
                yield sse("sigma_match_done", 80, f"Matched {len(sigma_matches)} global Sigma rules",
                         {"sigma_matches": sigma_matches})
            except Exception as e:
                logger.error(f"Global Sigma error: {e}")
                sigma_matches = []
                yield sse("sigma_match_done", 80, "Sigma matching failed")

            # ── Stage 4: SIEM queries ─────────────────────────────────
            yield sse("siem", 82, "Generating SIEM queries...")

            siem_queries = {
                "splunk": {"description": "", "query": "", "notes": ""},
                "qradar": {"description": "", "query": "", "notes": ""},
                "elastic": {"description": "", "query": "", "notes": ""},
                "sentinel": {"description": "", "query": "", "notes": ""},
            }

            def _do_siem_structured():
                structured = generate_siem_queries(analysis_data)
                return siem_queries_to_flat(structured)

            def _do_siem_ai():
                if not more_sigma_rules:
                    return None
                return convert_sigma_to_siem_queries(
                    sigma_rules=more_sigma_rules,
                    openai_api_key=openai_api_key,
                    provider_name=provider_name,
                    model_name=model_name,
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

            # ── Combine all Sigma ─────────────────────────────────────
            all_sigma_yaml = ioc_sigma_yaml
            if more_sigma_rules:
                all_sigma_yaml = (all_sigma_yaml + "\n---\n" + more_sigma_rules) if all_sigma_yaml else more_sigma_rules

            # ── Stage 5: Atomic Red Team Test Scenarios ──────────────
            atomic_tests = []
            if all_sigma_yaml and len(all_sigma_yaml.strip()) > 20:
                yield sse("atomic_tests", 93, "Generating Atomic Red Team test scenarios...")
                try:
                    atomic_tests = generate_atomic_tests_from_sigma(
                        sigma_rules=all_sigma_yaml,
                        threat_context=threat_summary,
                        openai_api_key=openai_api_key,
                        provider_name=provider_name,
                        model_name=model_name,
                    )
                    yield sse("atomic_tests_done", 97, f"Generated {len(atomic_tests)} atomic test scenarios",
                             {"atomic_tests": atomic_tests})
                except Exception as e:
                    logger.error(f"Atomic test generation error: {e}")
                    yield sse("atomic_tests_done", 97, "Atomic test generation failed")

            # ── Final result ──────────────────────────────────────────
            yield sse("finalizing", 98, "Compiling final report...")

            response = {
                "threat_summary": threat_summary,
                "analysis_data": {
                    "indicators_of_compromise": analysis_data.get("indicators_of_compromise", {}),
                    "ttps": analysis_data.get("ttps", []),
                    "threat_actors": analysis_data.get("threat_actors", []),
                    "tools_or_malware": analysis_data.get("tools_or_malware", []),
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

            # Save to database
            try:
                report_data = {
                    'id': str(uuid.uuid4()),
                    'url': url,
                    'timestamp': datetime.now().isoformat(),
                    'provider': provider_name,
                    'model': model_name,
                    **response
                }
                ReportRepository.create(report_data)
                logger.info(f"Saved report with ID: {report_data['id']}")
            except Exception as e:
                logger.error(f"Error saving report: {e}")

            yield sse("complete", 100, "Analysis complete!", response)

        except Exception as e:
            logger.error(f"Stream analysis error: {e}")
            logger.error(traceback.format_exc())
            yield sse("error", 0, str(e))

    return app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )


@app.route('/api/generate_rule', methods=['POST', 'OPTIONS'])
def generate_rule():
    logger.info(f"generate_rule called with method: {request.method}")
    
    if request.method == 'OPTIONS':
        logger.info("Handling OPTIONS request")
        return '', 204
        
    try:
        logger.info("Processing POST request to generate_rule")
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        prompt = data.get('prompt')
        api_key, provider_name, model_name = _extract_provider_params(data)

        logger.info(f"Provider: {provider_name}, API Key provided: {bool(api_key)}")

        if not prompt or not api_key:
            logger.error("Missing required parameters")
            return jsonify({'error': 'Missing required parameters (prompt + api_key/openai_api_key)'}), 400

        # Validate prompt
        prompt_valid, prompt_error = validate_prompt(prompt)
        if not prompt_valid:
            return jsonify({'error': prompt_error}), 400

        # Validate API key
        key_valid, key_error = validate_api_key(api_key)
        if not key_valid:
            return jsonify({'error': key_error}), 400

        # Get QA system instance with multi-provider support
        qa = get_qa_system(api_key, provider_name, model_name)
        
        # Generate rule using QA system
        result = qa._generate_response(prompt, "sigma")
        
        if not result or "rule" not in result:
            return jsonify({'error': 'Failed to generate rule'}), 500

        # Calculate confidence score
        confidence_result = qa.confidence_calculator.calculate_confidence(result["rule"], result.get("test_cases", []))

        # Ensure author is set to PERSEPTOR
        if "rule" in result and isinstance(result["rule"], dict):
            result["rule"]["author"] = "PERSEPTOR"
            result["rule"]["date"] = datetime.now().strftime('%Y/%m/%d')

        # Save the rule to storage
        rule_data = {
            'id': str(uuid.uuid4()),
            'title': result["rule"].get("title", "Untitled Rule"),
            'description': result["rule"].get("description", ""),
            'author': result["rule"].get("author", "PERSEPTOR"),
            'date': result["rule"].get("date", datetime.now().strftime('%Y/%m/%d')),
            'product': 'sigma',
            'confidence_score': confidence_result["overall_score"],
            'mitre_techniques': result.get("mitre_techniques", []),
            'test_cases': result.get("test_cases", []),
            'recommendations': result.get("recommendations", []),
            'references': result.get("references", []),
            'rule_content': result["rule"],
            'created_at': datetime.now().isoformat()
        }
        
        RuleRepository.create(rule_data)

        return jsonify({
            'rule': result["rule"],
            'explanation': result.get("explanation", ""),
            'test_cases': result.get("test_cases", []),
            'mitre_techniques': result.get("mitre_techniques", []),
            'recommendations': result.get("recommendations", []),
            'references': result.get("references", []),
            'confidence_score': confidence_result["overall_score"],
            'component_scores': confidence_result["component_scores"],
            'explanations': confidence_result.get("explanations", {}),
            'weights': confidence_result.get("weights", {}),
            'maturity': confidence_result.get("maturity", {}),
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in generate_rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rules', methods=['GET'])
@rate_limit("read")
def get_rules():
    """Get all created rules from database"""
    try:
        rules = RuleRepository.list_all()
        return jsonify({
            'rules': rules,
            'count': len(rules)
        })
    except Exception as e:
        logger.error(f"Error fetching rules: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """Delete a specific rule from database"""
    try:
        deleted = RuleRepository.delete(rule_id)
        if not deleted:
            return jsonify({'error': 'Rule not found'}), 404
        return jsonify({'message': 'Rule deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rules/<rule_id>/download', methods=['GET'])
def download_rule(rule_id):
    """Download a specific rule as YAML file"""
    try:
        rule = RuleRepository.get_by_id(rule_id)
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404

        import yaml
        from flask import Response

        yaml_content = yaml.dump(rule['rule_content'], default_flow_style=False, allow_unicode=True)
        safe_title = rule["title"].replace(" ", "_").replace("/", "_")

        return Response(
            yaml_content,
            mimetype='text/yaml',
            headers={'Content-Disposition': f'attachment; filename="{safe_title}.yaml"'}
        )
    except Exception as e:
        logger.error(f"Error downloading rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports', methods=['GET'])
@rate_limit("read")
def get_reports():
    """Get all analyzed reports from database"""
    try:
        reports = ReportRepository.list_all()
        return jsonify({
            'reports': reports,
            'count': len(reports)
        })
    except Exception as e:
        logger.error(f"Error fetching reports: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Delete a specific report from database"""
    try:
        deleted = ReportRepository.delete(report_id)
        if not deleted:
            return jsonify({'error': 'Report not found'}), 404

        logger.info(f"Deleted report with ID: {report_id}")
        return jsonify({'message': 'Report deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        return jsonify({'error': str(e)}), 500

# --- Session Management Endpoints ---

@app.route('/api/session', methods=['POST'])
@validate_json_content_type
def create_session():
    """Create a new session with encrypted API key storage."""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '')
        provider = data.get('provider', 'openai')
        model = data.get('model')

        if not api_key:
            return jsonify({'error': 'api_key is required'}), 400

        result = session_manager.create_session(api_key, provider, model)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session', methods=['DELETE'])
def destroy_session():
    """Destroy the current session."""
    try:
        token = request.headers.get('X-Session-Token')
        if not token:
            return jsonify({'error': 'X-Session-Token header required'}), 400

        session_manager.destroy_session(token)
        return jsonify({'message': 'Session destroyed'})
    except Exception as e:
        logger.error(f"Error destroying session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/usage', methods=['GET'])
def get_usage():
    """Get token usage statistics matching frontend TokenUsage interface."""
    try:
        # Resolve session to get session_id for scoped usage
        session_token = request.headers.get('X-Session-Token')
        session_id = None
        if session_token:
            session_data = session_manager.validate_session(session_token)
            if session_data:
                session_id = session_data.get('session_id')

        # Always show total usage across all sessions (session_id filtering
        # only useful if per-session tracking is implemented in AI calls)
        summary = TokenUsageRepository.get_usage_summary(None)

        # Estimate cost based on tokens (rough average: $0.002/1K input, $0.008/1K output)
        prompt_tokens = summary.get('total_prompt_tokens', 0)
        completion_tokens = summary.get('total_completion_tokens', 0)
        estimated_cost = (prompt_tokens / 1000 * 0.002) + (completion_tokens / 1000 * 0.008)

        # Return flat object matching frontend TokenUsage interface
        return jsonify({
            'total_prompt_tokens': prompt_tokens,
            'total_completion_tokens': completion_tokens,
            'total_cost': round(estimated_cost, 6),
            'request_count': summary.get('total_requests', 0),
        })
    except Exception as e:
        logger.error(f"Error fetching usage: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with system status."""
    sigma_rules_dir = config.sigma_rules_dir
    sigma_count = 0
    if os.path.exists(sigma_rules_dir):
        sigma_count = sum(
            1 for f in os.listdir(sigma_rules_dir)
            if f.endswith(('.yml', '.yaml'))
        )

    return jsonify({
        "status": "ok",
        "version": config.version,
        "app_name": config.app_name,
        "debug": config.debug,
        "default_provider": config.default_provider,
        "default_model": config.default_model,
        "sigma_rules_loaded": sigma_count,
        "available_providers": list(config.ai_providers.keys()),
        "timestamp": datetime.now().isoformat(),
    })


@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available AI models organized by provider with detailed info."""
    return jsonify({
        "providers": get_available_providers(),
        "default_provider": config.default_provider,
        "default_model": config.default_model,
    })


if __name__ == '__main__':
    logger.info(f"Starting {config.app_name} v{config.version}")
    logger.info(f"Default AI provider: {config.default_provider}, model: {config.default_model}")

    # CRITICAL: Disable reloader to prevent crashes during long-running analysis.
    # Torch/easyocr imports trigger thousands of file-watch events that cause
    # the watchdog reloader to restart Flask mid-request → ECONNRESET on frontend.
    # debug=True still gives detailed error pages, just no auto-reload.
    app.run(
        host=config.host,
        debug=True,
        port=config.port,
        use_reloader=False,
    )