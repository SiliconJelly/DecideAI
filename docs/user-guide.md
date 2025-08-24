# AI Employee Decision System - User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Web Interface](#web-interface)
3. [Employee Management](#employee-management)
4. [Document Processing](#document-processing)
5. [AI-Powered Queries](#ai-powered-queries)
6. [Project Management](#project-management)
7. [Skills and Specializations](#skills-and-specializations)
8. [Reports and Analytics](#reports-and-analytics)
9. [User Management](#user-management)
10. [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Setup

1. **Access the System**
   - Open your web browser and navigate to the system URL
   - Default: http://localhost:7860 (web interface) or http://localhost:8000/docs (API)

2. **Create Your Account**
   - Click "Register" on the login page
   - Fill in your details:
     - Email address
     - Username
     - Strong password (minimum 8 characters with uppercase, lowercase, number, and special character)
     - First and last name
   - Click "Create Account"

3. **Login**
   - Enter your username and password
   - Click "Login"
   - You'll be redirected to the main dashboard

### Dashboard Overview

The main dashboard provides:
- **Quick Stats**: Number of employees, documents processed, active projects
- **Recent Activity**: Latest document uploads and AI queries
- **Quick Actions**: Common tasks like adding employees or uploading documents
- **AI Chat**: Natural language interface for quick queries

## Web Interface

### Navigation

The web interface is organized into several main sections:

- **Dashboard**: Overview and quick actions
- **Employees**: Manage employee profiles
- **Documents**: Upload and process documents
- **Projects**: Manage projects and team assignments
- **AI Assistant**: Natural language query interface
- **Reports**: Analytics and reporting tools
- **Settings**: System configuration and user management

### Using the AI Chat Interface

The AI chat interface allows you to ask questions in natural language:

1. **Type your question** in the chat box at the bottom
2. **Press Enter** or click "Send"
3. **Review the response** from the AI assistant
4. **Ask follow-up questions** for more details

#### Example Questions:
- "Who are our best Python developers?"
- "Show me employees with machine learning experience"
- "Suggest a team for a web development project"
- "What skills does John Doe have?"
- "Who should we consider for promotion to senior developer?"

## Employee Management

### Adding New Employees

1. **Navigate to Employees** section
2. **Click "Add Employee"**
3. **Fill in the form**:
   - Personal Information: Name, email, phone
   - Employment Details: Department, position, hire date
   - Skills: Select from existing skills or add new ones
   - Specializations: Choose relevant specializations
4. **Click "Save Employee"**

### Editing Employee Profiles

1. **Find the employee** using search or browse
2. **Click on the employee name** to open their profile
3. **Click "Edit Profile"**
4. **Update the information** as needed
5. **Click "Save Changes"**

### Managing Employee Skills

#### Adding Skills to an Employee:
1. Open the employee's profile
2. Go to the "Skills" tab
3. Click "Add Skill"
4. Select skill from dropdown or create new
5. Set proficiency level (Beginner, Intermediate, Advanced, Expert)
6. Add notes if needed
7. Click "Save"

#### Skill Verification:
- Skills can be verified through document analysis
- Upload CVs or certificates to automatically extract skills
- Manual verification by administrators
- Confidence scores show reliability of skill assessments

### Employee Search and Filtering

Use the search functionality to find employees:

- **Text Search**: Search by name, email, or department
- **Skill Filter**: Find employees with specific skills
- **Department Filter**: Filter by department or position
- **Advanced Search**: Combine multiple criteria

## Document Processing

### Uploading Documents

1. **Select an employee** from the employee list
2. **Click "Upload Document"**
3. **Choose document type**:
   - CV/Resume
   - Certificate
   - Performance Review
   - Other
4. **Drag and drop** the file or click "Browse"
5. **Click "Upload"**

### Supported File Types

- **PDF files** (.pdf)
- **Image files** (.jpg, .jpeg, .png, .tiff, .bmp)
- **Maximum file size**: 10MB

### Document Processing Pipeline

After upload, documents go through automatic processing:

1. **OCR Processing**: Text extraction from images and PDFs
2. **Language Detection**: Automatic detection of document language
3. **AI Analysis**: Extraction of structured information
4. **Skill Extraction**: Identification of skills and experience
5. **Confidence Scoring**: Reliability assessment of extracted data

### Reviewing Processed Documents

1. **Go to Documents** section
2. **Click on a document** to view details
3. **Review extracted information**:
   - Raw text from OCR
   - Structured data (name, email, skills, etc.)
   - Confidence scores
4. **Verify and correct** information if needed
5. **Approve or reject** extracted data

### Document Status Indicators

- **Pending**: Uploaded but not yet processed
- **Processing**: Currently being analyzed
- **Completed**: Successfully processed
- **Failed**: Processing encountered errors
- **Verified**: Human-verified information

## AI-Powered Queries

### Types of Queries

The AI system can handle various types of questions:

#### Employee Recommendations:
- "Who is the best candidate for a senior developer position?"
- "Find employees with both Python and machine learning skills"
- "Who has the most experience in project management?"

#### Team Suggestions:
- "Suggest a team of 5 for a mobile app project"
- "Who should work together on a data science project?"
- "Create a balanced team for a full-stack web project"

#### Skill Analysis:
- "What are the most common skills in our engineering team?"
- "Which employees need training in cloud technologies?"
- "Show me the skill distribution across departments"

#### Career Development:
- "Who is ready for promotion to team lead?"
- "What skills should John develop for career advancement?"
- "Find mentorship opportunities for junior developers"

### Query Context

Provide additional context to get better results:

```
Query: "Suggest a team for a machine learning project"
Context: 
- Project duration: 6 months
- Required skills: Python, TensorFlow, data analysis
- Team size: 4 people
- Experience level: Mix of senior and junior
```

### Understanding AI Responses

AI responses include:
- **Direct Answer**: Main recommendation or information
- **Confidence Score**: How certain the AI is about the response
- **Reasoning**: Why this recommendation was made
- **Alternative Options**: Other possibilities to consider
- **Additional Information**: Related insights or suggestions

## Project Management

### Creating Projects

1. **Go to Projects** section
2. **Click "New Project"**
3. **Fill in project details**:
   - Project name and description
   - Start and end dates
   - Required skills
   - Team size
   - Priority level
4. **Click "Create Project"**

### Team Assignment

#### Manual Assignment:
1. Open the project
2. Click "Assign Team Members"
3. Search and select employees
4. Define roles for each member
5. Save assignments

#### AI-Assisted Assignment:
1. Open the project
2. Click "Get AI Recommendations"
3. Review suggested team members
4. Accept or modify suggestions
5. Finalize team assignments

### Project Tracking

Monitor project progress:
- **Team Overview**: Current team members and roles
- **Skill Coverage**: How well the team covers required skills
- **Workload Analysis**: Team member availability and workload
- **Progress Updates**: Status updates and milestones

## Skills and Specializations

### Skill Management

#### Adding New Skills:
1. Go to **Skills** section
2. Click "Add Skill"
3. Enter skill details:
   - Skill name
   - Category (Technical, Soft Skills, etc.)
   - Description
   - Related skills
4. Save the skill

#### Skill Categories:
- **Programming Languages**: Python, Java, JavaScript, etc.
- **Frameworks**: React, Django, Spring, etc.
- **Tools**: Git, Docker, Kubernetes, etc.
- **Soft Skills**: Leadership, Communication, Problem-solving
- **Domain Knowledge**: Finance, Healthcare, E-commerce

### Specializations

Specializations are broader areas of expertise:
- **Web Development**
- **Data Science**
- **Mobile Development**
- **DevOps**
- **UI/UX Design**
- **Project Management**

### Skill Assessment

#### Proficiency Levels:
- **Beginner** (1-2): Basic understanding
- **Intermediate** (3-4): Can work independently
- **Advanced** (5-6): Can mentor others
- **Expert** (7-8): Industry expert level

#### Assessment Methods:
- **Self-assessment**: Employee rates their own skills
- **Manager assessment**: Supervisor evaluation
- **Document analysis**: Automatic extraction from CVs
- **Peer review**: Colleague feedback
- **Certification**: External certifications and courses

## Reports and Analytics

### Available Reports

#### Employee Reports:
- **Employee Directory**: Complete list with contact information
- **Skills Matrix**: Skills distribution across the organization
- **Department Analysis**: Breakdown by department and role
- **Experience Levels**: Seniority distribution

#### Project Reports:
- **Project Portfolio**: All active and completed projects
- **Resource Allocation**: Team assignments and utilization
- **Skill Gaps**: Missing skills for upcoming projects
- **Performance Metrics**: Project success rates and timelines

#### AI Analytics:
- **Query Statistics**: Most common AI queries
- **Recommendation Accuracy**: Success rate of AI suggestions
- **Usage Patterns**: How the system is being used
- **Processing Metrics**: Document processing statistics

### Generating Reports

1. **Go to Reports** section
2. **Select report type**
3. **Choose date range** and filters
4. **Click "Generate Report"**
5. **View online** or **download** (PDF, Excel, CSV)

### Custom Reports

Create custom reports:
1. Click "Custom Report"
2. Select data sources
3. Choose fields to include
4. Apply filters and sorting
5. Save report template for reuse

## User Management

### User Roles

#### Regular User:
- View employee information
- Upload documents
- Use AI queries
- Generate basic reports

#### Administrator:
- All regular user permissions
- Manage user accounts
- System configuration
- Advanced reports
- Data export/import

### Managing User Accounts (Admin Only)

#### Adding Users:
1. Go to **Settings** > **Users**
2. Click "Add User"
3. Fill in user details
4. Assign role (User or Admin)
5. Send invitation email

#### User Status Management:
- **Active**: Can access the system
- **Inactive**: Account disabled
- **Pending**: Invitation sent but not accepted

### Password Management

#### Changing Your Password:
1. Go to **Settings** > **Profile**
2. Click "Change Password"
3. Enter current password
4. Enter new password (twice)
5. Click "Update Password"

#### Password Requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

## Troubleshooting

### Common Issues

#### Login Problems:
- **Forgot Password**: Use "Forgot Password" link on login page
- **Account Locked**: Contact administrator
- **Invalid Credentials**: Check username and password

#### Document Upload Issues:
- **File Too Large**: Maximum 10MB file size
- **Unsupported Format**: Use PDF or image files
- **Upload Failed**: Check internet connection and try again

#### AI Query Problems:
- **No Response**: Try rephrasing your question
- **Unclear Answer**: Provide more context in your query
- **Slow Response**: System may be processing, please wait

#### Performance Issues:
- **Slow Loading**: Clear browser cache and cookies
- **Timeout Errors**: Refresh the page and try again
- **Browser Compatibility**: Use Chrome, Firefox, or Safari

### Getting Help

#### In-App Help:
- Click the "?" icon for context-sensitive help
- Use the search function in help documentation
- Check tooltips on form fields

#### Contact Support:
- **Email**: support@example.com
- **Help Desk**: Available during business hours
- **Documentation**: Comprehensive guides available online

### Best Practices

#### For Better AI Results:
- Be specific in your queries
- Provide context when possible
- Use proper terminology
- Ask follow-up questions for clarification

#### For Document Processing:
- Use high-quality scans
- Ensure text is readable
- Use standard document formats
- Include complete information

#### For Data Quality:
- Regularly update employee information
- Verify AI-extracted data
- Keep skills and specializations current
- Remove outdated information

### System Maintenance

#### Regular Tasks:
- Update employee information quarterly
- Review and verify document processing results
- Clean up old or irrelevant data
- Update skills and specializations as needed

#### Data Backup:
- System automatically backs up data daily
- Export important data regularly
- Keep local copies of critical documents
- Test data recovery procedures

---

For additional help or questions not covered in this guide, please contact our support team or refer to the technical documentation.