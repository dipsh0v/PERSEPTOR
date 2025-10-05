import os
import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import io
from modules.ui_module import (
    display_analysis_data,
    print_yara_rules_pretty,  
    print_colored,
    print_rule,
    print_table,
    print_sigma_rules_pretty,
    print_additional_sigma_rules_in_tables,
    print_refined_sigma_in_tables,
)

from modules.logger_module import CSVLogger
from modules.gpt_module import (
    safe_json_parse,
    extract_iocs_ttps_gpt,
    refine_sigma_queries_with_gpt,
    generate_more_sigma_rules_from_article,
    summarize_threat_report,
    convert_sigma_to_siem_queries
)
from modules.ocr_module import (
    get_dynamic_image_urls,
    extract_image_urls_static,
    extract_text_from_images
)
from modules.sigma_module import (
    generate_sigma_rules_for_commands,
)
from modules.yara_module import generate_yara_rules
from modules.global_sigma_match_module import (
    load_sigma_rules_local,
    match_sigma_rules_with_report
)
from modules.qa_module import create_qa_system

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def display_logo():
    print(r"""
        ██████╗ ███████╗██████╗ ███████╗███████╗██████╗ ████████╗ ██████╗ ██████╗ 
        ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
        ██████╔╝█████╗  ██████╔╝███████╗█████╗  ██████╔╝   ██║   ██║   ██║██████╔╝
        ██╔═══╝ ██╔══╝  ██╔══██╗╚════██║██╔══╝  ██╔═══╝    ██║   ██║   ██║██╔══██╗
        ██║     ███████╗██║  ██║███████║███████╗██║        ██║   ╚██████╔╝██║  ██║
        ╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝        ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                                                                           
                    AI Driven Threat Intelligence/Hunting Toolkit
""")

def process_manual_url(openai_api_key=""):
    url = input("Enter the URL to analyze: ")
    try:
        print_colored("[+] Fetching content from URL...", "cyan")
        resp = requests.get(url, timeout=15)
        soup = BeautifulSoup(resp.content, "html.parser")
        text_content = soup.get_text()

        print_colored("[+] Collecting static images...", "green")
        static_imgs = extract_image_urls_static(soup, url)
        print_colored("[+] Collecting dynamic images...", "green")
        dynamic_imgs = get_dynamic_image_urls(url)
        all_imgs = list(set(static_imgs + dynamic_imgs))

        print_colored("[+] Starting OCR process...", "green")
        images_ocr_text = extract_text_from_images(all_imgs)
        combined_text = text_content + "\n\n[IMAGE_OCR_SECTION]\n" + images_ocr_text

        threat_summary = summarize_threat_report(
            text=combined_text,
            openai_api_key=openai_api_key
        )
        print_rule("Threat Summary")
        print_colored(threat_summary, "yellow")

        gpt_json_str = extract_iocs_ttps_gpt(combined_text, openai_api_key=openai_api_key)
        cleaned_json_str = (
            gpt_json_str
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        analysis_data = safe_json_parse(cleaned_json_str)
        display_analysis_data(analysis_data)

        yara_rules = generate_yara_rules(analysis_data)
        print_rule("Generated YARA Rules")
        print_yara_rules_pretty(yara_rules)

        print_colored("[+] Generating additional Sigma rules with AI...", "green")
        more_sigma_rules = generate_more_sigma_rules_from_article(
            article_text=text_content,
            images_ocr_text=images_ocr_text,
            openai_api_key=openai_api_key
        )
        print_rule("Additional Sigma Rules")
        print_additional_sigma_rules_in_tables(more_sigma_rules)

        print_rule("Global Sigma Matches")
        sigma_rules_directory = os.path.join(os.path.expanduser("~"), "Desktop", "SigmaHQ - Process Creation")
        sigma_rules = load_sigma_rules_local(sigma_rules_directory)
        print_colored(f"[+] Loaded {len(sigma_rules)} Sigma rules", "green")
        
        # Get global sigma matches
        sigma_matches = match_sigma_rules_with_report(
            sigma_rules=sigma_rules,
            analysis_data=analysis_data,
            report_text=combined_text.lower(),
            root_directory=sigma_rules_directory,
            sigma_repo_path="rules/windows/process_creation",
            threshold=0.0
        )

    except Exception as e:
        print_colored(f"[!] Error processing URL: {url} - {e}", "red")

def process_qa_query(openai_api_key=""):
    """
    Process a natural language query to generate Sigma rules.
    """
    try:
        # Create Q&A system
        qa_system = create_qa_system(openai_api_key=openai_api_key)
        
        while True:
            print_colored("\nQ&A Options:", "bold cyan")
            print_colored("1. Enter a new query", "white")
            print_colored("2. Return to main menu", "white")
            
            choice = input("Select an option (1/2): ")
            
            if choice == "1":
                query = input("\nEnter your query (e.g., 'Create a Sigma rule to detect suspicious PowerShell script execution'): ")
                print_rule("Processing Query")
                qa_system.process_query(query)
            elif choice == "2":
                break
            else:
                print_colored("Invalid choice. Please try again.", "red")
                
    except Exception as e:
        print_colored(f"[!] Error in Q&A processing: {e}", "red")

def main():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "terminal_output.csv")
    logger = CSVLogger(desktop_path)

    original_stdout = sys.stdout
    sys.stdout = logger

    try:
        display_logo()
        openai_api_key = ""

        while True:
            print_colored("\nOptions:", "bold cyan")
            print_colored("1. Manual URL input", "white")
            print_colored("2. Q&A Option", "white")
            print_colored("3. Exit", "white")

            choice = input("Select an option (1/2/3): ")
            if choice == "1":
                process_manual_url(openai_api_key=openai_api_key)
            elif choice == "2":
                process_qa_query(openai_api_key=openai_api_key)
            elif choice == "3":
                print_colored("Exiting...", "bold yellow")
                break
            else:
                print_colored("Invalid choice. Please try again.", "red")

    finally:
        sys.stdout = original_stdout
        logger.close()
        print_colored(f"All terminal outputs have been saved to {desktop_path}", "yellow")

@app.route('/api/generate-pdf', methods=['POST', 'OPTIONS'])
def generate_pdf():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        data = request.get_json()
        analysis_result = data.get('analysis_result')
        
        if not analysis_result:
            return jsonify({'error': 'No analysis result provided'}), 400

        # Create PDF report
        pdf_generator = PDFReportGenerator()
        
        # Prepare sections for the report
        sections = [
            ReportSection(
                title="Threat Summary",
                content=analysis_result.get('threat_summary', 'No threat summary available')
            ),
            ReportSection(
                title="Indicators of Compromise",
                content=format_iocs(analysis_result.get('analysis_data', {}).get('indicators_of_compromise', {}))
            ),
            ReportSection(
                title="MITRE ATT&CK TTPs",
                content=format_ttps(analysis_result.get('analysis_data', {}).get('ttps', []))
            ),
            ReportSection(
                title="Threat Actors",
                content=format_list(analysis_result.get('analysis_data', {}).get('threat_actors', []))
            ),
            ReportSection(
                title="Tools & Malware",
                content=format_list(analysis_result.get('analysis_data', {}).get('tools_or_malware', []))
            ),
            ReportSection(
                title="Generated Sigma Rules",
                content=analysis_result.get('generated_sigma_rules', 'No Sigma rules generated')
            ),
            ReportSection(
                title="Generated YARA Rules",
                content=format_yara_rules(analysis_result.get('yara_rules', []))
            ),
            ReportSection(
                title="Possible Sigma Matches",
                content=format_sigma_matches(analysis_result.get('sigma_matches', []))
            )
        ]

        # Generate PDF
        pdf_bytes = pdf_generator.generate_report(
            title="Threat Analysis Report",
            sections=sections
        )

        response = send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'threat_analysis_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
        
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def format_iocs(iocs):
    if not iocs:
        return "No indicators of compromise found"
    
    formatted = []
    for category, items in iocs.items():
        if items:
            formatted.append(f"\n{category.replace('_', ' ').title()}:")
            for item in items:
                formatted.append(f"- {item}")
    
    return "\n".join(formatted) if formatted else "No indicators of compromise found"

def format_ttps(ttps):
    if not ttps:
        return "No TTPs found"
    
    formatted = []
    for ttp in ttps:
        formatted.append(f"\n{ttp['technique_name']} ({ttp['mitre_id']})")
        formatted.append(f"Description: {ttp['description']}")
    
    return "\n".join(formatted)

def format_list(items):
    if not items:
        return "No items found"
    
    return "\n".join([f"- {item}" for item in items])

def format_yara_rules(rules):
    if not rules:
        return "No YARA rules generated"
    
    formatted = []
    for rule in rules:
        formatted.append(f"\n{rule['name']}")
        formatted.append(f"Description: {rule['description']}")
        formatted.append(f"Severity: {rule['severity']}")
        formatted.append(f"Tags: {', '.join(rule['tags'])}")
        formatted.append(f"Rule:\n{rule['rule']}")
    
    return "\n".join(formatted)

def format_sigma_matches(matches):
    if not matches:
        return "No Sigma matches found"
    
    formatted = []
    for match in matches:
        formatted.append(f"\n{match['title']} ({match['id']})")
        formatted.append(f"Level: {match['level']}")
        formatted.append(f"Match Ratio: {match['match_ratio']}%")
        formatted.append(f"Description: {match['description']}")
        if match['matched_keywords']:
            formatted.append(f"Matched Keywords: {', '.join(match['matched_keywords'])}")
        if match['tags']:
            formatted.append(f"Tags: {', '.join(match['tags'])}")
    
    return "\n".join(formatted)

if __name__ == "__main__":
    app.run(debug=True, port=5000)





