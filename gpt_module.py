from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

def extract_ttps_actors_tools_gpt(text: str, ocr_text: str = "") -> Dict:
    """Extract TTPs, Threat Actors and Tools from text using GPT-4."""
    try:
        # Combine text and OCR text if available
        full_text = text
        if ocr_text:
            full_text += "\n\nOCR Text:\n" + ocr_text

        messages = [
            SystemMessage(content="You are a cybersecurity expert specializing in threat intelligence and MITRE ATT&CK framework."),
            HumanMessage(content=f"""Analyze the following text and extract:
1. MITRE ATT&CK TTPs
2. Threat Actors
3. Tools or Malware used

Text to analyze:
{full_text}

Return the results in the following JSON format:
{{
    "ttps": [
        "list of TTPs"
    ],
    "threat_actors": [
        "list of threat actors"
    ],
    "tools_or_malware": [
        "list of tools or malware"
    ]
}}""")
        ]

        response = llm(messages)
        result = response.content
        return json.loads(result)

    except Exception as e:
        logger.error(f"Error in extract_ttps_actors_tools_gpt: {str(e)}")
        return {
            "ttps": [],
            "threat_actors": [],
            "tools_or_malware": []
        } 