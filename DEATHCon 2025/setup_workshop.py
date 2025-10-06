#!/usr/bin/env python3
"""
DEATHCon 2025 Workshop Setup Script
Human vs AI Detection Engineering Challenge

This script helps participants prepare for the workshop by:
1. Setting up the required environment
2. Validating prerequisites
3. Testing PERSEPTOR connection
4. Preparing workspace
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

class WorkshopSetup:
    def __init__(self):
        self.workshop_dir = Path("DEATHCon 2025")
        self.perseptor_dir = Path("..")
        self.setup_log = []
        
    def log(self, message, level="INFO"):
        """Log setup progress"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.setup_log.append(log_entry)
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        self.log("Checking prerequisites...")
        
        prerequisites = {
            "Python 3.8+": self.check_python_version(),
            "Node.js 16+": self.check_node_version(),
            "Git": self.check_git(),
            "OpenAI API Key": self.check_openai_key(),
            "Internet Connection": self.check_internet()
        }
        
        all_good = True
        for prereq, status in prerequisites.items():
            if status:
                self.log(f"✅ {prereq}: OK")
            else:
                self.log(f"❌ {prereq}: MISSING", "ERROR")
                all_good = False
                
        return all_good
        
    def check_python_version(self):
        """Check Python version"""
        try:
            version = sys.version_info
            return version.major == 3 and version.minor >= 8
        except:
            return False
            
    def check_node_version(self):
        """Check Node.js version"""
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().lstrip('v')
                major = int(version.split('.')[0])
                return major >= 16
        except:
            pass
        return False
        
    def check_git(self):
        """Check if Git is installed"""
        try:
            subprocess.run(["git", "--version"], 
                         capture_output=True, text=True)
            return True
        except:
            return False
            
    def check_openai_key(self):
        """Check if OpenAI API key is set"""
        return bool(os.getenv("OPENAI_API_KEY"))
        
    def check_internet(self):
        """Check internet connection"""
        try:
            requests.get("https://api.openai.com", timeout=5)
            return True
        except:
            return False
            
    def setup_workspace(self):
        """Set up workshop workspace"""
        self.log("Setting up workshop workspace...")
        
        # Create workshop directories
        directories = [
            "workspace",
            "workspace/analysis",
            "workspace/rules",
            "workspace/comparison",
            "workspace/submissions"
        ]
        
        for directory in directories:
            dir_path = self.workshop_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.log(f"Created directory: {dir_path}")
            
        # Copy template files
        template_files = [
            "workshop_template.md",
            "README.md"
        ]
        
        for template in template_files:
            src = self.workshop_dir / template
            dst = self.workshop_dir / "workspace" / f"my_{template}"
            if src.exists():
                import shutil
                shutil.copy2(src, dst)
                self.log(f"Copied template: {template}")
                
    def test_perseptor(self):
        """Test PERSEPTOR connection"""
        self.log("Testing PERSEPTOR connection...")
        
        try:
            # Test if PERSEPTOR API is running
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ PERSEPTOR API: Running")
                return True
            else:
                self.log("❌ PERSEPTOR API: Not responding", "WARNING")
                return False
        except:
            self.log("❌ PERSEPTOR API: Not running", "WARNING")
            self.log("Please start PERSEPTOR with: python3 api/app.py", "INFO")
            return False
            
    def create_workshop_config(self):
        """Create workshop configuration file"""
        config = {
            "workshop": {
                "name": "DEATHCon 2025 - Human vs AI Challenge",
                "date": "2025-11-08",
                "duration_minutes": 60,
                "participant_id": f"participant_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "phases": {
                    "manual_analysis": 30,
                    "sigmahq_integration": 15,
                    "ai_comparison": 15
                }
            },
            "perseptor": {
                "api_url": "http://localhost:5000",
                "frontend_url": "http://localhost:3000"
            },
            "resources": {
                "sigmahq_url": "https://github.com/SigmaHQ/sigma",
                "mitre_attack": "https://attack.mitre.org/",
                "yara_rules": "https://github.com/Yara-Rules/rules"
            }
        }
        
        config_path = self.workshop_dir / "workspace" / "workshop_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        self.log(f"Created workshop config: {config_path}")
        
    def generate_participant_id(self):
        """Generate unique participant ID"""
        participant_id = f"DEATHCon2025_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log(f"Your Participant ID: {participant_id}")
        return participant_id
        
    def save_setup_log(self):
        """Save setup log to file"""
        log_path = self.workshop_dir / "workspace" / "setup_log.txt"
        with open(log_path, 'w') as f:
            f.write("DEATHCon 2025 Workshop Setup Log\n")
            f.write("=" * 50 + "\n\n")
            for entry in self.setup_log:
                f.write(entry + "\n")
                
        self.log(f"Setup log saved: {log_path}")
        
    def run_setup(self):
        """Run complete workshop setup"""
        self.log("🚀 Starting DEATHCon 2025 Workshop Setup")
        self.log("=" * 50)
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.log("❌ Prerequisites check failed!", "ERROR")
            self.log("Please install missing requirements and try again.", "INFO")
            return False
            
        # Setup workspace
        self.setup_workspace()
        
        # Test PERSEPTOR
        perseptor_ok = self.test_perseptor()
        
        # Create config
        self.create_workshop_config()
        
        # Generate participant ID
        participant_id = self.generate_participant_id()
        
        # Save log
        self.save_setup_log()
        
        # Final status
        self.log("=" * 50)
        if perseptor_ok:
            self.log("✅ Workshop setup completed successfully!")
        else:
            self.log("⚠️ Workshop setup completed with warnings!")
            self.log("PERSEPTOR is not running. Start it with: python3 api/app.py", "INFO")
            
        self.log(f"Your workspace is ready: {self.workshop_dir / 'workspace'}")
        self.log("Good luck with the challenge! 🏆")
        
        return True

def main():
    """Main setup function"""
    print("🐉 DEATHCon 2025 Workshop Setup")
    print("Human vs AI Detection Engineering Challenge")
    print("=" * 50)
    
    setup = WorkshopSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 Setup completed! You're ready for the workshop!")
        print("📁 Check your workspace in: DEATHCon 2025/workspace/")
    else:
        print("\n❌ Setup failed. Please check the requirements.")
        sys.exit(1)

if __name__ == "__main__":
    main()
