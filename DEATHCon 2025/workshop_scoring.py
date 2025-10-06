#!/usr/bin/env python3
"""
DEATHCon 2025 Workshop Scoring System
Human vs AI Detection Engineering Challenge

This script evaluates participant submissions and compares them with AI results.
"""

import json
import yaml
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

class WorkshopScorer:
    def __init__(self):
        self.scoring_weights = {
            "completeness": 0.25,
            "accuracy": 0.25,
            "rule_quality": 0.20,
            "innovation": 0.15,
            "speed": 0.15
        }
        
    def score_manual_analysis(self, submission: Dict) -> Dict[str, float]:
        """Score manual threat analysis"""
        scores = {}
        
        # Completeness Score (0-10)
        completeness_score = self._score_completeness(submission)
        scores["completeness"] = completeness_score
        
        # Accuracy Score (0-10)
        accuracy_score = self._score_accuracy(submission)
        scores["accuracy"] = accuracy_score
        
        # Innovation Score (0-10)
        innovation_score = self._score_innovation(submission)
        scores["innovation"] = innovation_score
        
        return scores
        
    def score_detection_rules(self, rules: List[Dict]) -> Dict[str, float]:
        """Score generated detection rules"""
        scores = {}
        
        # Rule Quality Score (0-10)
        quality_score = self._score_rule_quality(rules)
        scores["rule_quality"] = quality_score
        
        return scores
        
    def compare_with_ai(self, human_results: Dict, ai_results: Dict) -> Dict[str, Any]:
        """Compare human analysis with AI results"""
        comparison = {
            "human_scores": human_results,
            "ai_scores": ai_results,
            "differences": {},
            "winner": {},
            "insights": []
        }
        
        # Compare each aspect
        for aspect in ["completeness", "accuracy", "rule_quality", "innovation"]:
            human_score = human_results.get(aspect, 0)
            ai_score = ai_results.get(aspect, 0)
            
            comparison["differences"][aspect] = {
                "human": human_score,
                "ai": ai_score,
                "difference": human_score - ai_score
            }
            
            if human_score > ai_score:
                comparison["winner"][aspect] = "Human"
            elif ai_score > human_score:
                comparison["winner"][aspect] = "AI"
            else:
                comparison["winner"][aspect] = "Tie"
                
        # Generate insights
        comparison["insights"] = self._generate_insights(comparison)
        
        return comparison
        
    def calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        total_score = 0
        total_weight = 0
        
        for aspect, score in scores.items():
            weight = self.scoring_weights.get(aspect, 0)
            total_score += score * weight
            total_weight += weight
            
        return total_score / total_weight if total_weight > 0 else 0
        
    def _score_completeness(self, submission: Dict) -> float:
        """Score completeness of analysis"""
        required_fields = [
            "threat_summary",
            "ttps",
            "mitre_techniques", 
            "iocs",
            "threat_actors",
            "tools_malware",
            "sigma_rules",
            "yara_rules"
        ]
        
        completed_fields = 0
        for field in required_fields:
            if field in submission and submission[field]:
                completed_fields += 1
                
        return (completed_fields / len(required_fields)) * 10
        
    def _score_accuracy(self, submission: Dict) -> float:
        """Score accuracy of analysis (requires reference data)"""
        # This would need reference data to compare against
        # For now, return a placeholder score
        return 7.5  # Placeholder
        
    def _score_innovation(self, submission: Dict) -> float:
        """Score innovation and creativity"""
        innovation_indicators = [
            "creative_approaches",
            "novel_insights",
            "unique_rule_combinations",
            "advanced_techniques"
        ]
        
        innovation_count = 0
        for indicator in innovation_indicators:
            if indicator in submission and submission[indicator]:
                innovation_count += 1
                
        return min(innovation_count * 2.5, 10)
        
    def _score_rule_quality(self, rules: List[Dict]) -> float:
        """Score quality of detection rules"""
        if not rules:
            return 0
            
        total_score = 0
        for rule in rules:
            rule_score = self._evaluate_single_rule(rule)
            total_score += rule_score
            
        return total_score / len(rules)
        
    def _evaluate_single_rule(self, rule: Dict) -> float:
        """Evaluate a single detection rule"""
        score = 0
        
        # Check required fields
        required_fields = ["title", "description", "detection"]
        for field in required_fields:
            if field in rule and rule[field]:
                score += 1
                
        # Check rule structure
        if "detection" in rule:
            detection = rule["detection"]
            if "selection" in detection and "condition" in detection:
                score += 2
                
        # Check for false positives
        if "falsepositives" in rule and rule["falsepositives"]:
            score += 1
            
        # Check for proper tagging
        if "tags" in rule and rule["tags"]:
            score += 1
            
        return min(score, 10)
        
    def _generate_insights(self, comparison: Dict) -> List[str]:
        """Generate insights from comparison"""
        insights = []
        
        # Analyze winners
        human_wins = sum(1 for winner in comparison["winner"].values() if winner == "Human")
        ai_wins = sum(1 for winner in comparison["winner"].values() if winner == "AI")
        
        if human_wins > ai_wins:
            insights.append("Human analysis showed superior performance overall")
        elif ai_wins > human_wins:
            insights.append("AI analysis demonstrated stronger capabilities")
        else:
            insights.append("Human and AI analysis were closely matched")
            
        # Specific insights
        for aspect, diff in comparison["differences"].items():
            if abs(diff["difference"]) > 2:
                if diff["difference"] > 0:
                    insights.append(f"Human significantly outperformed AI in {aspect}")
                else:
                    insights.append(f"AI significantly outperformed Human in {aspect}")
                    
        return insights
        
    def generate_report(self, participant_id: str, scores: Dict, comparison: Dict) -> str:
        """Generate detailed scoring report"""
        report = f"""
# 🏆 DEATHCon 2025 Workshop Results

**Participant ID:** {participant_id}  
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Workshop:** Human vs AI Detection Engineering Challenge

## 📊 Overall Scores

| Aspect | Human | AI | Winner |
|--------|-------|----|---------|"""
        
        for aspect, diff in comparison["differences"].items():
            human_score = diff["human"]
            ai_score = diff["ai"]
            winner = comparison["winner"][aspect]
            report += f"\n| {aspect.title()} | {human_score:.1f} | {ai_score:.1f} | {winner} |"
            
        # Overall winner
        human_overall = self.calculate_overall_score(comparison["human_scores"])
        ai_overall = self.calculate_overall_score(comparison["ai_scores"])
        
        if human_overall > ai_overall:
            overall_winner = "Human"
        elif ai_overall > human_overall:
            overall_winner = "AI"
        else:
            overall_winner = "Tie"
            
        report += f"""

## 🎯 Overall Performance
- **Human Overall Score:** {human_overall:.1f}/10
- **AI Overall Score:** {ai_overall:.1f}/10
- **Winner:** {overall_winner}

## 💡 Key Insights
"""
        
        for insight in comparison["insights"]:
            report += f"- {insight}\n"
            
        report += f"""

## 📈 Detailed Analysis

### Completeness
- **Human:** {comparison['differences']['completeness']['human']:.1f}/10
- **AI:** {comparison['differences']['completeness']['ai']:.1f}/10
- **Difference:** {comparison['differences']['completeness']['difference']:+.1f}

### Accuracy
- **Human:** {comparison['differences']['accuracy']['human']:.1f}/10
- **AI:** {comparison['differences']['accuracy']['ai']:.1f}/10
- **Difference:** {comparison['differences']['accuracy']['difference']:+.1f}

### Rule Quality
- **Human:** {comparison['differences']['rule_quality']['human']:.1f}/10
- **AI:** {comparison['differences']['rule_quality']['ai']:.1f}/10
- **Difference:** {comparison['differences']['rule_quality']['difference']:+.1f}

### Innovation
- **Human:** {comparison['differences']['innovation']['human']:.1f}/10
- **AI:** {comparison['differences']['innovation']['ai']:.1f}/10
- **Difference:** {comparison['differences']['innovation']['difference']:+.1f}

---

*Generated by DEATHCon 2025 Workshop Scoring System*
"""
        
        return report

def main():
    """Example usage of the scoring system"""
    scorer = WorkshopScorer()
    
    # Example human submission
    human_submission = {
        "threat_summary": "Comprehensive analysis of APT group...",
        "ttps": ["T1055", "T1083", "T1105"],
        "mitre_techniques": ["Process Injection", "File Discovery", "Remote File Copy"],
        "iocs": ["192.168.1.1", "malicious.com", "abc123def456"],
        "threat_actors": ["APT29"],
        "tools_malware": ["Cobalt Strike", "Mimikatz"],
        "sigma_rules": [{"title": "Suspicious Process", "description": "Detects suspicious process"}],
        "yara_rules": [{"name": "Malware_Signature", "strings": ["$s1 = \"evil\""]}],
        "creative_approaches": True,
        "novel_insights": True
    }
    
    # Example AI results
    ai_results = {
        "completeness": 8.5,
        "accuracy": 9.0,
        "rule_quality": 8.0,
        "innovation": 6.5
    }
    
    # Score human analysis
    human_scores = scorer.score_manual_analysis(human_submission)
    rule_scores = scorer.score_detection_rules(human_submission["sigma_rules"])
    human_scores.update(rule_scores)
    
    # Compare with AI
    comparison = scorer.compare_with_ai(human_scores, ai_results)
    
    # Generate report
    report = scorer.generate_report("DEATHCon2025_001", human_scores, comparison)
    
    print(report)

if __name__ == "__main__":
    main()
