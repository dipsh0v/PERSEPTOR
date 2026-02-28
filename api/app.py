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
    _smart_fetch_url,
    get_dynamic_image_urls,
    extract_image_urls_static,
    extract_text_from_images,
    fetch_page_content,
    extract_text_from_pdf_bytes,
)

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
from modules.middleware import rate_limit, validate_json_content_type, extract_provider_params
from modules.pipeline.orchestrator import run_analysis_pipeline_sync, run_analysis_pipeline_stream
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
        api_key, provider_name, model_name = extract_provider_params(data)
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

        response = run_analysis_pipeline_sync(
            text_content=text_content,
            images_ocr_text=images_ocr_text,
            combined_text=combined_text,
            source_url=url,
            provider_name=provider_name,
            model_name=model_name,
            openai_api_key=openai_api_key,
            parent_dir=parent_dir
        )

        return jsonify(response)

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

        api_key, provider_name, model_name = extract_provider_params(data)
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
            yield from run_analysis_pipeline_stream(
                text_content=text_content,
                images_ocr_text=images_ocr_text,
                combined_text=combined_text,
                source_url=url,
                provider_name=provider_name,
                model_name=model_name,
                openai_api_key=openai_api_key,
                parent_dir=parent_dir,
                sse=sse
            )

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


@app.route('/api/analyze/pdf/stream', methods=['POST', 'OPTIONS'])
def analyze_pdf_stream():
    """SSE streaming analysis for uploaded PDF files."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        # Validate PDF file presence
        if 'pdf' not in request.files:
            raise ValueError("No PDF file provided")

        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            raise ValueError("No file selected")

        if not pdf_file.filename.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are accepted")

        # Read PDF bytes (check size: max 20MB)
        pdf_bytes = pdf_file.read()
        if len(pdf_bytes) > 20 * 1024 * 1024:
            raise ValueError("PDF file exceeds 20MB limit")

        if len(pdf_bytes) == 0:
            raise ValueError("PDF file is empty")

        pdf_filename = pdf_file.filename

        # Extract provider params from form data
        form_data = {
            'provider': request.form.get('provider', 'openai'),
            'model': request.form.get('model', None),
            'openai_api_key': request.form.get('openai_api_key', ''),
            'api_key': request.form.get('api_key', ''),
        }
        api_key, provider_name, model_name = extract_provider_params(form_data)
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
            # ── Stage 1: Extract text from PDF ─────────────────────────
            yield sse("fetching", 5, f"Extracting text from PDF: {pdf_filename}...")

            try:
                combined_text = extract_text_from_pdf_bytes(pdf_bytes)
            except Exception as e:
                yield sse("error", 0, f"Error reading PDF: {str(e)}")
                return

            if not combined_text or len(combined_text.strip()) < 50:
                yield sse("error", 0,
                    f"Could not extract sufficient text from PDF ({len(combined_text.strip())} chars). "
                    "The PDF may be image-based or contain very little text.")
                return

            text_content = combined_text
            images_ocr_text = ""  # No image OCR for PDF uploads

            yield sse("fetched", 15, f"Extracted {len(combined_text)} chars from PDF")
            yield sse("ocr_done", 20, "PDF text extraction complete")

            # ── Stage 2: Parallel AI calls ─────────────────────────────
            yield from run_analysis_pipeline_stream(
                text_content=text_content,
                images_ocr_text=images_ocr_text,
                combined_text=text_content, # PDF extraction does not have image OCR
                source_url=f"pdf://{pdf_filename}",
                provider_name=provider_name,
                model_name=model_name,
                openai_api_key=openai_api_key,
                parent_dir=parent_dir,
                sse=sse
            )

        except Exception as e:
            logger.error(f"PDF stream analysis error: {e}")
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
        api_key, provider_name, model_name = extract_provider_params(data)

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