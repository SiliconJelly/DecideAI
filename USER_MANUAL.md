# 📖 DecideAI User Manual

## For German & Japanese Institutions

Welcome to DecideAI - your AI-powered HR helper system designed specifically for German and Japanese universities and SMEs.

## 🎯 What is DecideAI?

DecideAI helps you make better HR decisions by:
- 🤖 **AI-Powered Insights**: Ask questions about your employees in natural language
- 🌍 **Multilingual Support**: Works in German, Japanese, and English
- 🏛️ **Institution-Focused**: Designed for universities and SMEs
- 🔒 **Privacy-First**: All processing happens locally on your computer
- 📊 **Smart Analytics**: Get insights about skills, teams, and projects

## 🚀 Getting Started

### Step 1: Access the System
1. Open your web browser
2. Go to: http://localhost:7860
3. You'll see the DecideAI login screen

### Step 2: Login
- **Username**: `admin`
- **Password**: `AdminPassword123!`
- Click "Login"

### Step 3: Upload Your Employee Data
1. Click on "Employees" tab
2. Click "Bulk Upload"
3. Upload your CSV file (or use our sample_employees.csv)
4. Review the results

## 📊 Using the System

### Main Interface Sections

#### 1. Dashboard
- Overview of your employees
- Quick statistics
- Recent activities

#### 2. Employees
- **View All**: See all employees
- **Add New**: Add individual employees
- **Bulk Upload**: Upload CSV files
- **Search**: Find specific employees

#### 3. AI Assistant
- **Natural Language Queries**: Ask questions about your employees
- **Multilingual Support**: Ask in German, Japanese, or English
- **Smart Suggestions**: Get AI-powered recommendations

#### 4. Documents
- **Upload CVs**: Process resumes automatically
- **Certificates**: Store and analyze certificates
- **OCR Processing**: Extract text from images and PDFs

## 🗣️ Asking AI Questions

### English Examples
```
"Who are our employees?"
"Who has Python programming skills?"
"Suggest a team for a web development project"
"Who works in the Engineering department?"
```

### German Examples (Deutsch)
```
"Wer sind unsere Mitarbeiter?"
"Welche Professoren haben KI-Expertise?"
"Wer arbeitet in der Informatik-Abteilung?"
"Schlagen Sie ein Team für Machine Learning vor"
```

### Japanese Examples (日本語)
```
"私たちの従業員は誰ですか？"
"機械学習の経験がある従業員は誰ですか？"
"Pythonプロジェクトに最適な人は誰ですか？"
"Web開発チームを提案してください"
```

## 📋 Managing Employee Data

### Adding Employees Individually
1. Go to "Employees" → "Add New"
2. Fill in the form:
   - **Basic Info**: Name, email, position
   - **Department**: Select or type department
   - **Skills**: Add relevant skills
   - **Hire Date**: When they joined
3. Click "Save"

### Bulk Upload via CSV
1. Prepare your CSV file with columns:
   ```
   first_name,last_name,email,position,department
   ```
2. Go to "Employees" → "Bulk Upload"
3. Select your CSV file
4. Review the preview
5. Click "Upload"

### CSV Template Example
```csv
first_name,last_name,email,position,department
Hans,Müller,hans.mueller@uni-berlin.de,Professor,Computer Science
Yuki,Tanaka,yuki.tanaka@tokyo-tech.ac.jp,Associate Professor,AI Research
Anna,Schmidt,anna.schmidt@company.de,Senior Developer,Engineering
```

## 📄 Document Processing

### Uploading CVs and Certificates
1. Go to "Documents" tab
2. Click "Upload Document"
3. Select the employee
4. Choose document type (CV, Certificate, etc.)
5. Upload the file (PDF or image)
6. The system will automatically extract information

### OCR Features
- **Text Extraction**: Automatically extract text from images
- **Multilingual OCR**: Supports German, Japanese, and English documents
- **Smart Parsing**: Identifies skills, experience, and qualifications

## 🔍 Search and Filtering

### Quick Search
- Use the search box to find employees by name, email, or skills
- Search works across all employee data

### Advanced Filtering
- **Department**: Filter by department
- **Skills**: Find employees with specific skills
- **Position**: Filter by job title
- **Hire Date**: Filter by when they joined

## 🎯 Use Cases by Institution Type

### German Universities
- **Faculty Management**: Track professors and researchers
- **Research Teams**: Form interdisciplinary research groups
- **Skill Mapping**: Identify expertise across departments
- **Compliance**: GDPR-compliant data management

### Japanese Universities
- **Academic Staff**: Manage faculty and research staff
- **Collaboration**: Find researchers for joint projects
- **Hierarchical Structure**: Respect academic hierarchies
- **Cultural Awareness**: Japanese business etiquette integration

### German SMEs (Mittelstand)
- **Team Building**: Form project teams efficiently
- **Skill Development**: Identify training needs
- **Succession Planning**: Plan for leadership transitions
- **Compliance**: German labor law compliance

### Japanese SMEs
- **Project Assignment**: Assign staff to projects
- **Skill Assessment**: Evaluate team capabilities
- **Decision Support**: Support consensus-building (nemawashi)
- **Growth Planning**: Plan team expansion

## ⚙️ Settings and Configuration

### Language Settings
1. Go to "Settings"
2. Select your preferred language:
   - **Deutsch** (German)
   - **日本語** (Japanese)
   - **English**
3. Save changes

### User Management
1. Go to "Settings" → "Users"
2. Add new users with appropriate roles:
   - **Admin**: Full access
   - **HR Manager**: Employee management
   - **Viewer**: Read-only access

### Data Export
1. Go to "Settings" → "Export"
2. Choose export format (CSV, Excel, PDF)
3. Select data to export
4. Download the file

## 🔐 Security and Privacy

### Data Privacy
- **Local Processing**: All data stays on your computer
- **No Cloud**: No data sent to external servers
- **Encryption**: Data encrypted at rest
- **Access Control**: Role-based permissions

### GDPR Compliance (German Institutions)
- **Right to Access**: Employees can request their data
- **Right to Deletion**: Delete employee data when requested
- **Data Minimization**: Only collect necessary data
- **Audit Trail**: Track all data access and changes

### Privacy Best Practices (Japanese Institutions)
- **Consent Management**: Track data usage consent
- **Data Minimization**: Collect only essential information
- **Access Logging**: Monitor who accesses what data
- **Regular Audits**: Review data usage regularly

## 🆘 Troubleshooting

### Common Issues

#### "Cannot connect to AI service"
- **Solution**: Restart the system with `python START_DECIDEAI.py`

#### "Upload failed"
- **Check**: File format (CSV, PDF, or image)
- **Check**: File size (under 50MB)
- **Check**: File encoding (UTF-8 recommended)

#### "AI not responding in my language"
- **Check**: Language settings in preferences
- **Try**: Asking the same question in English first

#### "Slow performance"
- **Check**: Available RAM (8GB minimum)
- **Check**: Hard drive space (10GB minimum)
- **Try**: Restart the system

### Getting Help
1. **Check Logs**: Look in the logs/ folder for error messages
2. **Restart System**: Try restarting with `python START_DECIDEAI.py`
3. **Contact Support**: Reach out to your IT department
4. **Documentation**: Check README.md for technical details

## 📈 Best Practices

### Data Management
- **Regular Backups**: Export your data regularly
- **Clean Data**: Keep employee information up to date
- **Consistent Format**: Use consistent naming and formatting
- **Regular Reviews**: Review and update employee skills

### AI Usage
- **Clear Questions**: Ask specific, clear questions
- **Context**: Provide context for better answers
- **Verify Results**: Always verify AI suggestions
- **Learn Patterns**: Learn what types of questions work best

### Security
- **Change Default Password**: Change the admin password
- **Regular Updates**: Keep the system updated
- **User Training**: Train users on security best practices
- **Access Control**: Give users only necessary permissions

## 🎉 Success Tips

### For HR Managers
- Start with sample data to learn the system
- Upload your real data gradually
- Train your team on the AI features
- Use multilingual capabilities for international staff

### For IT Administrators
- Monitor system performance regularly
- Set up automated backups
- Plan for user training sessions
- Keep documentation updated

### For End Users
- Experiment with different question formats
- Use the language you're most comfortable with
- Provide feedback on AI responses
- Explore all features gradually

---

## 🎯 Ready to Use DecideAI?

You now have everything you need to use DecideAI effectively in your German or Japanese institution. Start with the sample data, then gradually add your real employee information.

**Remember**: DecideAI is designed to assist your HR decisions, not replace human judgment. Always verify important decisions with your team.

**Need more help?** Check the PRODUCTION_DEPLOYMENT_GUIDE.md for technical details or contact your system administrator.