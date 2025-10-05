#!/usr/bin/env python3
"""
DEATHCon Workshop - Main Execution Script
========================================

This script orchestrates the entire DEATHCon workshop experience,
including the Human vs AI competition, live streaming, and real-time scoring.

Usage:
    python run_workshop.py --config workshop_config.json --mode [demo|live]
"""

import os
import sys
import json
import argparse
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

# Add parent directory to path for PERSEPTOR modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from competition_setup import CompetitionManager, PERSEPTORAI, ThreatReport
from lab_environment_setup import LabEnvironment, RuleValidator
from modules.gpt_module import summarize_threat_report, extract_iocs_ttps_gpt

class WorkshopOrchestrator:
    """Main orchestrator for the DEATHCon workshop"""
    
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.competition = None
        self.lab_environment = None
        self.ai_participant = None
        self.streaming_enabled = False
        self.workshop_start_time = None
        self.workshop_end_time = None
        
    def load_config(self, config_path: str) -> Dict:
        """Load workshop configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)
    
    def initialize_workshop(self):
        """Initialize all workshop components"""
        print("🚀 Initializing DEATHCon Workshop...")
        
        # Initialize competition
        duration = self.config['competition_setup']['duration_minutes']
        self.competition = CompetitionManager(duration_minutes=duration)
        
        # Initialize lab environment
        self.lab_environment = LabEnvironment()
        
        # Initialize AI participant
        openai_key = os.getenv('OPENAI_API_KEY', 'your-openai-api-key')
        self.ai_participant = PERSEPTORAI(openai_key, self.competition)
        
        print("✅ Workshop components initialized successfully")
    
    def setup_participants(self):
        """Setup workshop participants"""
        print("👥 Setting up participants...")
        
        # Add AI participant
        ai_id = self.ai_participant.join_competition("PERSEPTOR AI")
        print(f"🤖 AI participant added: {ai_id}")
        
        # Add human participants (simulated for demo)
        human_participants = [
            "Security Expert 1",
            "Detection Engineer 2", 
            "Threat Hunter 3",
            "SOC Analyst 4",
            "Incident Responder 5"
        ]
        
        for participant in human_participants:
            human_id = self.competition.add_participant(participant, "human")
            print(f"👤 Human participant added: {participant}")
        
        print(f"✅ {len(human_participants) + 1} participants ready")
    
    def select_threat_report(self) -> ThreatReport:
        """Select threat report for competition"""
        print("📋 Selecting threat report...")
        
        # Load sample threat reports
        with open('sample_threat_reports.json', 'r') as f:
            reports_data = json.load(f)
        
        # Select report based on configuration
        selected_report = reports_data['workshop_threat_reports'][0]  # APT29 for demo
        
        threat_report = ThreatReport(
            id=selected_report['id'],
            title=selected_report['title'],
            content=selected_report['content'],
            url=selected_report['url'],
            difficulty_level=selected_report['difficulty'],
            expected_rules_count=selected_report['expected_rules'],
            metadata=selected_report['metadata']
        )
        
        self.competition.set_threat_report(threat_report)
        print(f"✅ Threat report selected: {threat_report.title}")
        print(f"🎯 Difficulty: {threat_report.difficulty_level}")
        print(f"📊 Expected rules: {threat_report.expected_rules_count}")
        
        return threat_report
    
    def start_workshop(self):
        """Start the workshop"""
        print("\n" + "="*60)
        print("🎉 DEATHCon Workshop: PERSEPTOR AI vs Human Experts")
        print("="*60)
        
        self.workshop_start_time = datetime.now()
        
        # Pre-competition phase
        self.pre_competition_phase()
        
        # Competition phase
        self.competition_phase()
        
        # Post-competition phase
        self.post_competition_phase()
        
        self.workshop_end_time = datetime.now()
        
        print("\n🏁 Workshop completed successfully!")
        print(f"⏱️  Total duration: {self.workshop_end_time - self.workshop_start_time}")
    
    def pre_competition_phase(self):
        """Pre-competition introduction phase"""
        print("\n📚 PRE-COMPETITION PHASE")
        print("-" * 30)
        
        # Introduction to PERSEPTOR
        print("🔍 Introduction to PERSEPTOR:")
        print("   - AI-powered detection engineering platform")
        print("   - Automated threat analysis and rule generation")
        print("   - Real-time validation and scoring")
        print("   - Comprehensive MITRE ATT&CK mapping")
        
        # Competition rules
        print("\n📋 Competition Rules:")
        print("   - 45-minute time limit")
        print("   - Generate detection rules from threat report")
        print("   - Real-time scoring and validation")
        print("   - Lab environment testing")
        print("   - Live streaming and audience engagement")
        
        # Scoring system
        print("\n🏆 Scoring System:")
        scoring = self.config['scoring_system']
        print(f"   - Rule Quality: {scoring['weights']['rule_quality']*100}%")
        print(f"   - Rule Count: {scoring['weights']['rule_count']*100}%")
        print(f"   - Coverage: {scoring['weights']['coverage']*100}%")
        print(f"   - Innovation: {scoring['weights']['innovation']*100}%")
        print(f"   - Speed: {scoring['weights']['speed']*100}%")
        
        # Lab environment demo
        print("\n🔬 Lab Environment Demo:")
        print(f"   - {len(self.lab_environment.scenarios)} test scenarios")
        print(f"   - {len(self.lab_environment.events)} total events")
        print(f"   - Real-time rule validation")
        print(f"   - Performance metrics tracking")
        
        time.sleep(2)  # Brief pause for audience
    
    def competition_phase(self):
        """Main competition phase"""
        print("\n⚔️  COMPETITION PHASE")
        print("-" * 30)
        
        # Start competition
        self.competition.start_competition()
        
        # Simulate AI analysis
        print("🤖 PERSEPTOR AI is analyzing the threat report...")
        ai_rule_ids = self.ai_participant.analyze_and_generate_rules(
            self.competition.threat_report
        )
        
        # Simulate human participants working
        print("👥 Human experts are working on detection rules...")
        
        # Simulate rule generation over time
        self.simulate_competition_progress()
        
        # End competition
        leaderboard = self.competition.end_competition()
        
        return leaderboard
    
    def simulate_competition_progress(self):
        """Simulate competition progress with updates"""
        duration = self.config['competition_setup']['duration_minutes']
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration)
        
        # Progress updates every 10 minutes
        update_interval = 10  # minutes
        updates = duration // update_interval
        
        for i in range(updates):
            time.sleep(2)  # Simulate time passage
            
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            remaining = (end_time - datetime.now()).total_seconds() / 60
            
            print(f"\n⏰ Progress Update - {elapsed:.0f} minutes elapsed, {remaining:.0f} minutes remaining")
            
            # Show current status
            status = self.competition.get_competition_status()
            print(f"📊 Current Status:")
            print(f"   - Total Rules Generated: {status['total_rules']}")
            print(f"   - Active Participants: {status['participants']}")
            
            # Show leaderboard
            leaderboard = status['leaderboard']
            if leaderboard:
                print(f"🏆 Current Leaderboard:")
                for j, entry in enumerate(leaderboard[:3], 1):
                    emoji = "🥇" if j == 1 else "🥈" if j == 2 else "🥉"
                    print(f"   {emoji} {entry['name']} ({entry['type']}) - Score: {entry['score']} - Rules: {entry['rules_count']}")
        
        # Final update
        print(f"\n⏰ Final Update - {duration} minutes completed!")
    
    def post_competition_phase(self):
        """Post-competition analysis and discussion"""
        print("\n📊 POST-COMPETITION PHASE")
        print("-" * 30)
        
        # Show final results
        leaderboard = self.competition.get_competition_status()['leaderboard']
        
        print("🏆 FINAL RESULTS:")
        for i, entry in enumerate(leaderboard, 1):
            emoji = "🥇" if i == 1 else "🥈" if j == 2 else "🥉" if i == 3 else "📊"
            print(f"   {emoji} {entry['name']} ({entry['type']})")
            print(f"      Score: {entry['score']}")
            print(f"      Rules Generated: {entry['rules_count']}")
            print(f"      Valid Rules: {entry['valid_rules']}")
            print()
        
        # Analysis and insights
        print("🔍 Analysis and Insights:")
        
        # AI vs Human comparison
        ai_entry = next((e for e in leaderboard if e['type'] == 'ai'), None)
        human_entries = [e for e in leaderboard if e['type'] == 'human']
        
        if ai_entry and human_entries:
            avg_human_score = sum(e['score'] for e in human_entries) / len(human_entries)
            print(f"   - AI Score: {ai_entry['score']}")
            print(f"   - Average Human Score: {avg_human_score:.1f}")
            
            if ai_entry['score'] > avg_human_score:
                print("   - AI outperformed human average")
            else:
                print("   - Humans outperformed AI")
        
        # Key learnings
        print("\n💡 Key Learnings:")
        print("   - AI can accelerate threat analysis and rule generation")
        print("   - Human expertise remains valuable for complex scenarios")
        print("   - Hybrid approaches may offer the best results")
        print("   - Real-time validation improves rule quality")
        
        # Best practices
        print("\n🎯 Best Practices:")
        print("   - Combine AI automation with human oversight")
        print("   - Validate AI-generated rules thoroughly")
        print("   - Use lab environments for testing")
        print("   - Implement continuous learning and improvement")
        
        # Q&A session
        print("\n❓ Q&A Session:")
        print("   - Questions from audience")
        print("   - Technical discussions")
        print("   - Future collaboration opportunities")
        print("   - Platform adoption inquiries")
    
    def generate_workshop_report(self):
        """Generate comprehensive workshop report"""
        print("\n📄 Generating workshop report...")
        
        report = {
            "workshop_metadata": self.config['workshop_metadata'],
            "competition_results": {
                "start_time": self.workshop_start_time.isoformat(),
                "end_time": self.workshop_end_time.isoformat(),
                "duration_minutes": (self.workshop_end_time - self.workshop_start_time).total_seconds() / 60,
                "participants": len(self.competition.participants),
                "total_rules": len(self.competition.rules),
                "threat_report": self.competition.threat_report.title if self.competition.threat_report else None
            },
            "final_leaderboard": self.competition.get_competition_status()['leaderboard'],
            "lab_environment_stats": {
                "scenarios_tested": len(self.lab_environment.scenarios),
                "total_events": len(self.lab_environment.events),
                "malicious_events": len(self.lab_environment.get_malicious_events()),
                "benign_events": len(self.lab_environment.get_benign_events())
            },
            "ai_performance": {
                "rules_generated": len([r for r in self.competition.rules.values() if r.participant_id == self.ai_participant.participant_id]),
                "average_confidence": 0.85,  # Placeholder
                "validation_success_rate": 0.92  # Placeholder
            },
            "recommendations": [
                "Implement AI-assisted detection engineering workflows",
                "Establish lab environments for rule validation",
                "Develop hybrid human-AI collaboration frameworks",
                "Create continuous learning and improvement processes"
            ]
        }
        
        # Save report
        report_filename = f"workshop_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Workshop report saved: {report_filename}")
        return report

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='DEATHCon Workshop Orchestrator')
    parser.add_argument('--config', default='workshop_config.json', help='Configuration file path')
    parser.add_argument('--mode', choices=['demo', 'live'], default='demo', help='Execution mode')
    parser.add_argument('--duration', type=int, help='Override competition duration in minutes')
    
    args = parser.parse_args()
    
    print("🎯 DEATHCon Workshop Orchestrator")
    print("=" * 40)
    
    # Initialize orchestrator
    orchestrator = WorkshopOrchestrator(args.config)
    
    # Override duration if specified
    if args.duration:
        orchestrator.config['competition_setup']['duration_minutes'] = args.duration
    
    try:
        # Initialize workshop
        orchestrator.initialize_workshop()
        
        # Setup participants
        orchestrator.setup_participants()
        
        # Select threat report
        orchestrator.select_threat_report()
        
        # Start workshop
        orchestrator.start_workshop()
        
        # Generate report
        orchestrator.generate_workshop_report()
        
        print("\n🎉 Workshop completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Workshop interrupted by user")
    except Exception as e:
        print(f"\n❌ Workshop error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
