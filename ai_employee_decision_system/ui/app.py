"""
Main UI application for the AI Employee Decision System.
"""

import json
import requests
from typing import Tuple, Optional

import gradio as gr

from ai_employee_decision_system.core import config, get_logger

logger = get_logger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:8000"


class EmployeeSystemUI:
    """Main UI class for the Employee Decision System."""
    
    def __init__(self):
        """Initialize the UI."""
        self.logger = get_logger(__name__)
        self.logger.info("Initializing Employee System UI")
        self.token = None
        self.login_status = "Not logged in"
    
    def login(self, username: str, password: str) -> str:
        """Login to the system."""
        if not username or not password:
            return "Please enter both username and password."
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.login_status = f"Logged in as {username}"
                return f"✅ Successfully logged in as {username}!"
            else:
                return f"❌ Login failed: {response.json().get('detail', 'Unknown error')}"
                
        except Exception as e:
            self.logger.error("Login error: %s", str(e))
            return f"❌ Login error: {str(e)}"
    
    def get_headers(self):
        """Get headers with authentication token."""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}
    
    def process_natural_language_query(self, query: str) -> str:
        """Process a natural language query and return response."""
        if not query.strip():
            return "Please enter a question about your employees."
        
        if not self.token:
            return "❌ Please login first to use this feature."
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/ai/query",
                json={"query": query},
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                return f"🤖 {result.get('response', 'No response received')}"
            else:
                return f"❌ Error: {response.json().get('detail', 'Unknown error')}"
                
        except Exception as e:
            self.logger.error("Error processing query: %s", str(e))
            return f"❌ I encountered an error processing your request: {str(e)}"
    
    def add_employee(self, first_name: str, last_name: str, email: str, 
                    position: str, department: str) -> str:
        """Add a new employee to the system."""
        if not all([first_name, last_name, email]):
            return "Please fill in at least the name and email fields."
        
        if not self.token:
            return "❌ Please login first to add employees."
        
        try:
            employee_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "position": position or None,
                "department": department or None
            }
            
            response = requests.post(
                f"{API_BASE_URL}/employees/",
                json=employee_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                employee = response.json()
                return f"✅ Successfully added employee: {employee['first_name']} {employee['last_name']}"
            else:
                return f"❌ Error adding employee: {response.json().get('detail', 'Unknown error')}"
                
        except Exception as e:
            self.logger.error("Error adding employee: %s", str(e))
            return f"❌ Error adding employee: {str(e)}"
    
    def get_employees(self) -> str:
        """Get list of all employees."""
        if not self.token:
            return "❌ Please login first to view employees."
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/employees/",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                employees = response.json()
                if not employees:
                    return "No employees found. Add some employees first!"
                
                result = "👥 **Current Employees:**\n\n"
                for emp in employees:
                    result += f"• **{emp['first_name']} {emp['last_name']}**\n"
                    result += f"  📧 {emp['email']}\n"
                    if emp.get('position'):
                        result += f"  💼 {emp['position']}\n"
                    if emp.get('department'):
                        result += f"  🏢 {emp['department']}\n"
                    result += "\n"
                
                return result
            else:
                return f"❌ Error getting employees: {response.json().get('detail', 'Unknown error')}"
                
        except Exception as e:
            self.logger.error("Error getting employees: %s", str(e))
            return f"❌ Error getting employees: {str(e)}"
    
    def check_system_health(self) -> str:
        """Check system health."""
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                return f"✅ System Status: {data['status']}\n📊 Version: {data['version']}"
            else:
                return f"❌ System health check failed: {response.status_code}"
        except Exception as e:
            return f"❌ Cannot connect to system: {str(e)}"
    
    def bulk_upload_employees(self, file) -> str:
        """Bulk upload employees from CSV file."""
        if not file:
            return "❌ Please select a CSV file to upload."
        
        if not self.token:
            return "❌ Please login first to upload employees."
        
        try:
            # Check if file has the right extension
            if not hasattr(file, 'name') or not file.name.endswith('.csv'):
                return "❌ Please upload a CSV file (.csv extension required)."
            
            # Prepare file for upload
            if hasattr(file, 'read'):
                # File is a file-like object
                file_content = file.read()
                if isinstance(file_content, str):
                    file_content = file_content.encode('utf-8')
                files = {"file": (file.name, file_content, "text/csv")}
            else:
                # File is binary data
                files = {"file": (getattr(file, 'name', 'upload.csv'), file, "text/csv")}
            
            response = requests.post(
                f"{API_BASE_URL}/employees/bulk-upload",
                files=files,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                result = response.json()
                output = f"✅ **Upload Successful!**\n\n"
                output += f"📊 **Summary:**\n"
                output += f"• Created: {result['created_count']} employees\n"
                output += f"• Errors: {result['error_count']}\n\n"
                
                if result.get('employees'):
                    output += f"👥 **Created Employees:**\n"
                    for emp in result['employees'][:5]:  # Show first 5
                        output += f"• {emp['first_name']} {emp['last_name']} ({emp['email']})\n"
                    if len(result['employees']) > 5:
                        output += f"• ... and {len(result['employees']) - 5} more\n"
                
                if result.get('errors'):
                    output += f"\n⚠️ **Errors:**\n"
                    for error in result['errors'][:5]:  # Show first 5 errors
                        output += f"• {error}\n"
                    if len(result['errors']) > 5:
                        output += f"• ... and {len(result['errors']) - 5} more errors\n"
                
                return output
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                return f"❌ Upload failed: {error_detail}"
                
        except Exception as e:
            self.logger.error("Error uploading employees: %s", str(e))
            return f"❌ Error uploading employees: {str(e)}"
    
    def upload_document(self, employee_email: str, doc_type: str, file) -> str:
        """Upload a document for an employee."""
        if not all([employee_email, doc_type, file]):
            return "❌ Please fill in all fields and select a file."
        
        if not self.token:
            return "❌ Please login first to upload documents."
        
        try:
            # First, find the employee ID by email
            response = requests.get(
                f"{API_BASE_URL}/employees/",
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                return f"❌ Error finding employee: {response.json().get('detail', 'Unknown error')}"
            
            employees = response.json()
            employee = None
            for emp in employees:
                if emp['email'].lower() == employee_email.lower():
                    employee = emp
                    break
            
            if not employee:
                return f"❌ Employee with email {employee_email} not found. Please add the employee first."
            
            # Upload the document
            if hasattr(file, 'read'):
                file_content = file.read()
                files = {"file": (file.name, file_content, getattr(file, 'type', None) or "application/octet-stream")}
            else:
                files = {"file": (getattr(file, 'name', 'document'), file, "application/octet-stream")}
            
            data = {"document_type": doc_type}
            
            response = requests.post(
                f"{API_BASE_URL}/employees/{employee['id']}/documents/",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                document = response.json()
                return f"✅ **Document uploaded successfully!**\n\n📄 **Details:**\n• Employee: {employee['first_name']} {employee['last_name']}\n• Document: {document['name']}\n• Type: {document['type']}\n• Size: {document['size']} bytes\n\n💡 You can now process this document to extract skills and information."
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                return f"❌ Document upload failed: {error_detail}"
                
        except Exception as e:
            self.logger.error("Error uploading document: %s", str(e))
            return f"❌ Error uploading document: {str(e)}"


def run_app():
    """Run the Gradio application."""
    logger.info("Starting AI Employee Decision System UI")
    
    ui = EmployeeSystemUI()
    
    # Create the main interface with tabs
    with gr.Blocks(title=config.app_name, theme=gr.themes.Soft()) as demo:
        gr.Markdown(f"# {config.app_name}")
        gr.Markdown("🚀 **Make data-driven organizational decisions about employees using AI**")
        
        # Login Section
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🔐 Login")
                username_input = gr.Textbox(label="Username", placeholder="admin")
                password_input = gr.Textbox(label="Password", type="password", placeholder="AdminPassword123!")
                login_button = gr.Button("Login", variant="primary")
                login_output = gr.Textbox(label="Login Status", value="Not logged in")
                
                login_button.click(
                    ui.login,
                    inputs=[username_input, password_input],
                    outputs=[login_output]
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 🏥 System Status")
                health_button = gr.Button("Check System Health")
                health_output = gr.Textbox(label="System Health")
                
                health_button.click(
                    ui.check_system_health,
                    outputs=[health_output]
                )
        
        gr.Markdown("---")
        
        with gr.Tabs():
            # AI Query Tab
            with gr.TabItem("🤖 Ask AI"):
                gr.Markdown("### Ask questions about your employees in natural language")
                gr.Markdown("**Examples:**")
                gr.Markdown("• *Who is the best employee for a Python project?*")
                gr.Markdown("• *What are the skills of John Doe?*")
                gr.Markdown("• *Suggest a team for a machine learning project*")
                
                with gr.Row():
                    query_input = gr.Textbox(
                        lines=3,
                        placeholder="Ask me anything about your employees...",
                        label="Your Question"
                    )
                
                query_button = gr.Button("🚀 Ask AI", variant="primary")
                query_output = gr.Textbox(label="AI Response", lines=10)
                
                query_button.click(
                    ui.process_natural_language_query,
                    inputs=[query_input],
                    outputs=[query_output]
                )
            
            # Employee Management Tab
            with gr.TabItem("👥 Employees"):
                gr.Markdown("### Employee Management")
                
                with gr.Tabs():
                    with gr.TabItem("View & Add"):
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("#### View Employees")
                                view_emp_button = gr.Button("📋 View All Employees")
                                view_emp_output = gr.Textbox(label="Employee List", lines=15)
                                
                                view_emp_button.click(
                                    ui.get_employees,
                                    outputs=[view_emp_output]
                                )
                            
                            with gr.Column():
                                gr.Markdown("#### Add New Employee")
                                emp_first_name = gr.Textbox(label="First Name", placeholder="John")
                                emp_last_name = gr.Textbox(label="Last Name", placeholder="Doe")
                                emp_email = gr.Textbox(label="Email", placeholder="john.doe@company.com")
                                emp_position = gr.Textbox(label="Position", placeholder="Software Developer")
                                emp_department = gr.Textbox(label="Department", placeholder="Engineering")
                                
                                add_emp_button = gr.Button("➕ Add Employee", variant="primary")
                                add_emp_output = gr.Textbox(label="Result")
                                
                                add_emp_button.click(
                                    ui.add_employee,
                                    inputs=[emp_first_name, emp_last_name, emp_email, emp_position, emp_department],
                                    outputs=[add_emp_output]
                                )
                    
                    with gr.TabItem("Bulk Upload"):
                        gr.Markdown("#### Upload Employee Database")
                        gr.Markdown("Upload a CSV file with employee data. Required columns: `first_name`, `last_name`, `email`. Optional: `position`, `department`")
                        
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("**CSV Format Example:**")
                                gr.Code("""first_name,last_name,email,position,department
John,Doe,john.doe@company.com,Software Developer,Engineering
Jane,Smith,jane.smith@company.com,Data Scientist,AI Research
Mike,Johnson,mike.johnson@company.com,Project Manager,Operations""")
                                
                                bulk_file = gr.File(
                                    label="Employee CSV File",
                                    file_types=[".csv"],
                                    type="binary"
                                )
                                bulk_upload_button = gr.Button("📤 Upload Employees", variant="primary")
                            
                            with gr.Column():
                                bulk_upload_output = gr.Textbox(label="Upload Results", lines=15)
                        
                        bulk_upload_button.click(
                            ui.bulk_upload_employees,
                            inputs=[bulk_file],
                            outputs=[bulk_upload_output]
                        )
                    
                    with gr.TabItem("Document Upload"):
                        gr.Markdown("#### Upload Employee Documents (CVs, Certificates)")
                        
                        with gr.Row():
                            with gr.Column():
                                doc_employee_email = gr.Textbox(
                                    label="Employee Email",
                                    placeholder="john.doe@company.com"
                                )
                                doc_type = gr.Dropdown(
                                    choices=["CV", "Certificate", "Performance Review", "Other"],
                                    label="Document Type",
                                    value="CV"
                                )
                                doc_file = gr.File(
                                    label="Document File",
                                    file_types=[".pdf", ".jpg", ".jpeg", ".png"]
                                )
                                doc_upload_button = gr.Button("📄 Upload Document", variant="primary")
                            
                            with gr.Column():
                                doc_upload_output = gr.Textbox(label="Upload Results", lines=10)
                        
                        doc_upload_button.click(
                            ui.upload_document,
                            inputs=[doc_employee_email, doc_type, doc_file],
                            outputs=[doc_upload_output]
                        )
            
            # API Testing Tab
            with gr.TabItem("🔧 API Test"):
                gr.Markdown("### Test API Endpoints")
                gr.Markdown("Use this tab to test the system functionality")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Quick Tests")
                        gr.Markdown("**Default Admin Credentials:**")
                        gr.Markdown("• Username: `admin`")
                        gr.Markdown("• Password: `AdminPassword123!`")
                        
                        gr.Markdown("**Test Steps:**")
                        gr.Markdown("1. Login with admin credentials")
                        gr.Markdown("2. Add a few test employees")
                        gr.Markdown("3. Ask AI questions about them")
                        gr.Markdown("4. Check system health")
                    
                    with gr.Column():
                        gr.Markdown("#### System Information")
                        gr.Markdown(f"**API Server:** {API_BASE_URL}")
                        gr.Markdown(f"**API Docs:** {API_BASE_URL}/docs")
                        gr.Markdown(f"**Health Check:** {API_BASE_URL}/health")
                        
                        gr.Markdown("#### Features Available")
                        gr.Markdown("✅ User Authentication")
                        gr.Markdown("✅ Employee Management")
                        gr.Markdown("✅ AI-Powered Queries")
                        gr.Markdown("✅ Natural Language Processing")
                        gr.Markdown("✅ RESTful API")
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("*🎯 AI Employee Decision System - Making smart organizational decisions with AI*")
        gr.Markdown("*📚 Visit the [API Documentation]({}) for more details*".format(f"{API_BASE_URL}/docs"))
    
    # Launch the application
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=config.debug,
    )
    
    return demo