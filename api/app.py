from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import traceback
import logging

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# PERSEPTOR modüllerini import et
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from modules.qa_module import create_qa_system
from modules.gpt_module import (
    summarize_threat_report,
    extract_iocs_ttps_gpt,
    safe_json_parse,
    generate_more_sigma_rules_from_article,
    convert_sigma_to_siem_queries
)
from modules.ocr_module import (
    get_dynamic_image_urls,
    extract_image_urls_static,
    extract_text_from_images
)
from modules.yara_module import generate_yara_rules
from modules.sigma_module import generate_sigma_rules_for_commands
from modules.global_sigma_match_module import (
    load_sigma_rules_local,
    match_sigma_rules_with_report
)
import json
import uuid

app = Flask(__name__)

# Sadece Flask-CORS kullan
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

# Initialize QA system
qa_system = None

# Rules storage (in production, use a database)
rules_storage = []

def get_qa_system(openai_api_key):
    global qa_system
    if not qa_system:
        qa_system = create_qa_system(openai_api_key=openai_api_key)
    return qa_system

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_url():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    try:
        data = request.json
        if not data:
            raise ValueError("No JSON data received")
            
        url = data.get('url')
        if not url:
            raise ValueError("URL is required")
            
        openai_api_key = data.get('openai_api_key', '')
        if not openai_api_key:
            raise ValueError("OpenAI API key is required")

        logger.info(f"Starting analysis for URL: {url}")

        # URL'den içerik çek
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error fetching URL: {str(e)}")
            raise ValueError(f"Error fetching URL: {str(e)}")

        soup = BeautifulSoup(resp.content, "html.parser")
        text_content = soup.get_text()

        # Görüntüleri topla
        try:
            static_imgs = extract_image_urls_static(soup, url)
            dynamic_imgs = get_dynamic_image_urls(url)
            all_imgs = list(set(static_imgs + dynamic_imgs))
        except Exception as e:
            logger.error(f"Error extracting images: {str(e)}")
            all_imgs = []

        # OCR işlemi
        try:
            images_ocr_text = extract_text_from_images(all_imgs)
            combined_text = text_content + "\n\n[IMAGE_OCR_SECTION]\n" + images_ocr_text
        except Exception as e:
            logger.error(f"Error in OCR processing: {str(e)}")
            images_ocr_text = ""
            combined_text = text_content

        # Tehdit özeti
        try:
            threat_summary = summarize_threat_report(
                text=combined_text,
                openai_api_key=openai_api_key
            )
        except Exception as e:
            logger.error(f"Error generating threat summary: {str(e)}")
            threat_summary = "Error generating threat summary"

        # IOC ve TTP analizi
        try:
            gpt_json_str = extract_iocs_ttps_gpt(combined_text, openai_api_key=openai_api_key)
            cleaned_json_str = gpt_json_str.replace("```json", "").replace("```", "").strip()
            analysis_data = safe_json_parse(cleaned_json_str)
        except Exception as e:
            logger.error(f"Error in IOC/TTP analysis: {str(e)}")
            analysis_data = {"error": "Error in IOC/TTP analysis"}

        # YARA kuralları
        try:
            yara_rules_text = generate_yara_rules(analysis_data)
            yara_rules = []
            
            # YARA kurallarını ayrıştır
            current_rule = None
            for line in yara_rules_text.split('\n'):
                if line.startswith('rule '):
                    if current_rule:
                        yara_rules.append(current_rule)
                    current_rule = {
                        'name': line.split('rule ')[1].strip('{').strip(),
                        'description': '',
                        'rule': line,
                        'severity': 'medium',
                        'tags': [],
                        'metadata': {
                            'author': 'PERSEPTOR',
                            'version': '1.0'
                        }
                    }
                elif current_rule:
                    current_rule['rule'] += '\n' + line
                    if 'description = ' in line:
                        current_rule['description'] = line.split('description = ')[1].strip('"')
            
            if current_rule:
                yara_rules.append(current_rule)
        except Exception as e:
            logger.error(f"Error generating YARA rules: {str(e)}")
            yara_rules = []

        # Sigma kuralları
        try:
            more_sigma_rules = generate_more_sigma_rules_from_article(
                article_text=text_content,
                images_ocr_text=images_ocr_text,
                openai_api_key=openai_api_key
            )
            
            # Sigma kurallarını temizle ve düzenle
            if more_sigma_rules and not more_sigma_rules.startswith("Error"):
                # YAML belgelerini ayır
                rules = []
                current_rule = []
                
                for line in more_sigma_rules.split('\n'):
                    # Yeni kural başlangıcı
                    if line.strip().startswith('title:'):
                        if current_rule:
                            rules.append('\n'.join(current_rule))
                        current_rule = [line]
                    # Açıklama metinlerini ve ayraçları atla
                    elif not any(skip in line for skip in [
                        '–––––––––––––––––––––––––––––––––––––––––––––––',
                        'These rules can be further tuned',
                        'Below are two Sigma rules',
                        'This rule detects',
                        'This query searches'
                    ]):
                        if current_rule or line.strip():
                            current_rule.append(line)
            
                # Son kuralı ekle
                if current_rule:
                    rules.append('\n'.join(current_rule))
                
                # Temizlenmiş kuralları birleştir
                more_sigma_rules = '\n\n'.join(rules)
            else:
                more_sigma_rules = ""
        except Exception as e:
            logger.error(f"Error generating Sigma rules: {str(e)}")
            more_sigma_rules = ""

        # SIEM Queries dönüştürme
        try:
            if more_sigma_rules and not more_sigma_rules.startswith("Error"):
                siem_queries = convert_sigma_to_siem_queries(
                    sigma_rules=more_sigma_rules,
                    openai_api_key=openai_api_key
                )
            else:
                siem_queries = {
                    "splunk": {"description": "No Sigma rules available", "query": "N/A", "notes": "Generate Sigma rules first"},
                    "qradar": {"description": "No Sigma rules available", "query": "N/A", "notes": "Generate Sigma rules first"},
                    "elastic": {"description": "No Sigma rules available", "query": "N/A", "notes": "Generate Sigma rules first"},
                    "sentinel": {"description": "No Sigma rules available", "query": "N/A", "notes": "Generate Sigma rules first"}
                }
        except Exception as e:
            logger.error(f"Error converting Sigma to SIEM queries: {str(e)}")
            siem_queries = {
                "splunk": {"description": "Error generating query", "query": "Error", "notes": str(e)},
                "qradar": {"description": "Error generating query", "query": "Error", "notes": str(e)},
                "elastic": {"description": "Error generating query", "query": "Error", "notes": str(e)},
                "sentinel": {"description": "Error generating query", "query": "Error", "notes": str(e)}
            }

        # Global Sigma eşleşmeleri
        try:
            sigma_rules_directory = os.path.join(os.path.expanduser("~"), "Desktop", "SigmaHQ - Process Creation")
            sigma_rules = load_sigma_rules_local(sigma_rules_directory)
            sigma_matches = match_sigma_rules_with_report(
                sigma_rules=sigma_rules,
                analysis_data=analysis_data,
                report_text=combined_text.lower(),
                root_directory=sigma_rules_directory,
                sigma_repo_path="rules/windows/process_creation",
                threshold=0.0
            )
        except Exception as e:
            logger.error(f"Error in Sigma matching: {str(e)}")
            sigma_matches = []

        # Yanıt oluştur
        response = {
            "threat_summary": threat_summary,
            "analysis_data": {
                "indicators_of_compromise": analysis_data.get("indicators_of_compromise", {}),
                "ttps": analysis_data.get("ttps", []),
                "threat_actors": analysis_data.get("threat_actors", []),
                "tools_or_malware": analysis_data.get("tools_or_malware", [])
            },
            "yara_rules": yara_rules,
            "generated_sigma_rules": more_sigma_rules,
            "siem_queries": siem_queries,
            "sigma_matches": sigma_matches
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in analyze_url: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

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
        openai_api_key = data.get('openai_api_key')
        
        logger.info(f"Prompt: {prompt}")
        logger.info(f"OpenAI API Key provided: {bool(openai_api_key)}")
        
        if not prompt or not openai_api_key:
            logger.error("Missing required parameters")
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Get QA system instance
        qa = get_qa_system(openai_api_key)
        
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
        
        rules_storage.append(rule_data)

        return jsonify({
            'rule': result["rule"],
            'explanation': result.get("explanation", ""),
            'test_cases': result.get("test_cases", []),
            'mitre_techniques': result.get("mitre_techniques", []),
            'recommendations': result.get("recommendations", []),
            'references': result.get("references", []),
            'confidence_score': confidence_result["overall_score"],
            'component_scores': confidence_result["component_scores"],
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in generate_rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Get all created rules"""
    try:
        return jsonify({
            'rules': rules_storage,
            'count': len(rules_storage)
        })
    except Exception as e:
        logger.error(f"Error fetching rules: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """Delete a specific rule"""
    try:
        global rules_storage
        rules_storage = [rule for rule in rules_storage if rule['id'] != rule_id]
        return jsonify({'message': 'Rule deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rules/<rule_id>/download', methods=['GET'])
def download_rule(rule_id):
    """Download a specific rule as YAML file"""
    try:
        rule = next((r for r in rules_storage if r['id'] == rule_id), None)
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404
        
        import yaml
        from io import StringIO
        
        # Convert rule content to YAML
        yaml_content = yaml.dump(rule['rule_content'], default_flow_style=False, allow_unicode=True)
        
        from flask import Response
        return Response(
            yaml_content,
            mimetype='text/yaml',
            headers={'Content-Disposition': f'attachment; filename="{rule["title"].replace(" ", "_")}.yaml"'}
        )
    except Exception as e:
        logger.error(f"Error downloading rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 