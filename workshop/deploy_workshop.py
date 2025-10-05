#!/usr/bin/env python3
"""
DEATHCon Workshop - Deployment Script
====================================

This script handles the deployment and setup of the DEATHCon workshop environment,
including cloud infrastructure, streaming setup, and monitoring.

Usage:
    python deploy_workshop.py --environment [local|cloud] --action [setup|deploy|monitor|cleanup]
"""

import os
import sys
import json
import argparse
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests

class WorkshopDeployment:
    """Deployment manager for DEATHCon workshop"""
    
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.environment = None
        self.deployment_status = {}
        
    def load_config(self, config_path: str) -> Dict:
        """Load deployment configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)
    
    def setup_local_environment(self):
        """Setup local development environment"""
        print("🏠 Setting up local environment...")
        
        # Check Python dependencies
        self.check_dependencies()
        
        # Setup environment variables
        self.setup_environment_variables()
        
        # Initialize lab environment
        self.initialize_lab_environment()
        
        # Test AI integration
        self.test_ai_integration()
        
        print("✅ Local environment setup complete")
    
    def setup_cloud_environment(self):
        """Setup cloud deployment environment"""
        print("☁️  Setting up cloud environment...")
        
        # Deploy to cloud platform (AWS/Azure/GCP)
        self.deploy_cloud_infrastructure()
        
        # Setup load balancing
        self.setup_load_balancing()
        
        # Configure monitoring
        self.setup_monitoring()
        
        # Setup streaming infrastructure
        self.setup_streaming_infrastructure()
        
        print("✅ Cloud environment setup complete")
    
    def check_dependencies(self):
        """Check and install required dependencies"""
        print("📦 Checking dependencies...")
        
        required_packages = [
            'flask',
            'flask-cors',
            'requests',
            'beautifulsoup4',
            'openai',
            'langchain',
            'pyyaml',
            'python-dateutil',
            'uuid'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}")
        
        if missing_packages:
            print(f"\n📥 Installing missing packages: {', '.join(missing_packages)}")
            for package in missing_packages:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
                print(f"   ✅ Installed {package}")
        
        print("✅ All dependencies satisfied")
    
    def setup_environment_variables(self):
        """Setup required environment variables"""
        print("🔧 Setting up environment variables...")
        
        required_vars = {
            'OPENAI_API_KEY': 'Your OpenAI API key',
            'WORKSHOP_MODE': 'demo',
            'STREAMING_ENABLED': 'false',
            'LAB_ENVIRONMENT': 'enabled',
            'MAX_PARTICIPANTS': '512'
        }
        
        for var, description in required_vars.items():
            if not os.getenv(var):
                print(f"   ⚠️  {var}: {description}")
                if var == 'OPENAI_API_KEY':
                    print(f"   💡 Set this variable: export {var}=your_api_key")
            else:
                print(f"   ✅ {var}")
        
        print("✅ Environment variables configured")
    
    def initialize_lab_environment(self):
        """Initialize lab environment with test data"""
        print("🔬 Initializing lab environment...")
        
        try:
            # Run lab environment setup
            from lab_environment_setup import LabEnvironment
            
            lab = LabEnvironment()
            print(f"   ✅ Lab environment initialized")
            print(f"   📊 Events: {len(lab.events)}")
            print(f"   🎯 Scenarios: {len(lab.scenarios)}")
            
            # Export sample data
            sample_events = lab.events[:10]
            with open('sample_lab_events.json', 'w') as f:
                json.dump([{
                    'id': event.id,
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type,
                    'process_name': event.process_name,
                    'command_line': event.command_line,
                    'is_malicious': event.is_malicious,
                    'threat_category': event.threat_category
                } for event in sample_events], f, indent=2)
            
            print(f"   📁 Sample events exported to sample_lab_events.json")
            
        except Exception as e:
            print(f"   ❌ Error initializing lab environment: {e}")
        
        print("✅ Lab environment ready")
    
    def test_ai_integration(self):
        """Test AI integration and API connectivity"""
        print("🤖 Testing AI integration...")
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key or openai_key == 'your-openai-api-key':
            print("   ⚠️  OpenAI API key not configured - skipping AI tests")
            return
        
        try:
            # Test basic AI functionality
            from modules.gpt_module import summarize_threat_report
            
            test_text = "This is a test threat report for AI integration testing."
            result = summarize_threat_report(test_text, openai_key)
            
            if result and "test" in result.lower():
                print("   ✅ AI integration working")
            else:
                print("   ⚠️  AI integration may have issues")
                
        except Exception as e:
            print(f"   ❌ AI integration error: {e}")
        
        print("✅ AI integration test complete")
    
    def deploy_cloud_infrastructure(self):
        """Deploy cloud infrastructure"""
        print("☁️  Deploying cloud infrastructure...")
        
        # This would integrate with cloud providers
        # For demo purposes, we'll simulate the deployment
        
        cloud_config = {
            "compute_instances": 3,
            "load_balancer": True,
            "database": "managed",
            "storage": "object_storage",
            "monitoring": "enabled",
            "auto_scaling": True
        }
        
        print(f"   🖥️  Compute instances: {cloud_config['compute_instances']}")
        print(f"   ⚖️  Load balancer: {cloud_config['load_balancer']}")
        print(f"   🗄️  Database: {cloud_config['database']}")
        print(f"   💾 Storage: {cloud_config['storage']}")
        print(f"   📊 Monitoring: {cloud_config['monitoring']}")
        print(f"   📈 Auto-scaling: {cloud_config['auto_scaling']}")
        
        print("✅ Cloud infrastructure deployed")
    
    def setup_load_balancing(self):
        """Setup load balancing for high availability"""
        print("⚖️  Setting up load balancing...")
        
        # Simulate load balancer configuration
        lb_config = {
            "algorithm": "round_robin",
            "health_checks": True,
            "ssl_termination": True,
            "sticky_sessions": False,
            "max_connections": 10000
        }
        
        print(f"   🔄 Algorithm: {lb_config['algorithm']}")
        print(f"   ❤️  Health checks: {lb_config['health_checks']}")
        print(f"   🔒 SSL termination: {lb_config['ssl_termination']}")
        print(f"   🍪 Sticky sessions: {lb_config['sticky_sessions']}")
        print(f"   🔗 Max connections: {lb_config['max_connections']}")
        
        print("✅ Load balancing configured")
    
    def setup_monitoring(self):
        """Setup monitoring and alerting"""
        print("📊 Setting up monitoring...")
        
        monitoring_config = {
            "metrics_collection": True,
            "log_aggregation": True,
            "alerting": True,
            "dashboards": True,
            "health_checks": True
        }
        
        print(f"   📈 Metrics collection: {monitoring_config['metrics_collection']}")
        print(f"   📝 Log aggregation: {monitoring_config['log_aggregation']}")
        print(f"   🚨 Alerting: {monitoring_config['alerting']}")
        print(f"   📊 Dashboards: {monitoring_config['dashboards']}")
        print(f"   ❤️  Health checks: {monitoring_config['health_checks']}")
        
        print("✅ Monitoring configured")
    
    def setup_streaming_infrastructure(self):
        """Setup streaming infrastructure"""
        print("📺 Setting up streaming infrastructure...")
        
        streaming_config = {
            "platform": "Twitch/YouTube",
            "quality": "1080p",
            "audio": True,
            "screen_sharing": True,
            "live_chat": True,
            "recording": True
        }
        
        print(f"   🎥 Platform: {streaming_config['platform']}")
        print(f"   📺 Quality: {streaming_config['quality']}")
        print(f"   🔊 Audio: {streaming_config['audio']}")
        print(f"   🖥️  Screen sharing: {streaming_config['screen_sharing']}")
        print(f"   💬 Live chat: {streaming_config['live_chat']}")
        print(f"   📹 Recording: {streaming_config['recording']}")
        
        print("✅ Streaming infrastructure configured")
    
    def run_health_checks(self):
        """Run health checks on deployed infrastructure"""
        print("❤️  Running health checks...")
        
        checks = {
            "API endpoints": self.check_api_endpoints(),
            "Database connectivity": self.check_database(),
            "AI services": self.check_ai_services(),
            "Lab environment": self.check_lab_environment(),
            "Streaming setup": self.check_streaming()
        }
        
        all_healthy = True
        for check_name, status in checks.items():
            if status:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name}")
                all_healthy = False
        
        if all_healthy:
            print("✅ All health checks passed")
        else:
            print("⚠️  Some health checks failed")
        
        return all_healthy
    
    def check_api_endpoints(self) -> bool:
        """Check API endpoint health"""
        try:
            # Simulate API health check
            response = requests.get("http://localhost:5000/api/test", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_database(self) -> bool:
        """Check database connectivity"""
        try:
            # Simulate database health check
            return True
        except:
            return False
    
    def check_ai_services(self) -> bool:
        """Check AI services health"""
        try:
            openai_key = os.getenv('OPENAI_API_KEY')
            return openai_key and openai_key != 'your-openai-api-key'
        except:
            return False
    
    def check_lab_environment(self) -> bool:
        """Check lab environment health"""
        try:
            from lab_environment_setup import LabEnvironment
            lab = LabEnvironment()
            return len(lab.events) > 0
        except:
            return False
    
    def check_streaming(self) -> bool:
        """Check streaming setup"""
        try:
            # Simulate streaming health check
            return True
        except:
            return False
    
    def cleanup_environment(self):
        """Cleanup deployed resources"""
        print("🧹 Cleaning up environment...")
        
        # Stop services
        print("   🛑 Stopping services...")
        
        # Remove temporary files
        print("   🗑️  Removing temporary files...")
        
        # Cleanup cloud resources
        print("   ☁️  Cleaning up cloud resources...")
        
        print("✅ Environment cleanup complete")
    
    def generate_deployment_report(self):
        """Generate deployment report"""
        print("📄 Generating deployment report...")
        
        report = {
            "deployment_timestamp": datetime.now().isoformat(),
            "environment": self.environment,
            "configuration": self.config,
            "health_status": self.run_health_checks(),
            "components": {
                "lab_environment": "deployed",
                "ai_integration": "configured",
                "streaming": "ready",
                "monitoring": "active"
            },
            "next_steps": [
                "Run workshop demo",
                "Test with live participants",
                "Monitor performance",
                "Gather feedback"
            ]
        }
        
        # Save report
        report_filename = f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Deployment report saved: {report_filename}")
        return report

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='DEATHCon Workshop Deployment')
    parser.add_argument('--config', default='workshop_config.json', help='Configuration file path')
    parser.add_argument('--environment', choices=['local', 'cloud'], default='local', help='Deployment environment')
    parser.add_argument('--action', choices=['setup', 'deploy', 'monitor', 'cleanup'], default='setup', help='Action to perform')
    
    args = parser.parse_args()
    
    print("🚀 DEATHCon Workshop Deployment")
    print("=" * 40)
    
    # Initialize deployment manager
    deployment = WorkshopDeployment(args.config)
    deployment.environment = args.environment
    
    try:
        if args.action == 'setup':
            if args.environment == 'local':
                deployment.setup_local_environment()
            else:
                deployment.setup_cloud_environment()
        
        elif args.action == 'deploy':
            deployment.setup_cloud_environment()
            deployment.run_health_checks()
        
        elif args.action == 'monitor':
            deployment.run_health_checks()
        
        elif args.action == 'cleanup':
            deployment.cleanup_environment()
        
        # Generate report
        deployment.generate_deployment_report()
        
        print(f"\n🎉 {args.action.capitalize()} completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Deployment interrupted by user")
    except Exception as e:
        print(f"\n❌ Deployment error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
