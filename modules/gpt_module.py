import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

################################################################################
# Utility Functions
################################################################################

def safe_json_parse(json_str: str) -> dict:
    """
    Safely parse a JSON string, returning a dictionary or empty {} on error.
    """
    try:
        return json.loads(json_str)
    except Exception as e:
        print(f"[!] JSON parse error: {e}")
        return {}


################################################################################
# Model Configuration
################################################################################

# Latest OpenAI models for optimal performance (as of 2025)
# gpt-4.1-2025-04-14: Latest GPT-4.1 model with best performance
# gpt-4.1-mini-2025-04-14: Optimized mini version for cost-effectiveness
# o4-mini-2025-04-16: Latest reasoning model for complex tasks
DEFAULT_MODEL = "gpt-4.1-2025-04-14"
DEFAULT_TEMPERATURE = 0.1  # Lower temperature for more consistent outputs
DEFAULT_REASONING_EFFORT = "high"  # Maximum reasoning effort for best results

def get_openai_model(model_name: str = None, temperature: float = None,
                     reasoning_effort: str = "medium", openai_api_key: str = ""):
    if model_name is None:
        model_name = DEFAULT_MODEL
    if temperature is None:
        temperature = DEFAULT_TEMPERATURE

    # The new O-series doesn't support temperature param
    O_SERIES_MODELS = {
        "o1", "o1-mini", "o1-preview", "o1-preview-2024-09-12",
        "o3", "o3-mini", "o3-mini-2024-09-12", 
        "o4", "o4-mini", "o4-mini-2025-04-16"
    }  # Latest reasoning models

    print(f"[DEBUG] Model: {model_name}, Is O-series: {model_name in O_SERIES_MODELS}")
    
    if model_name in O_SERIES_MODELS:
        print(f"[DEBUG] Using O-series model without temperature")
        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=openai_api_key
        )
    else:
        print(f"[DEBUG] Using regular model with temperature: {temperature}")
        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=openai_api_key,
            temperature=temperature
        )

    return llm


################################################################################
# Summarize Threat Report (Example: uses a “large reasoning” model)
################################################################################

def summarize_threat_report(
    text: str,
    openai_api_key: str = "",
    model_name: str = "gpt-4.1-2025-04-14",  
    reasoning_effort: str = "high"
) -> str:
    """
    Summarizes the threat scenario with chosen model (gpt-4.1-2025-04-14, o4-mini-2025-04-16, etc.).
    """
    try:
        llm = get_openai_model(
            model_name=model_name,
            temperature=0.1,  
            reasoning_effort=reasoning_effort,
            openai_api_key=openai_api_key
        )

        prompt_content = f"""
You are a senior cybersecurity analyst. Your task:

1. Carefully read the following text about a potential cyber threat.
2. Provide a concise, **plain text** summary.
3. Include the following elements if they are present:
   • Key CVEs or vulnerabilities
   • Severity level (low, medium, high, critical)
   • Targeted sector(s) and region(s)
   • Notable TTPs and any recommended mitigations

4. If the text does **not** mention any CVEs, vulnerabilities, or TTPs, say “No data available on CVEs/TTPs” (or a similar short placeholder).

5. Output:
   - No disclaimers or extra commentary.
   - Just the final summary in under 250 words.


TEXT TO ANALYZE:
{text}
"""
#         prompt_content = f"""
# You are a senior cybersecurity analyst. Please provide a concise summary of the threat scenario
# described below, including:
# - Key CVEs/vulnerabilities (if any)
# - Severity level
# - Targeted sector and region
# - TTPs or recommended mitigations

# Output should be plain text, max 250 words.

# TEXT:
# {text}
#         """

        human_message = HumanMessage(content=prompt_content)
        print("[+] Threat report summary being generated...")

        response = llm.invoke([human_message])
        return response.content.strip()

    except Exception as e:
        print(f"[!] Error summarizing threat report: {e}")
        return "Could not generate threat summary."


################################################################################
# Extract IoCs and TTPs (Example: uses a cost-optimized, small model)
################################################################################

def extract_iocs_ttps_gpt(
    text: str,
    openai_api_key: str = "",
    model_name: str = "gpt-4.1-2025-04-14",  
    reasoning_effort: str = "high"
):
    """
    Extract IoCs, TTPs, etc. from text. We request a JSON output.
    The new 'gpt-4.1-2025-04-14' provides optimal performance for structured outputs.
    """
    try:
        llm = get_openai_model(
            model_name=model_name,
            temperature=0.1,
            reasoning_effort=reasoning_effort,
            openai_api_key=openai_api_key
        )

        prompt_content = f"""
You are a cybersecurity analyst. Analyze the text below and extract IoCs, TTPs, plus
a recommended Sigma rule title & description.

Return a VALID JSON with structure:
{{
  "sigma_title": "...",
  "sigma_description": "...",
  "indicators_of_compromise": {{
    "ips": [],
    "domains": [],
    "urls": [],
    "email_addresses": [],
    "file_hashes": [],
    "filenames": [],
    "registry_keys": [],
    "process_names": [],
    "malicious_commands": []
  }},
  "ttps": [{{ "mitre_id": "", "technique_name": "", "description": ""}}],
  "suspicious_patterns": [],
  "process_chains": [],
  "cves": [],
  "tools_or_malware": [],
  "threat_actors": [],
  "campaigns": [],
  "malicious_execution_chains": [],
  "image_based_indicators": [],
  "obfuscations_refanged": [],
  "confidence_level": "high/medium/low",
  "notes": ""
}}

Text to analyze:
{text}
"""
        human_message = HumanMessage(content=prompt_content)
        print("[+] Extracting IoCs and TTPs (AI-based)...")
        response = llm.invoke([human_message])
        return response.content  

    except Exception as e:
        print(f"[!] Error in AI analysis: {e}")
        return "{}"


################################################################################
# Refine Sigma Queries with GPT
################################################################################

def refine_sigma_queries_with_gpt(
    sigma_yaml: str,
    splunk_queries: list,
    qradar_queries: list,
    openai_api_key: str = "",
    model_name: str = "gpt-4.1-2025-04-14",
    reasoning_effort: str = "medium"
):
    """
    Uses a smaller or mid-range model to refine Sigma, Splunk, and QRadar queries.
    """
    try:
        llm = get_openai_model(
            model_name=model_name,
            temperature=0.1,
            reasoning_effort=reasoning_effort,
            openai_api_key=openai_api_key
        )
        splunk_str = "\n".join(splunk_queries) if splunk_queries else "(No Splunk Queries)"
        qradar_str = "\n".join(qradar_queries) if qradar_queries else "(No QRadar Queries)"

        prompt_content = f"""
You are a cybersecurity expert. We have a Sigma rule in YAML plus Splunk and QRadar queries.
Refine them for clarity and completeness. Provide output in plain text with these sections:

1) Refined Sigma Rule
2) Refined Splunk Queries
3) Refined QRadar Queries

Sigma YAML:
{sigma_yaml}

Splunk queries:
{splunk_str}

QRadar queries:
{qradar_str}
"""
        human_message = HumanMessage(content=prompt_content)
        print("[+] Refining Sigma & SIEM queries with GPT...")
        response = llm.invoke([human_message])
        return response.content.strip()
    except Exception as e:
        print(f"[!] Error refining Sigma/queries with AI: {e}")
        return "Error refining output."


################################################################################
# Generate Additional Sigma Rules from Article
################################################################################

def generate_more_sigma_rules_from_article(
    article_text: str,
    images_ocr_text: str,
    openai_api_key: str = "",
    model_name: str = "gpt-4.1-2025-04-14",  # or 'o4-mini-2025-04-16' for reasoning tasks
    reasoning_effort: str = "high"
) -> str:
    """
    GPT-based function that reads an article and OCR text, then outputs extra Sigma rules in YAML.
    You might choose a bigger model if you want robust rule generation.
    """
    try:
        llm = get_openai_model(
            model_name=model_name,
            temperature=0.1,
            reasoning_effort=reasoning_effort,
            openai_api_key=openai_api_key
        )

        prompt_content = f"""
You are a seasoned cybersecurity analyst. We have an article + OCR text describing a threat scenario.
Write one or more Sigma rules in YAML to detect relevant IoCs/TTPs. Each rule:
- Title, id (placeholder is ok), status, description, references, tags, logsource, detection, fields, falsepositives, level
- If multiple rules, separate with '---' for multi-document YAML

Article text:
{article_text}

OCR text:
{images_ocr_text}
"""
        print("[+] Generating additional Sigma rule(s) from article + OCR...")
        human_message = HumanMessage(content=prompt_content)
        response = llm.invoke([human_message])
        return response.content.strip()
    except Exception as e:
        print(f"[!] Error generating extra Sigma rules: {e}")
        return "Error generating extra Sigma rules."


def convert_sigma_to_siem_queries(
    sigma_rules: str,
    openai_api_key: str = "",
    model_name: str = "gpt-4.1-2025-04-14",
    reasoning_effort: str = "high"
) -> dict:
    """
    Convert Sigma rules to SIEM queries for Splunk, QRadar, Elastic, and Microsoft Sentinel.
    Uses the latest GPT-4.1 model for optimal conversion accuracy.
    """
    try:
        llm = get_openai_model(
            model_name=model_name,
            temperature=0.1,
            reasoning_effort=reasoning_effort,
            openai_api_key=openai_api_key
        )

        prompt_content = f"""
You are an expert cybersecurity analyst specializing in SIEM query conversion. 
Convert the following Sigma rules into optimized queries for different SIEM platforms.

SIGMA RULES TO CONVERT:
{sigma_rules}

CRITICAL: You MUST respond with ONLY valid JSON. No explanations, no markdown, no code blocks, no additional text.

Required JSON format:
{{
  "splunk": {{
    "description": "Splunk SPL query optimized for performance",
    "query": "index=windows EventCode=1 | where ...",
    "notes": "Performance tips and field mappings"
  }},
  "qradar": {{
    "description": "IBM QRadar AQL query",
    "query": "SELECT * FROM events WHERE ...",
    "notes": "QRadar specific field mappings and optimizations"
  }},
  "elastic": {{
    "description": "Elasticsearch Query DSL for Elastic SIEM",
    "query": "{{'query': {{'bool': {{'must': [...]}}}}}}",
    "notes": "Elastic SIEM field mappings and index patterns"
  }},
  "sentinel": {{
    "description": "Microsoft Sentinel KQL query",
    "query": "SecurityEvent | where ...",
    "notes": "Sentinel specific tables and field mappings"
  }}
}}

IMPORTANT GUIDELINES:
1. Ensure queries are syntactically correct for each platform
2. Use appropriate field names and mappings for each SIEM
3. Optimize for performance (proper indexing, efficient filters)
4. Include relevant time ranges and event types
5. Add comments explaining complex logic
6. Handle different log sources (Windows, Linux, network, etc.)
7. Use proper escaping and syntax for each platform
8. If no Sigma rules are provided, return empty queries with appropriate messages

RESPOND WITH ONLY THE JSON OBJECT. NO OTHER TEXT.
"""

        human_message = HumanMessage(content=prompt_content)
        response = llm.invoke([human_message])
        
        # Debug: Log the response
        print(f"[DEBUG] AI Response: {response.content.strip()}")
        
        # Parse JSON response
        import json
        try:
            # Try to extract JSON from response if it's wrapped in text
            response_text = response.content.strip()
            
            # Look for JSON block in the response
            if "```json" in response_text:
                # Extract JSON from code block
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text[json_start:].strip()
            elif "```" in response_text:
                # Extract from generic code block
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text[json_start:].strip()
            else:
                # Try to find JSON object in the text
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                else:
                    json_text = response_text
            
            print(f"[DEBUG] Extracted JSON: {json_text}")
            siem_queries = json.loads(json_text)
            return siem_queries
            
        except json.JSONDecodeError as json_err:
            print(f"[DEBUG] JSON Parse Error: {json_err}")
            print(f"[DEBUG] Raw response: {response.content.strip()}")
            raise json_err
        
    except json.JSONDecodeError as e:
        print(f"[!] Error parsing SIEM queries JSON: {e}")
        # Fallback: Create basic SIEM queries from Sigma rules
        return create_fallback_siem_queries(sigma_rules)
    except Exception as e:
        print(f"[!] Error converting Sigma to SIEM queries: {e}")
        # Fallback: Create basic SIEM queries from Sigma rules
        return create_fallback_siem_queries(sigma_rules)


def create_fallback_siem_queries(sigma_rules: str) -> dict:
    """
    Create basic SIEM queries as fallback when AI conversion fails.
    """
    try:
        # Extract basic information from Sigma rules
        rules_text = sigma_rules.lower()
        
        # Basic Splunk query
        splunk_query = "index=* "
        if "process" in rules_text:
            splunk_query += "| search ProcessName=* "
        if "command" in rules_text:
            splunk_query += "| search CommandLine=* "
        if "file" in rules_text:
            splunk_query += "| search FileName=* "
        
        # Basic QRadar query
        qradar_query = "SELECT * FROM events WHERE "
        conditions = []
        if "process" in rules_text:
            conditions.append("processname IS NOT NULL")
        if "command" in rules_text:
            conditions.append("commandline IS NOT NULL")
        if conditions:
            qradar_query += " AND ".join(conditions)
        else:
            qradar_query += "1=1"
        
        # Basic Elastic query
        elastic_query = {
            "query": {
                "bool": {
                    "must": []
                }
            }
        }
        if "process" in rules_text:
            elastic_query["query"]["bool"]["must"].append({"exists": {"field": "process.name"}})
        if "command" in rules_text:
            elastic_query["query"]["bool"]["must"].append({"exists": {"field": "process.command_line"}})
        
        # Basic Sentinel query
        sentinel_query = "SecurityEvent | where "
        conditions = []
        if "process" in rules_text:
            conditions.append("ProcessName contains \"\"")
        if "command" in rules_text:
            conditions.append("CommandLine contains \"\"")
        if conditions:
            sentinel_query += " and ".join(conditions)
        else:
            sentinel_query += "1=1"
        
        return {
            "splunk": {
                "description": "Basic Splunk SPL query (fallback)",
                "query": splunk_query,
                "notes": "This is a basic query. Please customize based on your specific Sigma rule requirements."
            },
            "qradar": {
                "description": "Basic IBM QRadar AQL query (fallback)",
                "query": qradar_query,
                "notes": "This is a basic query. Please customize based on your specific Sigma rule requirements."
            },
            "elastic": {
                "description": "Basic Elasticsearch Query DSL (fallback)",
                "query": str(elastic_query).replace("'", '"'),
                "notes": "This is a basic query. Please customize based on your specific Sigma rule requirements."
            },
            "sentinel": {
                "description": "Basic Microsoft Sentinel KQL query (fallback)",
                "query": sentinel_query,
                "notes": "This is a basic query. Please customize based on your specific Sigma rule requirements."
            }
        }
    except Exception as e:
        print(f"[!] Error creating fallback SIEM queries: {e}")
        return {
            "splunk": {"description": "Error creating query", "query": "Error", "notes": str(e)},
            "qradar": {"description": "Error creating query", "query": "Error", "notes": str(e)},
            "elastic": {"description": "Error creating query", "query": "Error", "notes": str(e)},
            "sentinel": {"description": "Error creating query", "query": "Error", "notes": str(e)}
        }
