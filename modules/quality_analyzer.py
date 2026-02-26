import json
import yaml
import uuid
import os
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple
from modules.ai.base_provider import AIProvider, Message
from modules.ai.provider_factory import get_provider
from modules.ai.retry_handler import with_retry
from modules.logging_config import get_logger
from .cli_formatter import print_colored, print_rule, print_table, print_panel

logger = get_logger("quality_analyzer")

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

class RuleMaturityAssessor:
    """Assess rule maturity level based on multiple criteria."""

    MATURITY_LEVELS = {
        "production": {"min_score": 0.85, "label": "Production Ready", "color": "green"},
        "testing": {"min_score": 0.70, "label": "Testing Phase", "color": "cyan"},
        "experimental": {"min_score": 0.50, "label": "Experimental", "color": "yellow"},
        "draft": {"min_score": 0.0, "label": "Draft", "color": "red"},
    }

    @staticmethod
    def assess(rule: Dict, confidence_score: float, test_cases: List = None) -> Dict:
        """Assess rule maturity and return level + recommendations."""
        criteria = {
            "has_description": bool(rule.get("description", "")) and len(rule.get("description", "")) > 20,
            "has_author": bool(rule.get("author")),
            "has_date": bool(rule.get("date")),
            "has_tags": bool(rule.get("tags")) and len(rule.get("tags", [])) > 0,
            "has_detection": bool(rule.get("detection")),
            "has_logsource": bool(rule.get("logsource")),
            "has_falsepositives": bool(rule.get("falsepositives")),
            "has_level": bool(rule.get("level")),
            "has_test_cases": bool(test_cases) and len(test_cases) >= 2,
            "confidence_above_70": confidence_score >= 0.70,
        }

        met_count = sum(criteria.values())
        total = len(criteria)
        maturity_score = met_count / total

        # Determine maturity level
        level = "draft"
        for lvl, info in RuleMaturityAssessor.MATURITY_LEVELS.items():
            if maturity_score >= info["min_score"]:
                level = lvl
                break

        # Generate recommendations for missing criteria
        recommendations = []
        if not criteria["has_description"]:
            recommendations.append("Add a detailed description (>20 chars)")
        if not criteria["has_tags"]:
            recommendations.append("Add MITRE ATT&CK tags (e.g., attack.execution)")
        if not criteria["has_falsepositives"]:
            recommendations.append("Document known false positive scenarios")
        if not criteria["has_test_cases"]:
            recommendations.append("Add at least 2 test cases (positive + negative)")
        if not criteria["confidence_above_70"]:
            recommendations.append("Improve detection logic to raise confidence above 70%")

        return {
            "level": level,
            "label": RuleMaturityAssessor.MATURITY_LEVELS[level]["label"],
            "maturity_score": round(maturity_score, 2),
            "criteria_met": met_count,
            "criteria_total": total,
            "criteria": criteria,
            "recommendations": recommendations,
        }


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
        self.maturity_assessor = RuleMaturityAssessor()
        
    @staticmethod
    def _count_detection_strings(obj) -> list:
        """Recursively extract all string values from detection dict/list."""
        strings = []
        if isinstance(obj, str):
            strings.append(obj)
        elif isinstance(obj, list):
            for item in obj:
                strings.extend(RuleConfidenceCalculator._count_detection_strings(item))
        elif isinstance(obj, dict):
            for v in obj.values():
                strings.extend(RuleConfidenceCalculator._count_detection_strings(v))
        return strings

    def _calculate_complexity_score(self, rule: Dict) -> Tuple[float, str]:
        """Calculate score based on rule complexity and structure."""
        score = 1.0
        explanation = []

        if "detection" in rule:
            detection = rule["detection"]
            condition = detection.get("condition", "")

            # Parse condition properly — count distinct logical operators
            operators = {
                "and": len(re.findall(r'\band\b', condition, re.IGNORECASE)),
                "or": len(re.findall(r'\bor\b', condition, re.IGNORECASE)),
                "not": len(re.findall(r'\bnot\b', condition, re.IGNORECASE)),
                "1_of": len(re.findall(r'\b1 of\b', condition, re.IGNORECASE)),
                "all_of": len(re.findall(r'\ball of\b', condition, re.IGNORECASE)),
            }
            total_ops = sum(operators.values())

            if total_ops > 5:
                score *= 0.7
                explanation.append(f"\u26a0 Condition too complex ({total_ops} operators) \u2014 harder to maintain and debug")
            elif total_ops > 3:
                score *= 0.85
                explanation.append(f"\u26a1 Moderately complex condition ({total_ops} operators)")
            elif total_ops >= 1:
                score *= 0.95
                explanation.append(f"\u2713 Well-structured \u2014 {total_ops} logical operator(s) in condition")
            else:
                # Only "selection" with no operators — too simple
                score *= 0.90
                explanation.append(f"\u26a1 Simple condition without aggregation \u2014 consider adding filters or exclusions")

            # Check for complex patterns in all detection values (recursive)
            all_strings = self._count_detection_strings(detection)
            complex_patterns = 0
            for value_str in all_strings:
                if "|" in value_str: complex_patterns += 1
                if "(" in value_str: complex_patterns += 1
                if "*" in value_str: complex_patterns += 1
                if "?" in value_str: complex_patterns += 1

            if complex_patterns > 6:
                score *= 0.7
                explanation.append(f"\u26a0 Too many wildcards/regex ({complex_patterns}) \u2014 risk of false positives")
            elif complex_patterns > 3:
                score *= 0.85
                explanation.append(f"\u26a1 Several complex patterns ({complex_patterns} wildcards/regex)")
            elif complex_patterns > 0:
                explanation.append(f"\u2713 Acceptable pattern complexity ({complex_patterns})")

            # Check for nested conditions
            nested_level = 0
            for value in all_strings:
                nested_level = max(nested_level, value.count("("))

            if nested_level > 2:
                score *= 0.7
                explanation.append(f"\u26a0 Deeply nested logic ({nested_level} levels) \u2014 difficult to troubleshoot")
            elif nested_level > 0:
                score *= 0.9
                explanation.append(f"\u26a1 Some nesting ({nested_level} level(s))")
        else:
            score *= 0.5
            explanation.append("\u26a0 No detection block found \u2014 rule cannot function")

        return score, " | ".join(explanation)
    
    def _calculate_coverage_score(self, rule: Dict) -> Tuple[float, str]:
        """Calculate score based on rule coverage and scope."""
        score = 1.0
        explanation = []

        # Check log source coverage
        if "logsource" in rule:
            logsource = rule["logsource"]
            has_product = bool(logsource.get("product"))
            has_category = bool(logsource.get("category"))
            has_service = bool(logsource.get("service"))

            if has_product and has_category:
                score *= 0.95
                explanation.append("\u2713 Log source well-defined \u2014 product and category specified")
            elif has_product and has_service:
                score *= 0.93
                explanation.append("\u2713 Log source defined \u2014 product and service specified")
            elif has_product or has_category:
                score *= 0.85
                explanation.append("\u26a1 Partial log source \u2014 only product or category specified, not both")
            else:
                score *= 0.7
                explanation.append("\u26a0 Missing log source details \u2014 rule may not trigger on the correct event type")
        else:
            score *= 0.6
            explanation.append("\u26a0 No logsource block \u2014 rule won't route to any event type")

        # Check detection fields and value richness
        if "detection" in rule:
            detection = rule["detection"]
            field_count = sum(1 for k in detection.keys() if k != "condition")

            # Count total unique detection values (recursive)
            all_values = self._count_detection_strings(detection)
            value_count = len(all_values)

            if field_count < 2:
                score *= 0.7
                explanation.append(f"\u26a0 Only {field_count} detection field(s) \u2014 minimal coverage, easy to evade")
            elif field_count < 4:
                score *= 0.85
                explanation.append(f"\u26a1 {field_count} detection fields \u2014 consider adding more data points")
            else:
                score *= 0.95
                explanation.append(f"\u2713 Good detection coverage ({field_count} fields, {value_count} values)")

            # Bonus check: if a selection has very few values
            for key, val in detection.items():
                if key == "condition":
                    continue
                if isinstance(val, dict):
                    for sub_key, sub_val in val.items():
                        if isinstance(sub_val, list) and len(sub_val) < 2 and not sub_key.startswith("condition"):
                            score *= 0.93
                            explanation.append(f"\u26a1 Selection '{key}.{sub_key}' has only {len(sub_val)} value(s) \u2014 narrow detection surface")
                            break
        else:
            score *= 0.5
            explanation.append("\u26a0 No detection block found")

        return score, " | ".join(explanation)
    
    def _calculate_specificity_score(self, rule: Dict) -> Tuple[float, str]:
        """Calculate score based on rule specificity and precision."""
        score = 1.0
        explanation = []

        if "detection" in rule:
            detection = rule["detection"]

            # Recursively get ALL string values from detection
            all_values = self._count_detection_strings(detection)
            total_values = len(all_values)
            specific_values = 0
            wildcard_values = 0
            modifier_count = 0

            for val_str in all_values:
                if "*" in val_str or "?" in val_str:
                    wildcard_values += 1
                else:
                    specific_values += 1

            # Check for Sigma modifiers (|endswith, |startswith, |contains etc.)
            for key in detection.keys():
                if "|" in str(key):
                    modifier_count += 1

            if total_values > 0:
                ratio = specific_values / total_values
                if ratio < 0.3:
                    score *= 0.7
                    explanation.append(f"\u26a0 Low specificity ({ratio:.0%} exact values) \u2014 mostly wildcards, high false positive risk")
                elif ratio < 0.6:
                    score *= 0.85
                    explanation.append(f"\u26a1 Moderate specificity ({ratio:.0%} exact vs {wildcard_values} wildcards)")
                else:
                    score *= 0.95
                    explanation.append(f"\u2713 High specificity ({ratio:.0%} exact values) \u2014 precise detection")

            # Modifier usage bonus
            if modifier_count > 0:
                score = min(1.0, score * 1.03)
                explanation.append(f"\u2713 Uses {modifier_count} Sigma modifier(s) (|endswith, |contains etc.) \u2014 precise matching")

            # Check for overly broad selection lists
            for key, val in detection.items():
                if key == "condition":
                    continue
                if isinstance(val, dict):
                    for sub_key, sub_val in val.items():
                        if isinstance(sub_val, list) and len(sub_val) > 20:
                            score *= 0.9
                            explanation.append(f"\u26a1 Selection '{sub_key}' has {len(sub_val)} values \u2014 very broad list")
                            break

            # Check for common system process patterns that often cause false positives
            fp_processes = ["cmd.exe", "powershell.exe", "explorer.exe", "svchost.exe"]
            fp_found = []
            detection_str = str(detection).lower()
            for proc in fp_processes:
                if proc in detection_str:
                    fp_found.append(proc)
            if fp_found:
                score *= 0.92
                explanation.append(f"\u26a1 Targets common system processes ({', '.join(fp_found)}) \u2014 verify exclusions are in place")
        else:
            score *= 0.5
            explanation.append("\u26a0 No detection block")

        return score, " | ".join(explanation)
    
    def _calculate_mitre_alignment_score(self, rule: Dict) -> Tuple[float, str]:
        """Calculate score based on MITRE ATT&CK technique alignment."""
        score = 1.0
        explanation = []

        tags = rule.get("tags", [])
        if not tags:
            score *= 0.7
            explanation.append("\u26a0 No MITRE ATT&CK tags \u2014 threat correlation and SOC triage impacted")
            return score, " | ".join(explanation)

        mitre_tags = [tag for tag in tags if str(tag).startswith("attack.")]
        if not mitre_tags:
            score *= 0.75
            explanation.append("\u26a0 Tags present but no MITRE ATT&CK mappings \u2014 add attack.tXXXX tags")
            return score, " | ".join(explanation)

        # Separate tactics vs techniques vs sub-techniques
        tactics = []
        techniques = []
        sub_techniques = []
        for tag in mitre_tags:
            parts = tag.split(".")
            if len(parts) >= 3 and parts[1].startswith("t") and parts[1][1:].isdigit():
                sub_techniques.append(tag)
            elif len(parts) >= 2 and parts[1].startswith("t") and parts[1][1:].isdigit():
                techniques.append(tag)
            else:
                tactics.append(tag)

        if sub_techniques:
            score *= 0.97
            explanation.append(f"\u2713 {len(sub_techniques)} sub-technique(s) mapped \u2014 excellent precision for ATT&CK Navigator")
        if techniques:
            score *= 0.95
            explanation.append(f"\u2713 {len(techniques)} technique(s) mapped \u2014 good threat intelligence alignment")
        if tactics and not techniques and not sub_techniques:
            score *= 0.85
            explanation.append(f"\u26a1 Only tactic-level tags ({len(tactics)}) \u2014 add specific technique IDs (e.g., attack.t1059.001)")
        elif tactics:
            explanation.append(f"\u2713 {len(tactics)} tactic tag(s) for context")

        return score, " | ".join(explanation)
    
    def _calculate_test_case_score(self, rule: Dict, test_cases: List[Dict]) -> Tuple[float, str]:
        """Calculate score based on test case coverage."""
        if not test_cases:
            return 0.7, "\u26a0 No test cases provided \u2014 rule is untested and unreliable for production"

        score = 1.0
        explanation = []

        test_case_count = len(test_cases)
        if test_case_count < 2:
            score *= 0.7
            explanation.append(f"\u26a0 Only {test_case_count} test case \u2014 minimum 2 needed (positive + negative)")
        elif test_case_count < 4:
            score *= 0.85
            explanation.append(f"\u26a1 {test_case_count} test cases \u2014 consider adding edge-case scenarios")
        else:
            score *= 0.95
            explanation.append(f"\u2713 {test_case_count} test cases \u2014 thorough validation coverage")

        # Check test case quality (detailed descriptions)
        detailed_cases = sum(1 for case in test_cases if len(case.get("description", "")) > 50)
        if detailed_cases == 0:
            score *= 0.8
            explanation.append("\u26a0 No detailed test descriptions \u2014 testers won't know what to verify")
        elif detailed_cases < test_case_count / 2:
            score *= 0.9
            explanation.append(f"\u26a1 {detailed_cases}/{test_case_count} tests have detailed descriptions")
        else:
            explanation.append(f"\u2713 {detailed_cases}/{test_case_count} tests well-documented")

        # Check for positive and negative test cases
        has_positive = any("expected_result" in case for case in test_cases)
        has_negative = any(
            "false_positive" in case.get("description", "").lower()
            or "negative" in case.get("name", "").lower()
            or "benign" in case.get("description", "").lower()
            or case.get("expected_result", "").lower() in ("false", "no alert", "no detection", "not triggered")
            for case in test_cases
        )

        if not has_positive:
            score *= 0.8
            explanation.append("\u26a0 Missing positive test case \u2014 no proof the rule actually fires")
        if not has_negative:
            score *= 0.9
            explanation.append("\u26a1 Missing negative/FP test case \u2014 false positive rate unknown")
        if has_positive and has_negative:
            explanation.append("\u2713 Both positive and negative test scenarios covered")

        return score, " | ".join(explanation)
    
    def _calculate_rule_quality_score(self, rule: Dict) -> Tuple[float, str]:
        """Calculate score based on overall rule quality and metadata completeness."""
        score = 1.0
        explanation = []

        # Check required fields
        required_fields = ["title", "description", "author", "date", "detection"]
        missing_fields = [field for field in required_fields if field not in rule]
        if missing_fields:
            score *= 0.75
            explanation.append(f"\u26a0 Missing required fields: {', '.join(missing_fields)} \u2014 rule metadata incomplete")
        else:
            explanation.append("\u2713 All required fields present (title, description, author, date, detection)")

        # Check description quality
        desc = rule.get("description", "")
        if desc:
            desc_length = len(desc)
            if desc_length < 30:
                score *= 0.75
                explanation.append(f"\u26a0 Description too short ({desc_length} chars) \u2014 analysts need context to triage alerts")
            elif desc_length < 80:
                score *= 0.88
                explanation.append(f"\u26a1 Description could be more detailed ({desc_length} chars)")
            elif desc_length > 500:
                score *= 0.92
                explanation.append(f"\u26a1 Description very long ({desc_length} chars) \u2014 consider summarizing")
            else:
                explanation.append(f"\u2713 Good description length ({desc_length} chars)")
        else:
            score *= 0.7
            explanation.append("\u26a0 No description \u2014 analysts won't understand what this rule detects")

        # Check for proper level field
        level = rule.get("level", "")
        valid_levels = ["informational", "low", "medium", "high", "critical"]
        if level and level.lower() in valid_levels:
            explanation.append(f"\u2713 Severity level set: {level}")
        elif level:
            score *= 0.9
            explanation.append(f"\u26a1 Non-standard severity level: '{level}'")
        else:
            score *= 0.88
            explanation.append("\u26a1 Missing severity level \u2014 add 'level' field for SOC prioritization")

        # Check for status field
        status = rule.get("status", "")
        valid_statuses = ["stable", "test", "experimental", "deprecated", "unsupported"]
        if status and status.lower() in valid_statuses:
            explanation.append(f"\u2713 Rule status: {status}")
        elif not status:
            score *= 0.93
            explanation.append("\u26a1 Missing status field \u2014 add 'stable', 'test', or 'experimental'")

        # Check for proper detection formatting
        if "detection" in rule:
            detection = rule["detection"]
            if not any(isinstance(v, (str, list, dict)) for v in detection.values()):
                score *= 0.7
                explanation.append("\u26a0 Invalid detection field types \u2014 values must be string, list, or dict")
            if "condition" not in detection:
                score *= 0.7
                explanation.append("\u26a0 Missing condition in detection block \u2014 rule won't execute")

        return score, " | ".join(explanation)
    
    def _calculate_false_positive_risk(self, rule: Dict) -> Tuple[float, str]:
        """
        Calculate score based on false positive risk assessment.
        Higher score = lower FP risk = better.
        Uses industry best practices and common false positive patterns.
        """
        score = 1.0
        explanation = []
        risk_count = 0

        # ── Positive signals first (things that REDUCE FP risk) ──

        # 1. Check if rule documents false positives — shows awareness
        fps = rule.get("falsepositives", [])
        if fps and len(fps) > 0:
            score = min(1.0, score * 1.05)
            explanation.append(f"\u2713 False positives documented ({len(fps)} scenario(s)) \u2014 analysts can triage faster")

        # 2. Check if condition uses NOT / filter / exclusion — better FP handling
        condition = ""
        if "detection" in rule:
            condition = rule["detection"].get("condition", "")
        if condition:
            has_filter = bool(re.search(r'\bnot\b|\bfilter\b', condition, re.IGNORECASE))
            has_exclusion = any(k.startswith("filter") for k in rule.get("detection", {}).keys())
            if has_filter or has_exclusion:
                score = min(1.0, score * 1.05)
                explanation.append("\u2713 Uses filter/exclusion logic \u2014 actively reduces false positives")

        # 3. Check for Sigma modifiers (|endswith, |startswith) — more specific matching
        detection_keys_str = " ".join(str(k) for k in rule.get("detection", {}).keys())
        modifier_patterns = ["|endswith", "|startswith", "|contains", "|re", "|base64"]
        has_modifiers = any(mod in detection_keys_str for mod in modifier_patterns)
        if has_modifiers:
            score = min(1.0, score * 1.03)
            explanation.append("\u2713 Uses Sigma modifiers for precise value matching")

        # ── Risk signals (things that INCREASE FP risk) ──

        if "detection" in rule:
            detection = rule["detection"]
            detection_str = str(detection).lower()

            # 4. Broad wildcards
            broad_wildcards = ["*\\\\*\\\\*", "*.*", "\\\\*", ".*"]
            broad_found = [p for p in broad_wildcards if p in detection_str]
            if broad_found:
                score *= 0.85
                risk_count += len(broad_found)
                explanation.append(f"\u26a0 Broad wildcards detected ({len(broad_found)}) \u2014 high false positive risk")

            # 5. OR conditions without filters
            if " or " in condition.lower() and "not" not in condition.lower() and "filter" not in condition.lower():
                score *= 0.88
                risk_count += 1
                explanation.append("\u26a1 Uses OR conditions without filters \u2014 broadens detection surface")

            # 6. System process targeting without exclusions
            system_procs = ["svchost.exe", "explorer.exe", "lsass.exe", "csrss.exe",
                           "services.exe", "winlogon.exe", "cmd.exe", "powershell.exe"]
            targeted_procs = [p for p in system_procs if p in detection_str]
            if targeted_procs and not (has_filter or has_exclusion):
                score *= 0.88
                explanation.append(f"\u26a1 Targets {len(targeted_procs)} system process(es) without exclusion filter")

            # 7. Common legitimate paths without context
            common_paths = ["system32", "program files", "appdata", "temp"]
            path_hits = [p for p in common_paths if p in detection_str]
            if len(path_hits) >= 2:
                score *= 0.92
                explanation.append(f"\u26a1 References common system paths ({', '.join(path_hits[:3])}) \u2014 ensure context narrows scope")

        # ── Summary assessment ──
        if risk_count == 0 and score >= 0.95:
            explanation.append("\u2713 Low false positive risk \u2014 rule is well-scoped")
        elif score < 0.75:
            explanation.append("\u26a0 High false positive risk \u2014 add exclusions or narrow detection scope")

        return max(0.1, score), " | ".join(explanation) if explanation else "\u2713 No significant false positive risks detected"
    
    def _compute_dynamic_weights(self, scores: Dict[str, float]) -> Dict[str, float]:
        """
        Compute dynamic weights based on score variance.
        Components with lower scores get slightly higher weight to penalize weak areas.
        """
        base_weights = {
            "complexity": 0.15,
            "coverage": 0.15,
            "specificity": 0.15,
            "mitre_alignment": 0.10,
            "test_case_coverage": 0.15,
            "rule_quality": 0.15,
            "false_positive_risk": 0.15,
        }

        # Find the weakest components and boost their weight
        avg_score = sum(scores.values()) / len(scores)
        adjusted = {}
        for name, base_w in base_weights.items():
            score = scores.get(name, avg_score)
            if score < 0.6:
                adjusted[name] = base_w * 1.3  # Penalize weak areas more
            elif score < 0.8:
                adjusted[name] = base_w * 1.1
            else:
                adjusted[name] = base_w

        # Normalize weights to sum to 1.0
        total = sum(adjusted.values())
        return {k: v / total for k, v in adjusted.items()}

    def calculate_confidence(self, rule: Dict, test_cases: List[Dict] = None) -> Dict:
        """Calculate overall confidence score using multiple algorithms with dynamic weights."""
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

        # Dynamic weights based on score distribution
        weights = self._compute_dynamic_weights(scores)

        final_score = sum(scores[k] * weights[k] for k in weights.keys())
        final_score = min(1.0, max(0.0, final_score))

        # Maturity assessment
        maturity = self.maturity_assessor.assess(rule, final_score, test_cases)

        result = {
            "overall_score": final_score,
            "component_scores": scores,
            "explanations": explanations,
            "weights": weights,
            "maturity": maturity,
        }

        # Visualize the results (for CLI usage)
        try:
            self.visualizer.visualize_confidence(result)
        except Exception:
            pass  # Skip visualization in non-CLI contexts

        return result

class SigmaQA:
    def __init__(self, openai_api_key: str = "", model_name: str = "gpt-4.1-2025-04-14",
                 provider: Optional[AIProvider] = None, provider_name: str = "openai"):
        """
        Initialize the Q&A system with multi-provider support.

        Args:
            openai_api_key: API key (legacy support)
            model_name: Model to use for Q&A
            provider: AIProvider instance (preferred)
            provider_name: Provider name ("openai", "anthropic", "google")
        """
        self.openai_api_key = openai_api_key
        self.model_name = model_name

        # Multi-provider support
        if provider is not None:
            self.provider = provider
        elif openai_api_key:
            # Auto-detect provider from key prefix
            if openai_api_key.startswith("sk-ant-"):
                provider_name = "anthropic"
            elif openai_api_key.startswith("AIza"):
                provider_name = "google"
            self.provider = get_provider(provider_name, openai_api_key, model_name)
        else:
            self.provider = None

        self.confidence_calculator = RuleConfidenceCalculator()
        logger.info(f"SigmaQA initialized with provider: {provider_name}, model: {model_name}")
        
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
        except Exception:
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
        Generate a response based on the query and product using multi-provider AI.

        Args:
            query: Natural language query
            product: Target product (sigma, yara, splunk, qradar)
        """
        if not self.provider:
            logger.error("No AI provider configured")
            return {}

        messages = [
            Message(role="system", content=(
                f"You are a world-class cybersecurity expert specializing in {product.upper()} rules "
                "and threat detection engineering. You create production-quality detection rules "
                "following industry best practices and SigmaHQ conventions. "
                "You always respond with valid, parseable JSON only."
            )),
            Message(role="user", content=f"""Create a comprehensive detection rule based on the following query.

Query: {query}
Product: {product.upper()}

Return ONLY valid JSON with this exact structure:
{{
    "rule": {{
        "title": "Descriptive rule title",
        "description": "Detailed description of what this rule detects and why",
        "author": "PERSEPTOR",
        "date": "{datetime.now().strftime('%Y/%m/%d')}",
        "status": "experimental",
        "logsource": {{
            "category": "process_creation",
            "product": "windows"
        }},
        "detection": {{
            "selection": {{}},
            "condition": "selection"
        }},
        "falsepositives": [],
        "level": "medium",
        "tags": []
    }},
    "explanation": "Detailed explanation of the rule logic and detection approach",
    "test_cases": [
        {{
            "name": "Test case name",
            "description": "Detailed test case description",
            "expected_result": "Expected detection result (true positive / false positive)"
        }}
    ],
    "confidence_score": 0.85,
    "mitre_techniques": [
        {{
            "id": "T1059.001",
            "name": "Technique Name",
            "description": "How this technique is used in the detected threat"
        }}
    ],
    "recommendations": [
        "Tuning recommendation",
        "Implementation best practice",
        "False positive mitigation"
    ],
    "references": [
        {{
            "title": "Reference title",
            "url": "https://example.com",
            "description": "Reference description"
        }}
    ]
}}

IMPORTANT: Return ONLY the JSON object. No markdown, no explanations outside JSON."""),
        ]

        try:
            response = self.provider.generate(messages, temperature=0.1)
            # Track token usage
            try:
                from modules.ai_engine import _track_usage
                _track_usage(response, "generate_rule")
            except Exception:
                pass
            content = response.content.strip()

            # Extract JSON from response
            from modules.ai_engine import extract_json_from_response
            content = extract_json_from_response(content)

            # Remove control characters
            content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)

            result = json.loads(content)

            # Validate references
            if "references" in result:
                result["references"] = self._validate_references(result["references"])

            logger.info(
                f"Rule generated successfully",
                extra={"provider": self.provider.provider_name, "model": response.model},
            )
            return result
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
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

def create_qa_system(
    openai_api_key: str = "",
    model_name: str = "gpt-4.1-2025-04-14",
    provider: Optional[AIProvider] = None,
    provider_name: str = "openai",
) -> SigmaQA:
    """
    Create a new Q&A system instance with multi-provider support.

    Args:
        openai_api_key: API key (legacy support)
        model_name: Model to use
        provider: AIProvider instance (preferred)
        provider_name: Provider name ("openai", "anthropic", "google")

    Returns:
        SigmaQA: A new Q&A system instance
    """
    return SigmaQA(
        openai_api_key=openai_api_key,
        model_name=model_name,
        provider=provider,
        provider_name=provider_name,
    )