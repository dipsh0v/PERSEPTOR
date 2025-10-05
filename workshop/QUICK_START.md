# DEATHCon Workshop - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

This guide will help you quickly set up and run the DEATHCon workshop demonstration.

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Git (optional)

### 1. Environment Setup

```bash
# Clone or download the workshop files
cd workshop/

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export WORKSHOP_MODE="demo"
```

### 2. Quick Demo Run

```bash
# Run the workshop demo (30 minutes)
python run_workshop.py --mode demo --duration 30

# Or run with custom configuration
python run_workshop.py --config workshop_config.json --mode demo
```

### 3. Deploy Workshop Environment

```bash
# Setup local environment
python deploy_workshop.py --environment local --action setup

# Deploy to cloud (simulated)
python deploy_workshop.py --environment cloud --action deploy

# Run health checks
python deploy_workshop.py --action monitor
```

### 4. Test Individual Components

```bash
# Test competition setup
python competition_setup.py

# Test lab environment
python lab_environment_setup.py

# Test threat reports
python -c "import json; print(json.load(open('sample_threat_reports.json'))['workshop_threat_reports'][0]['title'])"
```

## 📊 Workshop Components

### Core Files

- **`run_workshop.py`** - Main workshop orchestrator
- **`competition_setup.py`** - Human vs AI competition logic
- **`lab_environment_setup.py`** - Test scenarios and validation
- **`deploy_workshop.py`** - Deployment and infrastructure
- **`workshop_config.json`** - Workshop configuration
- **`sample_threat_reports.json`** - Threat intelligence reports

### Configuration

Edit `workshop_config.json` to customize:
- Competition duration
- Scoring weights
- Threat report selection
- Lab environment settings
- AI model configuration

## 🎯 Workshop Flow

1. **Pre-Competition** (10 min)
   - Introduction to PERSEPTOR
   - Competition rules explanation
   - Lab environment demo

2. **Competition** (45 min)
   - Threat report revealed
   - Live rule generation
   - Real-time scoring
   - Audience engagement

3. **Post-Competition** (5 min)
   - Results announcement
   - Analysis and insights
   - Q&A session

## 🔧 Customization

### Adding New Threat Reports

1. Edit `sample_threat_reports.json`
2. Add new report with required fields:
   - `id`, `title`, `content`, `difficulty`
   - `expected_rules`, `metadata`

### Modifying Scoring

1. Edit `workshop_config.json`
2. Adjust `scoring_system.weights`
3. Add custom bonus/penalty rules

### Lab Environment

1. Edit `lab_environment_setup.py`
2. Add new event generators
3. Create custom test scenarios

## 📈 Monitoring

### Health Checks

```bash
# Check all components
python deploy_workshop.py --action monitor

# Test specific components
python -c "from lab_environment_setup import LabEnvironment; print('Lab OK' if LabEnvironment() else 'Lab Error')"
```

### Logs and Reports

- Workshop reports: `workshop_report_*.json`
- Deployment reports: `deployment_report_*.json`
- Sample events: `sample_lab_events.json`

## 🆘 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lab Environment Issues**
   ```bash
   python lab_environment_setup.py
   ```

4. **Competition Setup Errors**
   ```bash
   python competition_setup.py
   ```

### Debug Mode

```bash
# Run with verbose output
python run_workshop.py --mode demo --duration 5 2>&1 | tee workshop.log
```

## 📞 Support

- **Documentation**: `README.md`
- **Configuration**: `workshop_config.json`
- **Examples**: `sample_threat_reports.json`
- **Issues**: GitHub Issues

## 🎉 Next Steps

1. **Customize** the workshop for your needs
2. **Test** with different threat reports
3. **Deploy** to cloud infrastructure
4. **Run** live workshop
5. **Gather** feedback and improve

---

**Ready to revolutionize detection engineering with AI? Let's go! 🚀**
