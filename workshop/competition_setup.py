#!/usr/bin/env python3
"""
DEATHCon Workshop - Human vs AI Competition Setup
=================================================

Bu modül DEATHCon workshop'unda kullanılacak Human vs AI competition
için gerekli teknik altyapıyı sağlar.

Features:
- Gizli threat intelligence raporları
- Competition timer ve scoring
- Real-time rule validation
- Lab environment integration
- Live streaming support
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid

# PERSEPTOR modüllerini import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.gpt_module import (
    summarize_threat_report,
    extract_iocs_ttps_gpt,
    generate_more_sigma_rules_from_article,
    convert_sigma_to_siem_queries
)
from modules.sigma_module import generate_sigma_rules_for_commands
from modules.yara_module import generate_yara_rules
from modules.global_sigma_match_module import (
    load_sigma_rules_local,
    match_sigma_rules_with_report
)

@dataclass
class CompetitionParticipant:
    """Competition participant (Human or AI)"""
    id: str
    name: str
    type: str  # "human" or "ai"
    rules_generated: List[Dict]
    score: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class CompetitionRule:
    """Generated detection rule"""
    id: str
    participant_id: str
    rule_type: str  # "sigma" or "yara"
    rule_content: str
    title: str
    description: str
    confidence_score: float
    mitre_techniques: List[str]
    validation_result: Optional[Dict] = None
    timestamp: datetime = None

@dataclass
class ThreatReport:
    """Threat intelligence report for competition"""
    id: str
    title: str
    content: str
    url: str
    difficulty_level: str  # "easy", "medium", "hard"
    expected_rules_count: int
    metadata: Dict

class CompetitionTimer:
    """Competition timer with live updates"""
    
    def __init__(self, duration_minutes: int = 60):
        self.duration = timedelta(minutes=duration_minutes)
        self.start_time = None
        self.end_time = None
        self.is_running = False
        self.callbacks = []
        
    def start(self):
        """Start the competition timer"""
        self.start_time = datetime.now()
        self.end_time = self.start_time + self.duration
        self.is_running = True
        print(f"🚀 Competition started! Duration: {self.duration}")
        print(f"⏰ End time: {self.end_time.strftime('%H:%M:%S')}")
        
    def stop(self):
        """Stop the competition timer"""
        self.is_running = False
        print("🏁 Competition ended!")
        
    def get_remaining_time(self) -> timedelta:
        """Get remaining time"""
        if not self.is_running or not self.end_time:
            return timedelta(0)
        remaining = self.end_time - datetime.now()
        return remaining if remaining > timedelta(0) else timedelta(0)
        
    def is_finished(self) -> bool:
        """Check if competition is finished"""
        return self.is_running and self.get_remaining_time() <= timedelta(0)

class RuleValidator:
    """Validate generated detection rules"""
    
    def __init__(self):
        self.validation_criteria = {
            "sigma": {
                "required_fields": ["title", "description", "detection", "level"],
                "valid_levels": ["low", "medium", "high", "critical"],
                "syntax_check": True
            },
            "yara": {
                "required_fields": ["rule", "meta"],
                "syntax_check": True
            }
        }
    
    def validate_rule(self, rule: CompetitionRule) -> Dict:
        """Validate a detection rule"""
        rule_type = rule.rule_type
        criteria = self.validation_criteria.get(rule_type, {})
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "score": 0
        }
        
        try:
            # Basic syntax validation
            if rule_type == "sigma":
                self._validate_sigma_rule(rule, validation_result)
            elif rule_type == "yara":
                self._validate_yara_rule(rule, validation_result)
                
            # Calculate score
            validation_result["score"] = self._calculate_rule_score(rule, validation_result)
            
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
            
        return validation_result
    
    def _validate_sigma_rule(self, rule: CompetitionRule, result: Dict):
        """Validate Sigma rule"""
        # Check required fields
        if not rule.title:
            result["errors"].append("Missing title")
        if not rule.description:
            result["warnings"].append("Missing description")
            
        # Check rule content
        if "detection:" not in rule.rule_content.lower():
            result["errors"].append("Missing detection section")
            
    def _validate_yara_rule(self, rule: CompetitionRule, result: Dict):
        """Validate YARA rule"""
        # Check basic YARA syntax
        if not rule.rule_content.startswith("rule "):
            result["errors"].append("Invalid YARA rule syntax")
            
        if "condition:" not in rule.rule_content.lower():
            result["errors"].append("Missing condition section")
    
    def _calculate_rule_score(self, rule: CompetitionRule, validation: Dict) -> int:
        """Calculate rule score based on quality"""
        score = 0
        
        # Base score for valid rule
        if validation["is_valid"]:
            score += 50
            
        # Bonus for confidence score
        score += int(rule.confidence_score * 20)
        
        # Bonus for MITRE techniques
        score += len(rule.mitre_techniques) * 5
        
        # Penalty for errors
        score -= len(validation["errors"]) * 10
        
        # Penalty for warnings
        score -= len(validation["warnings"]) * 2
        
        return max(0, score)

class CompetitionManager:
    """Main competition manager"""
    
    def __init__(self, duration_minutes: int = 60):
        self.timer = CompetitionTimer(duration_minutes)
        self.validator = RuleValidator()
        self.participants: Dict[str, CompetitionParticipant] = {}
        self.rules: Dict[str, CompetitionRule] = {}
        self.threat_report: Optional[ThreatReport] = None
        self.is_active = False
        
    def add_participant(self, name: str, participant_type: str) -> str:
        """Add a participant to the competition"""
        participant_id = str(uuid.uuid4())
        participant = CompetitionParticipant(
            id=participant_id,
            name=name,
            type=participant_type,
            rules_generated=[]
        )
        self.participants[participant_id] = participant
        print(f"✅ Added {participant_type} participant: {name}")
        return participant_id
    
    def set_threat_report(self, report: ThreatReport):
        """Set the threat report for competition"""
        self.threat_report = report
        print(f"📋 Threat report set: {report.title}")
        print(f"🎯 Difficulty: {report.difficulty_level}")
        print(f"📊 Expected rules: {report.expected_rules_count}")
    
    def start_competition(self):
        """Start the competition"""
        if not self.threat_report:
            raise ValueError("Threat report must be set before starting competition")
        
        self.is_active = True
        self.timer.start()
        
        # Start participant tracking
        for participant in self.participants.values():
            participant.start_time = datetime.now()
            
        print(f"\n🎉 COMPETITION STARTED!")
        print(f"📋 Report: {self.threat_report.title}")
        print(f"⏰ Duration: {self.timer.duration}")
        print(f"👥 Participants: {len(self.participants)}")
        print("\n" + "="*50)
    
    def add_rule(self, participant_id: str, rule_type: str, rule_content: str, 
                 title: str, description: str, confidence_score: float = 0.0,
                 mitre_techniques: List[str] = None) -> str:
        """Add a rule from a participant"""
        if not self.is_active:
            raise ValueError("Competition is not active")
            
        if participant_id not in self.participants:
            raise ValueError("Invalid participant ID")
            
        rule_id = str(uuid.uuid4())
        rule = CompetitionRule(
            id=rule_id,
            participant_id=participant_id,
            rule_type=rule_type,
            rule_content=rule_content,
            title=title,
            description=description,
            confidence_score=confidence_score,
            mitre_techniques=mitre_techniques or [],
            timestamp=datetime.now()
        )
        
        # Validate rule
        rule.validation_result = self.validator.validate_rule(rule)
        
        # Add to collections
        self.rules[rule_id] = rule
        self.participants[participant_id].rules_generated.append(rule_id)
        
        # Update score
        if rule.validation_result["is_valid"]:
            self.participants[participant_id].score += rule.validation_result["score"]
        
        print(f"✅ Rule added by {self.participants[participant_id].name}: {title}")
        return rule_id
    
    def get_leaderboard(self) -> List[Dict]:
        """Get current leaderboard"""
        leaderboard = []
        for participant in self.participants.values():
            leaderboard.append({
                "name": participant.name,
                "type": participant.type,
                "score": participant.score,
                "rules_count": len(participant.rules_generated),
                "valid_rules": len([r for r in participant.rules_generated 
                                  if self.rules[r].validation_result["is_valid"]])
            })
        
        return sorted(leaderboard, key=lambda x: x["score"], reverse=True)
    
    def get_competition_status(self) -> Dict:
        """Get current competition status"""
        remaining_time = self.timer.get_remaining_time()
        
        return {
            "is_active": self.is_active,
            "remaining_time": str(remaining_time),
            "threat_report": self.threat_report.title if self.threat_report else None,
            "participants": len(self.participants),
            "total_rules": len(self.rules),
            "leaderboard": self.get_leaderboard()
        }
    
    def end_competition(self):
        """End the competition and show results"""
        self.is_active = False
        self.timer.stop()
        
        # Set end times
        for participant in self.participants.values():
            participant.end_time = datetime.now()
        
        print("\n🏁 COMPETITION ENDED!")
        print("="*50)
        
        # Show final results
        leaderboard = self.get_leaderboard()
        print("\n🏆 FINAL LEADERBOARD:")
        for i, entry in enumerate(leaderboard, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
            print(f"{emoji} {i}. {entry['name']} ({entry['type']}) - Score: {entry['score']} - Rules: {entry['rules_count']} ({entry['valid_rules']} valid)")
        
        return leaderboard

class PERSEPTORAI:
    """PERSEPTOR AI participant for competition"""
    
    def __init__(self, openai_api_key: str, competition_manager: CompetitionManager):
        self.api_key = openai_api_key
        self.competition = competition_manager
        self.participant_id = None
        
    def join_competition(self, name: str = "PERSEPTOR AI") -> str:
        """Join the competition as AI participant"""
        self.participant_id = self.competition.add_participant(name, "ai")
        return self.participant_id
    
    def analyze_and_generate_rules(self, threat_report: ThreatReport) -> List[str]:
        """Analyze threat report and generate detection rules"""
        if not self.participant_id:
            raise ValueError("AI participant must join competition first")
        
        rule_ids = []
        
        try:
            # Step 1: Summarize threat report
            summary = summarize_threat_report(
                text=threat_report.content,
                openai_api_key=self.api_key
            )
            
            # Step 2: Extract IoCs and TTPs
            iocs_ttps = extract_iocs_ttps_gpt(
                text=threat_report.content,
                openai_api_key=self.api_key
            )
            
            # Step 3: Generate Sigma rules
            sigma_rules = generate_more_sigma_rules_from_article(
                article_text=threat_report.content,
                images_ocr_text="",  # No images in this case
                openai_api_key=self.api_key
            )
            
            # Step 4: Generate YARA rules
            yara_rules_text = generate_yara_rules(iocs_ttps)
            
            # Add Sigma rules
            if sigma_rules and sigma_rules != "Error generating extra Sigma rules.":
                sigma_rule_id = self.competition.add_rule(
                    participant_id=self.participant_id,
                    rule_type="sigma",
                    rule_content=sigma_rules,
                    title="AI-Generated Sigma Rules",
                    description="Comprehensive Sigma rules generated by PERSEPTOR AI",
                    confidence_score=0.85,
                    mitre_techniques=self._extract_mitre_techniques(sigma_rules)
                )
                rule_ids.append(sigma_rule_id)
            
            # Add YARA rules
            if yara_rules_text:
                yara_rule_id = self.competition.add_rule(
                    participant_id=self.participant_id,
                    rule_type="yara",
                    rule_content=yara_rules_text,
                    title="AI-Generated YARA Rules",
                    description="YARA rules generated from extracted IoCs",
                    confidence_score=0.80,
                    mitre_techniques=[]
                )
                rule_ids.append(yara_rule_id)
            
            print(f"🤖 PERSEPTOR AI generated {len(rule_ids)} rules")
            
        except Exception as e:
            print(f"❌ AI analysis error: {str(e)}")
            
        return rule_ids
    
    def _extract_mitre_techniques(self, sigma_rules: str) -> List[str]:
        """Extract MITRE techniques from Sigma rules"""
        techniques = []
        # Simple extraction - in real implementation, use proper parsing
        if "T1055" in sigma_rules:
            techniques.append("T1055 - Process Injection")
        if "T1059" in sigma_rules:
            techniques.append("T1059 - Command and Scripting Interpreter")
        if "T1071" in sigma_rules:
            techniques.append("T1071 - Application Layer Protocol")
        return techniques

# Sample threat reports for competition
SAMPLE_THREAT_REPORTS = [
    ThreatReport(
        id="sample_1",
        title="APT29 Cozy Bear Campaign Analysis",
        content="""
        APT29, also known as Cozy Bear, has been conducting sophisticated cyber espionage campaigns targeting government organizations and critical infrastructure. The group uses advanced techniques including:
        
        - PowerShell-based payload delivery
        - Living off the land techniques using legitimate tools
        - Custom malware with anti-analysis capabilities
        - Command and control communication through encrypted channels
        
        Key indicators include:
        - Domain: cozybear[.]net
        - IP: 192.168.1.100
        - Hash: a1b2c3d4e5f6...
        - Process: powershell.exe -enc
        - Registry: HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
        """,
        url="https://example.com/apt29-report",
        difficulty_level="medium",
        expected_rules_count=5,
        metadata={"category": "APT", "severity": "high"}
    ),
    
    ThreatReport(
        id="sample_2",
        title="Ransomware-as-a-Service Operation",
        content="""
        A new ransomware-as-a-service operation has been identified targeting small and medium businesses. The operation uses:
        
        - Phishing emails with malicious attachments
        - Exploitation of unpatched vulnerabilities
        - Lateral movement using PsExec
        - Data exfiltration before encryption
        - Ransom demands in cryptocurrency
        
        Indicators:
        - Email: support@legitimate[.]com
        - URL: hxxp://download[.]malicious[.]site
        - File: invoice.pdf.exe
        - Process: psexec.exe
        - Registry: HKEY_LOCAL_MACHINE\\SOFTWARE\\Ransomware
        """,
        url="https://example.com/ransomware-report",
        difficulty_level="easy",
        expected_rules_count=4,
        metadata={"category": "Ransomware", "severity": "critical"}
    )
]

def main():
    """Demo competition setup"""
    print("🎯 DEATHCon Workshop - Human vs AI Competition Setup")
    print("="*60)
    
    # Initialize competition
    competition = CompetitionManager(duration_minutes=30)  # 30 min demo
    
    # Add participants
    human_id = competition.add_participant("Security Expert", "human")
    ai_id = competition.add_participant("PERSEPTOR AI", "ai")
    
    # Set threat report
    threat_report = SAMPLE_THREAT_REPORTS[0]
    competition.set_threat_report(threat_report)
    
    # Initialize AI
    openai_key = "your-openai-api-key"  # Replace with actual key
    ai_participant = PERSEPTORAI(openai_key, competition)
    ai_participant.join_competition()
    
    # Start competition
    competition.start_competition()
    
    # Simulate AI analysis
    print("\n🤖 PERSEPTOR AI is analyzing the threat report...")
    ai_rule_ids = ai_participant.analyze_and_generate_rules(threat_report)
    
    # Show status
    status = competition.get_competition_status()
    print(f"\n📊 Competition Status:")
    print(f"   Active: {status['is_active']}")
    print(f"   Time remaining: {status['remaining_time']}")
    print(f"   Total rules: {status['total_rules']}")
    
    # End competition
    competition.end_competition()

if __name__ == "__main__":
    main()
