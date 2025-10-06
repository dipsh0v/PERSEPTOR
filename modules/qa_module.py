import json
import yaml
import uuid
import os
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from .ui_module import print_colored, print_rule, print_table, print_panel

class ConfidenceVisualizer:
    def __init__(self):
        self.bar_length = 30
        self.colors = {
            "high": "green",
            "medium": "yellow",
            "low": "red"
        }
    
    def _get_color(self, score: float) -> str:
        """Get color based on score."""
        if score >= 0.8:
            return self.colors["high"]
        elif score >= 0.5:
            return self.colors["medium"]
        return self.colors["low"]
    
    def _create_bar(self, score: float) -> str:
        """Create a progress bar for the score."""
        filled_length = int(self.bar_length * score)
        bar = "█" * filled_length + "░" * (self.bar_length - filled_length)
        return bar
    
    def _create_radar_chart(self, scores: Dict[str, float], weights: Dict[str, float], explanations: Dict[str, str]) -> str:
        """Create an ASCII radar chart for the scores."""
        chart = []
        max_length = max(len(name) for name in scores.keys())
        
        # Create header
        chart.append(" " * (max_length + 2) + "Confidence Radar")
        chart.append(" " * (max_length + 2) + "─" * 20)
        
        # Create radar lines
        for name, score in scores.items():
            bar = self._create_bar(score)
            weight_str = f"({weights[name]*100:.0f}%)"
            explanation = explanations[name].split(" | ")[0] if explanations[name] else ""
            name_padded = name.replace("_", " ").title().ljust(max_length)
            chart.append(f"{name_padded} {bar} {score*100:5.1f}% {weight_str} ({explanation})")
        
        return "\n".join(chart)
    
    def _create_score_summary(self, overall_score: float) -> str:
        """Create a summary box for the overall score."""
        color = self._get_color(overall_score)
        bar = self._create_bar(overall_score)
        
        summary = [
            "┌" + "─" * (self.bar_length + 10) + "┐",
            "│ Overall Confidence Score".ljust(self.bar_length + 10) + "│",
            "│ " + bar + f" {overall_score*100:5.1f}% │",
            "└" + "─" * (self.bar_length + 10) + "┘"
        ]
        
        return "\n".join(summary)
    
    def visualize_confidence(self, confidence_result: Dict) -> None:
        """Visualize the confidence scores."""
        # Print overall score
        print_rule("Confidence Visualization")
        print_colored(
            self._create_score_summary(confidence_result["overall_score"]),
            self._get_color(confidence_result["overall_score"])
        )
        print()
        
        # Print radar chart with explanations
        print_rule("Component Analysis")
        print_colored(
            self._create_radar_chart(
                confidence_result["component_scores"],
                confidence_result["weights"],
                confidence_result["explanations"]
            ),
            "white"
        )
        print()

class RuleConfidenceCalculator:
    def __init__(self):
        self.algorithms = {
            "complexity": self._calculate_complexity_score,
            "coverage": self._calculate_coverage_score,
            "specificity": self._calculate_specificity_score,
            "mitre_alignment": self._calculate_mitre_alignment_score,
            "test_case_coverage": self._calculate_test_case_score,
            "rule_quality": self._calculate_rule_quality_score,
            "false_positive_risk": self._calculate_false_positive_risk
        }
        self.visualizer = ConfidenceVisualizer()
        
    def _calculate_complexity_score(self, rule: Dict) -> Tuple[float, str]:
        """Calculate score based on rule complexity and structure."""
        score = 1.0
        explanation = []
        
        if "detection" in rule:
            detection = rule["detection"]
            
            # Check number of conditions
            conditions = len(detection.get("condition", "").split(" and "))
            if conditions > 5:
                score *= 0.7
                explanation.append(f"Too many conditions ({conditions})")
            elif conditions > 3:
                score *= 0.85
                explanation.append(f"Many conditions ({conditions})")
            else:
                score *= 0.95
                explanation.append(f"Reasonable number of conditions ({conditions})")
            
            # Check for complex patterns
            complex_patterns = 0
            for value in detection.values():
                if isinstance(value, str):
                    if "|" in value:
                        complex_patterns += 1
                    if "(" in value:
                        complex_patterns += 1
                    if "*" in value:
                        complex_patterns += 1
                    if "?" in value:
                        complex_patterns += 1
            
            if complex_patterns > 3:
                score *= 0.7
                explanation.append(f"Too many complex patterns ({complex_patterns})")
            elif complex_patterns > 1:
                score *= 0.85
                explanation.append(f"Several complex patterns ({complex_patterns})")
            
            # Check for nested conditions
            nested_level = 0
            for value in detection.values():
                if isinstance(value, str):
                    nested_level = max(nested_level, value.count("("))
            
            if nested_level > 2:
                score *= 0.7
                explanation.append(f"Deep nesting ({nested_level} levels)")
            elif nested_level > 0:
                score *= 0.9
                explanation.append(f"Some nesting ({nested_level} levels)")
        
        return score, " | ".join(explanation)
    
    def _calculate_coverage_score(self, rule: Dict) -> Tuple[float, str]:
        """Calculate score based on rule coverage and scope."""
        score = 1.0
        explanation = []
        
        # Check log source coverage
        if "logsource" in rule:
            logsource = rule["logsource"]
            if "product" in logsource and "category" in logsource:
                score *= 0.95
                explanation.append("Specific product and category defined")
            elif "product" in logsource or "category" in logsource:
                score *= 0.85
                explanation.append("Partial log source definition")
            else:
                score *= 0.7
                explanation.append("Missing log source definition")
        
        # Check detection fields
        if "detection" in rule:
            detection = rule["detection"]
            field_count = sum(1 for k in detection.keys() if k != "condition")
            
            if field_count < 2:
                score *= 0.7
                explanation.append(f"Insufficient detection fields ({field_count})")
            elif field_count < 4:
                score *= 0.85
                explanation.append(f"Limited detection fields ({field_count})")
            else:
                score *= 0.95
                explanation.append(f"Good field coverage ({field_count})")
        
        return score, " | ".join(explanation)
    
    def _calculate_specificity_score(self, rule: Dict) -> Tuple[float, str]:
        """Calculate score based on rule specificity and precision."""
        score = 1.0
        explanation = []
        
        if "detection" in rule:
            detection = rule["detection"]
            
            # Check for specific values vs wildcards
            specific_values = 0
            wildcard_values = 0
            total_values = 0
            
            for value in detection.values():
                if isinstance(value, str):
                    total_values += 1
                    if "*" in value or "?" in value:
                        wildcard_values += 1
                    else:
                        specific_values += 1
            
            if total_values > 0:
                ratio = specific_values / total_values
                if ratio < 0.3:
                    score *= 0.7
                    explanation.append(f"Low specificity ratio ({ratio:.2f})")
                elif ratio < 0.6:
                    score *= 0.85
                    explanation.append(f"Moderate specificity ratio ({ratio:.2f})")
                else:
                    score *= 0.95
                    explanation.append(f"High specificity ratio ({ratio:.2f})")
            
            # Check for common false positive patterns
            false_positive_patterns = [
                "cmd.exe", "powershell.exe", "explorer.exe",
                "svchost.exe", "system32", "temp"
            ]
            
            for pattern in false_positive_patterns:
                if any(pattern.lower() in str(v).lower() for v in detection.values()):
                    score *= 0.9
                    explanation.append(f"Contains common false positive pattern: {pattern}")
        
        return score, " | ".join(explanation)
    
    def _calculate_mitre_alignment_score(self, rule: Dict) -> Tuple[float, str]:
        """Calculate score based on MITRE ATT&CK technique alignment."""
        score = 1.0
        explanation = []
        
        if "tags" in rule:
            mitre_tags = [tag for tag in rule["tags"] if tag.startswith("attack.")]
            if not mitre_tags:
                score *= 0.7
                explanation.append("No MITRE technique alignment")
            else:
                # Check for specific technique vs tactic alignment
                specific_techniques = sum(1 for tag in mitre_tags if "." in tag.split(".")[-1])
                if specific_techniques > 0:
                    score *= 0.95
                    explanation.append(f"Aligned with {specific_techniques} specific techniques")
                else:
                    score *= 0.85
                    explanation.append("Only tactic-level alignment")
        else:
            score *= 0.7
            explanation.append("Missing MITRE tags")
        
        return score, " | ".join(explanation)
    
    def _calculate_test_case_score(self, rule: Dict, test_cases: List[Dict]) -> Tuple[float, str]:
        """Calculate score based on test case coverage."""
        if not test_cases:
            return 0.7, "No test cases provided"
        
        score = 1.0
        explanation = []
        
        # Check test case coverage
        test_case_count = len(test_cases)
        if test_case_count < 2:
            score *= 0.7
            explanation.append(f"Insufficient test cases ({test_case_count})")
        elif test_case_count < 4:
            score *= 0.85
            explanation.append(f"Limited test cases ({test_case_count})")
        else:
            score *= 0.95
            explanation.append(f"Good test case coverage ({test_case_count})")
        
        # Check test case quality
        detailed_cases = sum(1 for case in test_cases if len(case.get("description", "")) > 50)
        if detailed_cases == 0:
            score *= 0.8
            explanation.append("No detailed test cases")
        elif detailed_cases < test_case_count / 2:
            score *= 0.9
            explanation.append(f"Some detailed test cases ({detailed_cases})")
        
        # Check for positive and negative test cases
        has_positive = any("expected_result" in case for case in test_cases)
        has_negative = any("false_positive" in case.get("description", "").lower() for case in test_cases)
        
        if not has_positive:
            score *= 0.8
            explanation.append("Missing positive test cases")
        if not has_negative:
            score *= 0.9
            explanation.append("Missing negative test cases")
        
        return score, " | ".join(explanation)
    
    def _calculate_rule_quality_score(self, rule: Dict) -> Tuple[float, str]:
        """Calculate score based on overall rule quality."""
        score = 1.0
        explanation = []
        
        # Check required fields
        required_fields = ["title", "description", "author", "date", "detection"]
        missing_fields = [field for field in required_fields if field not in rule]
        if missing_fields:
            score *= 0.8
            explanation.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Check description quality
        if "description" in rule:
            desc_length = len(rule["description"])
            if desc_length < 50:
                score *= 0.8
                explanation.append("Description too short")
            elif desc_length > 500:
                score *= 0.9
                explanation.append("Description too long")
        
        # Check for proper formatting
        if "detection" in rule:
            detection = rule["detection"]
            if not any(isinstance(v, (str, list, dict)) for v in detection.values()):
                score *= 0.7
                explanation.append("Invalid detection field types")
        
        return score, " | ".join(explanation)
    
    def _calculate_false_positive_risk(self, rule: Dict) -> Tuple[float, str]:
        """
        Calculate score based on false positive risk assessment.
        Uses industry best practices and common false positive patterns.
        """
        score = 1.0
        explanation = []
        risk_factors = []
        
        if "detection" in rule:
            detection = rule["detection"]
            
            # 1. Check for high-risk patterns that commonly cause false positives
            high_risk_patterns = {
                # Common system processes that are often legitimate
                "process": [
                    "svchost.exe", "explorer.exe", "system", "lsass.exe",
                    "winlogon.exe", "csrss.exe", "smss.exe", "services.exe",
                    "spoolsv.exe", "wininit.exe", "conhost.exe", "dllhost.exe",
                    "rundll32.exe", "regsvr32.exe", "mshta.exe", "wscript.exe",
                    "cscript.exe", "powershell.exe", "cmd.exe", "taskhost.exe"
                ],
                # Common system paths that are often legitimate
                "path": [
                    "system32", "program files", "windows", "temp",
                    "appdata", "users", "programdata", "inetpub",
                    "programdata", "common files", "microsoft", "syswow64"
                ],
                # Common legitimate file extensions
                "extension": [
                    ".exe", ".dll", ".sys", ".bat", ".cmd", ".ps1",
                    ".vbs", ".js", ".wsf", ".hta", ".lnk", ".url"
                ],
                # Common legitimate registry paths
                "registry": [
                    "HKLM\\SOFTWARE", "HKLM\\SYSTEM", "HKCU\\SOFTWARE",
                    "HKLM\\SOFTWARE\\Microsoft", "HKLM\\SYSTEM\\CurrentControlSet"
                ],
                # Common legitimate network patterns
                "network": [
                    "127.0.0.1", "localhost", "0.0.0.0", "255.255.255.255",
                    "169.254.", "224.0.0.", "239.255.255.", "ff02::"
                ]
            }
            
            # 2. Check for broad patterns that increase false positive risk
            broad_patterns = {
                "regex": [
                    ".*", ".*?", ".+", ".+?", ".*\\.", ".*\\.",
                    "\\d+", "\\w+", "[a-zA-Z]+", "[0-9]+", ".*\\..*",
                    ".*\\.exe", ".*\\.dll", ".*\\.sys"
                ],
                "wildcards": [
                    "*", "?", "**", "*.*", "*.exe", "*.dll", "*.sys",
                    "*\\*", "*\\*\\*", "*\\*\\*\\*"
                ]
            }
            
            # 3. Check for common legitimate activities
            legitimate_activities = {
                "scheduled_tasks": [
                    "schtasks", "at.exe", "task scheduler",
                    "scheduled task", "scheduled job"
                ],
                "system_updates": [
                    "windows update", "microsoft update",
                    "wsus", "windows defender update"
                ],
                "antivirus": [
                    "windows defender", "antivirus", "security scan",
                    "malware scan", "virus scan"
                ],
                "system_maintenance": [
                    "disk cleanup", "system maintenance",
                    "windows maintenance", "system check"
                ]
            }
            
            # Analyze detection fields for risks
            for field, value in detection.items():
                if field == "condition":
                    continue
                    
                value_str = str(value).lower()
                
                # Check high-risk patterns
                for category, patterns in high_risk_patterns.items():
                    for pattern in patterns:
                        if pattern.lower() in value_str:
                            score *= 0.9
                            risk_factors.append(f"Contains {category} pattern: {pattern}")
                
                # Check broad patterns
                for category, patterns in broad_patterns.items():
                    for pattern in patterns:
                        if pattern in value_str:
                            score *= 0.85
                            risk_factors.append(f"Contains broad {category} pattern: {pattern}")
                
                # Check legitimate activities
                for category, activities in legitimate_activities.items():
                    for activity in activities:
                        if activity.lower() in value_str:
                            score *= 0.9
                            risk_factors.append(f"Matches legitimate {category}: {activity}")
            
            # 4. Check for common false positive scenarios
            false_positive_scenarios = {
                "process_creation": [
                    "parent_process", "command_line", "image",
                    "process_name", "process_path"
                ],
                "file_operations": [
                    "file_path", "file_name", "file_extension",
                    "file_hash", "file_size"
                ],
                "network_activity": [
                    "destination_ip", "destination_port",
                    "source_ip", "source_port", "protocol"
                ],
                "registry_operations": [
                    "registry_path", "registry_key",
                    "registry_value", "registry_data"
                ]
            }
            
            # Check if rule matches common false positive scenarios
            for scenario, fields in false_positive_scenarios.items():
                if any(field in detection for field in fields):
                    score *= 0.95
                    risk_factors.append(f"Matches {scenario} scenario")
            
            # 5. Check for rule complexity that might increase false positive risk
            if "condition" in detection:
                condition = detection["condition"]
                if " or " in condition:
                    score *= 0.9
                    risk_factors.append("Uses OR conditions")
                if condition.count(" and ") > 2:
                    score *= 0.95
                    risk_factors.append("Multiple AND conditions")
            
            # Add the most significant risk factors to the explanation
            if risk_factors:
                # Sort risk factors by severity (broad patterns first, then specific ones)
                risk_factors.sort(key=lambda x: (
                    "broad" in x.lower(),
                    "pattern" in x.lower(),
                    "legitimate" in x.lower()
                ))
                explanation.append(" | ".join(risk_factors[:3]))  # Show top 3 risk factors
        
        return score, " | ".join(explanation) if explanation else "No significant risks detected"
    
    def calculate_confidence(self, rule: Dict, test_cases: List[Dict] = None) -> Dict:
        """Calculate overall confidence score using multiple algorithms."""
        scores = {}
        explanations = {}
        
        # Calculate individual scores
        for name, algorithm in self.algorithms.items():
            if name == "test_case_coverage":
                score, explanation = algorithm(rule, test_cases or [])
            else:
                score, explanation = algorithm(rule)
            scores[name] = score
            explanations[name] = explanation
        
        # Calculate weighted average with updated weights
        weights = {
            "complexity": 0.15,
            "coverage": 0.15,
            "specificity": 0.15,
            "mitre_alignment": 0.10,
            "test_case_coverage": 0.15,
            "rule_quality": 0.15,
            "false_positive_risk": 0.15
        }
        
        final_score = sum(scores[k] * weights[k] for k in weights.keys())
        final_score = min(1.0, max(0.0, final_score))  # Ensure score is between 0 and 1
        
        result = {
            "overall_score": final_score,
            "component_scores": scores,
            "explanations": explanations,
            "weights": weights
        }
        
        # Visualize the results
        self.visualizer.visualize_confidence(result)
        
        return result

class SigmaQA:
    def __init__(self, openai_api_key: str = "", model_name: str = "gpt-4.1-2025-04-14"):
        """
        Initialize the Q&A system.
        
        Args:
            openai_api_key: OpenAI API key
            model_name: Model to use for Q&A (default: o1)
        """
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=openai_api_key
        )
        self.confidence_calculator = RuleConfidenceCalculator()
        
        # Example queries for different products
        self.example_queries = {
            "sigma": [
                "Create a Sigma rule to detect suspicious PowerShell script execution with base64 encoding",
                "Generate a Sigma rule for detecting potential ransomware activity in file operations",
                "Make a Sigma rule for detecting unauthorized access attempts in authentication logs",
                "Create a Sigma rule for detecting data exfiltration attempts through network connections"
            ],
            "yara": [
                "Create a YARA rule to detect malicious PowerShell scripts with obfuscation",
                "Generate a YARA rule for identifying ransomware file patterns",
                "Make a YARA rule for detecting common malware droppers",
                "Create a YARA rule for identifying suspicious document macros"
            ],
            "splunk": [
                "Create a Splunk query to detect lateral movement through SMB",
                "Generate a Splunk query for identifying suspicious scheduled tasks",
                "Make a Splunk query for detecting unusual outbound connections",
                "Create a Splunk query for monitoring sensitive file access"
            ],
            "qradar": [
                "Create a QRadar rule to detect brute force login attempts",
                "Generate a QRadar rule for identifying data exfiltration",
                "Make a QRadar rule for detecting suspicious DNS queries",
                "Create a QRadar rule for monitoring privileged account usage"
            ]
        }

    def _validate_reference(self, url: str) -> bool:
        """
        Validate if a reference URL is accessible.
        
        Args:
            url: URL to validate
        
        Returns:
            bool: True if URL is accessible, False otherwise
        """
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False

    def _validate_references(self, references: List[Dict]) -> List[Dict]:
        """
        Validate a list of references and return only valid ones.
        
        Args:
            references: List of reference dictionaries
        
        Returns:
            List[Dict]: List of valid references
        """
        valid_references = []
        for ref in references:
            if "url" in ref and self._validate_reference(ref["url"]):
                valid_references.append(ref)
        return valid_references

    def _generate_response(self, query: str, product: str = "sigma") -> Dict:
        """
        Generate a response based on the query and product.
        
        Args:
            query: Natural language query
            product: Target product (sigma, yara, splunk, qradar)
        """
        prompt = f"""
You are a cybersecurity expert specializing in {product.upper()} rules and threat detection.
Create a comprehensive response based on the following query. The response should be detailed and actionable.

Query: {query}
Product: {product.upper()}

Return the response in the following JSON format:
{{
    "rule": {{
        // Product-specific rule format
        "title": "Rule title",
        "description": "Detailed description",
        "author": "Aytek Aytemur",
        "date": "{datetime.now().strftime('%Y/%m/%d')}",
        // Additional product-specific fields
    }},
    "explanation": "Detailed explanation of the rule and its components",
    "test_cases": [
        {{
            "name": "Test case name",
            "description": "Test case description",
            "expected_result": "Expected detection result"
        }}
    ],
    "confidence_score": 0.95,
    "mitre_techniques": [
        {{
            "id": "T1234",
            "name": "Technique Name",
            "description": "Description"
        }}
    ],
    "recommendations": [
        "Additional security recommendations",
        "Best practices for implementation",
        "Potential false positive scenarios"
    ],
    "references": [
        {{
            "title": "Reference title",
            "url": "Reference URL",
            "description": "Reference description"
        }}
    ]
}}
"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Clean the response content to handle escape characters
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            # Clean up any remaining escape characters and control characters
            content = content.replace("\\n", "\n").replace("\\t", "\t").replace("\\\"", "\"")
            
            # Remove control characters that cause JSON parsing issues
            import re
            content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
            
            # Try to find JSON object boundaries
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                content = content[start_idx:end_idx + 1]
            
            result = json.loads(content)
            
            # Validate references
            if "references" in result:
                result["references"] = self._validate_references(result["references"])
            
            return result
        except Exception as e:
            print(f"Error generating response: {e}")
            return {}

    def save_rule(self, rule: Dict, product: str, filename: str = None) -> str:
        """
        Save a rule to a file.
        
        Args:
            rule: The rule to save
            product: Product type (sigma, yara, splunk, qradar)
            filename: Optional filename
        
        Returns:
            str: Path to the saved file
        """
        try:
            if not filename:
                title = rule.get("title", "untitled").lower().replace(" ", "_")
                filename = f"{product}_rule_{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            
            # Create rules directory in the current workspace
            rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"{product}_rules")
            os.makedirs(rules_dir, exist_ok=True)
            
            filepath = os.path.join(rules_dir, filename)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                yaml.dump(rule, f, sort_keys=False, allow_unicode=True)
            
            return filepath
        except Exception as e:
            print_colored(f"Error saving rule: {str(e)}", "red")
            return None

    def display_examples(self, product: str = None):
        """
        Display example queries for the specified product or all products.
        
        Args:
            product: Optional product to show examples for
        """
        if product and product in self.example_queries:
            print_rule(f"Example {product.upper()} Queries")
            for i, query in enumerate(self.example_queries[product], 1):
                print_panel(query, title=f"Example {i}")
        else:
            for prod, queries in self.example_queries.items():
                print_rule(f"Example {prod.upper()} Queries")
                for i, query in enumerate(queries, 1):
                    print_panel(query, title=f"Example {i}")

    def process_query(self, query: str, product: str = "sigma") -> None:
        """
        Process a natural language query and generate appropriate rules.
        
        Args:
            query: Natural language query
            product: Target product (sigma, yara, splunk, qradar)
        """
        print_rule("Processing Query")
        print_panel(query, title="Input Query")
        
        # Generate response
        result = self._generate_response(query, product)
        if not result:
            print_colored("Failed to generate response.", "red")
            return

        # Display the rule
        print_rule(f"Generated {product.upper()} Rule")
        rule = result.get("rule", {})
        
        # Format the rule as proper YAML
        yaml_output = yaml.dump(rule, sort_keys=False, allow_unicode=True, default_flow_style=False)
        print_panel(yaml_output, title="Rule Content")

        # Display explanation
        if "explanation" in result:
            print_rule("Rule Explanation")
            print_panel(result["explanation"], title="Detailed Explanation")

        # Display test cases
        test_cases = result.get("test_cases", [])
        if test_cases:
            print_rule("Test Cases")
            for test_case in test_cases:
                print_panel(
                    f"Description: {test_case['description']}\n"
                    f"Expected Result: {test_case['expected_result']}",
                    title=test_case["name"]
                )

        # Display MITRE techniques
        if "mitre_techniques" in result:
            print_rule("MITRE ATT&CK Techniques")
            for technique in result["mitre_techniques"]:
                print_panel(
                    f"Description: {technique['description']}",
                    title=f"{technique['id']}: {technique['name']}"
                )

        # Display recommendations
        if "recommendations" in result:
            print_rule("Recommendations")
            for i, rec in enumerate(result["recommendations"], 1):
                print_panel(rec, title=f"Recommendation {i}")

        # Display references (only if there are valid ones)
        if "references" in result and result["references"]:
            print_rule("References")
            for ref in result["references"]:
                print_panel(
                    f"URL: {ref['url']}\nDescription: {ref['description']}",
                    title=ref["title"]
                )

        # Calculate and display confidence score with visualization
        confidence_result = self.confidence_calculator.calculate_confidence(rule, test_cases)

        # Ask user if they want to save the rule
        save_choice = input("\nWould you like to save this rule? (y/n): ").lower()
        if save_choice == 'y':
            filepath = self.save_rule(rule, product)
            if filepath:
                print_rule("Rule Saved")
                print_panel(filepath, title="Saved File Path")
            else:
                print_colored("Failed to save rule.", "red")
        else:
            print_colored("Rule not saved.", "yellow")

def create_qa_system(openai_api_key: str = "", model_name: str = "gpt-4.1-2025-04-14") -> SigmaQA:
    """
    Create a new Q&A system instance. 
    
    Args:
        openai_api_key: OpenAI API key
        model_name: Model to use for Q&A (default: o1)
    
    Returns:
        SigmaQA: A new Q&A system instance
    """
    return SigmaQA(openai_api_key=openai_api_key, model_name=model_name)