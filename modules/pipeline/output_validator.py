"""
PERSEPTOR v2.0 - Output Validator
Validates and repairs AI output to ensure structural correctness.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from modules.logging_config import get_logger

logger = get_logger("output_validator")


class OutputValidator:
    """Validates and repairs AI-generated output."""

    # ─── Required fields for each output type ────────────────────────────

    IOC_REQUIRED_FIELDS = {
        "sigma_title": str,
        "sigma_description": str,
        "indicators_of_compromise": dict,
        "ttps": list,
        "tools_or_malware": list,
        "threat_actors": list,
        "confidence_level": str,
    }

    IOC_SUBFIELDS = {
        "indicators_of_compromise": [
            "ips", "domains", "urls", "email_addresses",
            "file_hashes", "filenames", "registry_keys",
            "process_names", "malicious_commands",
        ]
    }

    SIEM_REQUIRED_FIELDS = {
        "splunk": dict,
        "qradar": dict,
        "elastic": dict,
        "sentinel": dict,
    }

    SIEM_QUERY_SUBFIELDS = ["description", "query", "notes"]

    RULE_RESPONSE_FIELDS = {
        "rule": dict,
        "explanation": str,
        "test_cases": list,
        "mitre_techniques": list,
        "recommendations": list,
        "confidence_score": (int, float),
        "component_scores": dict,
    }

    # ─── Validation Methods ──────────────────────────────────────────────

    @staticmethod
    def validate_json(text: str) -> Tuple[bool, Any]:
        """Parse and validate JSON from AI response."""
        text = text.strip()

        # Try to extract JSON from code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip() if end != -1 else text[start:].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip() if end != -1 else text[start:].strip()

        # Try to find JSON object or array
        if not text.startswith(("{", "[")):
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                text = text[json_start:json_end]
            else:
                arr_start = text.find("[")
                arr_end = text.rfind("]") + 1
                if arr_start != -1 and arr_end > arr_start:
                    text = text[arr_start:arr_end]

        try:
            data = json.loads(text)
            return True, data
        except json.JSONDecodeError as e:
            logger.warning(f"JSON validation failed: {e}")
            # Attempt repair
            repaired = OutputValidator._repair_json(text)
            if repaired is not None:
                return True, repaired
            return False, None

    @staticmethod
    def _repair_json(text: str) -> Optional[Any]:
        """Attempt to repair common JSON issues from AI responses."""

        # Strategy 1: Fix invalid backslash escapes character-by-character.
        # AI often produces \Users, \System32, \AppData, \test etc.
        # Valid JSON escapes after \ are: " \ / b f n r t u
        valid_escapes = set(r'"\/bfnrtu')
        chars = list(text)
        i = 0
        while i < len(chars) - 1:
            if chars[i] == '\\':
                next_char = chars[i + 1]
                if next_char not in valid_escapes:
                    # Invalid escape like \U, \S, \P → double the backslash
                    chars.insert(i, '\\')
                    i += 2  # skip both backslashes
                else:
                    i += 2  # skip valid escape sequence
            else:
                i += 1
        repaired = ''.join(chars)

        # Strategy 2: Remove trailing commas
        repaired = re.sub(r',\s*}', '}', repaired)
        repaired = re.sub(r',\s*]', ']', repaired)

        # Strategy 3: Remove control characters
        repaired = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', repaired)

        try:
            return json.loads(repaired)
        except json.JSONDecodeError as e:
            logger.debug(f"Repair attempt 1 failed at pos {e.pos}: {e.msg}")

        # Strategy 4: Handle truncated JSON (model hit token limit)
        truncated = repaired.rstrip()
        if truncated.count('"') % 2 != 0:
            truncated += '"'
        open_braces = truncated.count('{') - truncated.count('}')
        open_brackets = truncated.count('[') - truncated.count(']')
        truncated += ']' * max(0, open_brackets)
        truncated += '}' * max(0, open_braces)

        try:
            return json.loads(truncated)
        except json.JSONDecodeError as e:
            logger.debug(f"Repair attempt 2 (truncated) failed at pos {e.pos}: {e.msg}")

        # Strategy 5: Nuclear option — strip all backslashes that aren't
        # part of \n, \t, \", \\  (lossy but better than no data)
        nuclear = re.sub(r'\\(?![nrt"\\])', '', repaired)
        try:
            return json.loads(nuclear)
        except json.JSONDecodeError as e:
            logger.warning(f"All JSON repair strategies failed at pos {e.pos}: {e.msg}")
            return None

    @classmethod
    def validate_ioc_response(cls, data: dict) -> Tuple[bool, dict, List[str]]:
        """Validate IoC extraction response and fill missing fields."""
        warnings = []

        # Ensure required top-level fields
        for field, field_type in cls.IOC_REQUIRED_FIELDS.items():
            if field not in data:
                warnings.append(f"Missing field '{field}', added default")
                if field_type == str:
                    data[field] = ""
                elif field_type == list:
                    data[field] = []
                elif field_type == dict:
                    data[field] = {}

        # Ensure IoC subfields
        ioc = data.get("indicators_of_compromise", {})
        for subfield in cls.IOC_SUBFIELDS.get("indicators_of_compromise", []):
            if subfield not in ioc:
                ioc[subfield] = []
                warnings.append(f"Missing IoC field '{subfield}', added empty list")
        data["indicators_of_compromise"] = ioc

        # Validate TTPs structure
        valid_ttps = []
        for ttp in data.get("ttps", []):
            if isinstance(ttp, dict) and "mitre_id" in ttp:
                valid_ttps.append(ttp)
            elif isinstance(ttp, str):
                valid_ttps.append({
                    "mitre_id": ttp if ttp.startswith("T") else "",
                    "technique_name": ttp,
                    "description": "",
                })
        data["ttps"] = valid_ttps

        # Validate confidence level
        if data.get("confidence_level") not in ("high", "medium", "low"):
            data["confidence_level"] = "medium"
            warnings.append("Invalid confidence_level, defaulted to 'medium'")

        is_valid = len(warnings) == 0
        return is_valid, data, warnings

    @classmethod
    def validate_siem_response(cls, data: dict) -> Tuple[bool, dict, List[str]]:
        """Validate SIEM query conversion response."""
        warnings = []

        for platform, field_type in cls.SIEM_REQUIRED_FIELDS.items():
            if platform not in data:
                data[platform] = {
                    "description": f"{platform} query (missing from response)",
                    "query": "ERROR: Query not generated",
                    "notes": "AI response did not include this platform",
                }
                warnings.append(f"Missing platform '{platform}', added placeholder")
            else:
                for subfield in cls.SIEM_QUERY_SUBFIELDS:
                    if subfield not in data[platform]:
                        data[platform][subfield] = ""
                        warnings.append(f"Missing '{platform}.{subfield}'")

        is_valid = len(warnings) == 0
        return is_valid, data, warnings

    @classmethod
    def validate_rule_response(cls, data: dict) -> Tuple[bool, dict, List[str]]:
        """Validate rule generation response."""
        warnings = []

        for field, field_type in cls.RULE_RESPONSE_FIELDS.items():
            if field not in data:
                warnings.append(f"Missing field '{field}', added default")
                if field_type == str:
                    data[field] = ""
                elif field_type == list:
                    data[field] = []
                elif field_type == dict:
                    data[field] = {}
                elif field_type in ((int, float),):
                    data[field] = 0.0

        # Validate confidence score range
        if "confidence_score" in data:
            score = data["confidence_score"]
            if isinstance(score, (int, float)):
                if score > 1:
                    data["confidence_score"] = score / 100.0
                data["confidence_score"] = max(0.0, min(1.0, data["confidence_score"]))
            else:
                data["confidence_score"] = 0.5
                warnings.append("Invalid confidence_score type, defaulted to 0.5")

        # Validate component scores
        if "component_scores" in data and isinstance(data["component_scores"], dict):
            for key in ["detection_quality", "false_positive_risk", "coverage", "maintainability"]:
                if key not in data["component_scores"]:
                    data["component_scores"][key] = 0.5
                    warnings.append(f"Missing component_score '{key}'")
                else:
                    val = data["component_scores"][key]
                    if isinstance(val, (int, float)):
                        if val > 1:
                            data["component_scores"][key] = val / 100.0
                        data["component_scores"][key] = max(0.0, min(1.0, data["component_scores"][key]))

        is_valid = len(warnings) == 0
        return is_valid, data, warnings

    @staticmethod
    def validate_sigma_yaml(yaml_text: str) -> Tuple[bool, List[str]]:
        """Basic validation of Sigma rule YAML."""
        warnings = []
        required_fields = ["title", "logsource", "detection", "level"]

        for field in required_fields:
            if f"{field}:" not in yaml_text:
                warnings.append(f"Missing required Sigma field: {field}")

        # Check for valid level
        if "level:" in yaml_text:
            level_match = re.search(r"level:\s*(\w+)", yaml_text)
            if level_match:
                level = level_match.group(1).lower()
                if level not in ("informational", "low", "medium", "high", "critical"):
                    warnings.append(f"Invalid level '{level}'")

        is_valid = len(warnings) == 0
        return is_valid, warnings
