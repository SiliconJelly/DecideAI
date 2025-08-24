# DecideAI - HR Helper System

## AI-Powered HR Decision Support for German & Japanese Institutions

DecideAI is an advanced AI-powered HR decision support system specifically designed for German and Japanese institutions including universities and small-to-medium enterprises (SMEs). The system combines multilingual AI capabilities with local processing to provide intelligent HR management and employee decision support with cultural awareness and local compliance.

### Key Features

- **Multilingual HR Support**: Native German and Japanese language support with cultural awareness
- **University & SME Focused**: Tailored for academic institutions and small-medium enterprises
- **AI-Powered Employee Decisions**: Natural language queries for HR decision support
- **Local AI Processing**: Uses Ollama for completely offline AI inference
- **Privacy-First Design**: Complete offline operation with local data processing
- **Compliance Ready**: GDPR compliant for German institutions, privacy-focused for Japanese organizations

### Project Structure

```
DecideAI/
├── 🌐 frontend/                 # React web application
├── 🔧 backend/                  # FastAPI backend
├── 🧠 ai_employee_decision_system/  # Core HR AI system
│   ├── ai/                     # AI processing modules
│   ├── api/                    # API endpoints
│   ├── auth/                   # Authentication system
│   ├── models/                 # Data models (Employee, Skills, etc.)
│   ├── services/               # Business logic & AI services
│   ├── locales/                # German, Japanese, English translations
│   └── ui/                     # User interface components

├── 🐳 deployment/              # Docker, K8s deployment
├── 📊 monitoring/              # System monitoring
└── 🧪 testing/                # Test suites and data
```

## 🚀 Quick Start (No Technical Knowledge Required!)

### Option 1: One-Click Deployment (Recommended)
```bash
# Download and run the automated deployment script
python DEPLOY_DECIDEAI.py
```
This script will:
- ✅ Install all dependencies automatically
- ✅ Set up the AI engine (Ollama)
- ✅ Initialize the database
- ✅ Download required AI models
- ✅ Start the system

### Option 2: Simple Startup (If Already Deployed)
```bash
# Start the system
python START_DECIDEAI.py
```

### Option 3: Docker Deployment (For IT Departments)
```bash
# Production deployment with Docker
docker-compose up -d

# Initialize AI models (first time only)
docker-compose --profile init up model-init
```

## 📋 System Requirements

### Minimum Requirements:
- **OS**: Windows 10+, macOS 10.15+, or Linux
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **Python**: 3.8+ (automatically checked)

### What Gets Installed:
- ✅ DecideAI HR Helper System
- ✅ Ollama AI Engine (local, private)
- ✅ Required AI models for German/Japanese support
- ✅ Web interface and API

## 🎯 After Installation

### Access Your System:
- **Web Interface**: http://localhost:7860
- **API Documentation**: http://localhost:8000/docs
- **Default Login**: admin / AdminPassword123!

### First Steps:
1. **Upload Sample Data**: Use `sample_employees.csv`
2. **Try Multilingual Queries**:
   - English: "Who are our employees?"
   - German: "Welche Professoren haben KI-Expertise?"
   - Japanese: "機械学習の経験がある従業員は誰ですか？"

### Target Institutions

#### German Institutions
- **Universities**: Technical universities, research institutions, Fachhochschulen
- **SMEs**: German Mittelstand companies, startups, consulting firms
- **Compliance**: GDPR-compliant, German labor law awareness

#### Japanese Institutions  
- **Universities**: National, public, and private universities, research institutes
- **SMEs**: Japanese small-medium enterprises, technology companies
- **Cultural Awareness**: Japanese business etiquette, hierarchical structures

## 🛠️ Tech Stack

**Backend:** Python FastAPI, SQLAlchemy, SQLite/PostgreSQL, Pydantic  
**AI/ML:** Ollama, Llama2 7B Chat, Local LLM inference  
**Frontend:** React, Next.js, Gradio, TypeScript  
**Auth:** JWT tokens, Bcrypt, Role-based access  
**Deployment:** Docker, Kubernetes, GitHub Actions  
**Testing:** pytest, Tox, Pre-commit hooks  

## 🚀 Micro SaaS Ready

DecideAI is designed as a micro SaaS solution for:
- **Self-hosted deployments** for privacy-conscious organizations
- **Cloud SaaS offerings** with multi-tenant architecture
- **White-label solutions** for HR consultancies
- **Enterprise on-premise** installations

## 📈 Business Model

- **Freemium**: Basic features for small teams (up to 10 employees)
- **Professional**: Advanced AI features and integrations ($29/month)
- **Enterprise**: Custom deployment and support ($99/month)
- **White-label**: Partner program for resellers

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

© 2025 DecideAI - HR Helper System