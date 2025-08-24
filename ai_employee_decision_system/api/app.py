"""
FastAPI application for the AI Employee Decision System.
"""
import io
from typing import Dict, List, Optional, Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import UUID4
from sqlalchemy.orm import Session

from ai_employee_decision_system.core import config, get_logger
from ai_employee_decision_system.api.docs import API_METADATA, TAGS_METADATA, EXAMPLE_RESPONSES
from ai_employee_decision_system.models import (
    DocumentCreate,
    EmployeeCreate,
    EmployeeUpdate,
    ProjectCreate,
    SkillCreate,
    SpecializationCreate,
    TagCreate,
    db_session,
)
from ai_employee_decision_system.models.user import User
from ai_employee_decision_system.auth import (
    AuthService,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
)
from ai_employee_decision_system.services import (
    AIService,
    DocumentService,
    EmployeeService,
    ProjectService,
    SkillService,
    SpecializationService,
    TagService,
)

logger = get_logger(__name__)

app = FastAPI(
    title=API_METADATA["title"],
    description=API_METADATA["description"],
    version=API_METADATA["version"],
    contact=API_METADATA["contact"],
    license_info=API_METADATA["license"],
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    responses=EXAMPLE_RESPONSES,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Dependencies
def get_db():
    """Get a database session."""
    with db_session() as session:
        yield session


def get_auth_service(db: Session = Depends(get_db)):
    """Get the authentication service."""
    return AuthService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get the current authenticated user."""
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current authenticated admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Service dependencies
def get_employee_service(db: Session = Depends(get_db)):
    """Get the employee service."""
    return EmployeeService(db)


def get_document_service(db: Session = Depends(get_db)):
    """Get the document service."""
    return DocumentService(db)


def get_project_service(db: Session = Depends(get_db)):
    """Get the project service."""
    return ProjectService(db)


def get_skill_service(db: Session = Depends(get_db)):
    """Get the skill service."""
    return SkillService(db)


def get_specialization_service(db: Session = Depends(get_db)):
    """Get the specialization service."""
    return SpecializationService(db)


def get_tag_service(db: Session = Depends(get_db)):
    """Get the tag service."""
    return TagService(db)


def get_ai_service():
    """Get the AI service."""
    return AIService()


# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to the AI Employee Decision System API"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse, tags=["Authentication"])
def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user."""
    user = auth_service.create_user(user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed. Email or username may already exist."
        )
    return UserResponse(**user.to_dict())


@app.post("/auth/login", response_model=Token, tags=["Authentication"])
def login_user(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Login user and return access token."""
    user = auth_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_service.create_access_token(user)
    return token


@app.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(**current_user.to_dict())


@app.get("/auth/users", response_model=List[UserResponse], tags=["Authentication"])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get all users (admin only)."""
    users = auth_service.get_users(skip=skip, limit=limit)
    return [UserResponse(**user.to_dict()) for user in users]


@app.put("/auth/users/{user_id}/status", response_model=UserResponse, tags=["Authentication"])
def update_user_status(
    user_id: UUID4,
    is_active: bool,
    current_user: User = Depends(get_current_admin_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update user active status (admin only)."""
    user = auth_service.update_user_status(user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user.to_dict())


# Employee endpoints
@app.get("/employees/", tags=["Employees"])
def get_employees(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service),
):
    """Get all employees."""
    employees = employee_service.get_employees(skip=skip, limit=limit)
    return [employee.to_dict() for employee in employees]


@app.get("/employees/{employee_id}", tags=["Employees"])
def get_employee(
    employee_id: UUID4,
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service),
):
    """Get an employee by ID."""
    employee = employee_service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee.to_dict()


@app.post("/employees/", tags=["Employees"])
def create_employee(
    employee_data: EmployeeCreate,
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service),
):
    """Create a new employee."""
    employee = employee_service.create_employee(employee_data)
    return employee.to_dict()


@app.put("/employees/{employee_id}", tags=["Employees"])
def update_employee(
    employee_id: UUID4,
    employee_data: EmployeeUpdate,
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service),
):
    """Update an employee."""
    employee = employee_service.update_employee(employee_id, employee_data)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee.to_dict()


@app.delete("/employees/{employee_id}", tags=["Employees"])
def delete_employee(
    employee_id: UUID4,
    current_user: User = Depends(get_current_admin_user),
    employee_service: EmployeeService = Depends(get_employee_service),
):
    """Delete an employee (admin only)."""
    result = employee_service.delete_employee(employee_id)
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


# Document endpoints
@app.get("/documents/", tags=["Documents"])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    """Get all documents."""
    documents = document_service.get_documents(skip=skip, limit=limit)
    return [document.to_dict() for document in documents]


@app.get("/documents/{document_id}", tags=["Documents"])
def get_document(
    document_id: UUID4,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    """Get a document by ID."""
    document = document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.to_dict()


@app.post("/employees/{employee_id}/documents/", tags=["Documents"])
async def create_document(
    employee_id: UUID4,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    """Create a new document for an employee."""
    # Create document data
    document_data = DocumentCreate(
        name=file.filename,
        type=document_type,
        mime_type=file.content_type or "application/octet-stream",
        size=0,  # Will be updated after reading the file
    )
    
    # Read the file
    file_content = await file.read()
    document_data.size = len(file_content)
    
    # Create the document
    document = document_service.create_document(
        employee_id,
        document_data,
        io.BytesIO(file_content),
    )
    if not document:
        raise HTTPException(status_code=404, detail="Employee not found")
    return document.to_dict()


@app.post("/documents/{document_id}/process", tags=["Documents"])
def process_document(
    document_id: UUID4,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
):
    """Process a document with OCR and AI analysis."""
    document = document_service.process_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.to_dict()


@app.post("/employees/bulk-upload", tags=["Employees"])
async def bulk_upload_employees(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service),
):
    """Bulk upload employees from CSV/Excel file."""
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=400, 
            detail="Only CSV and Excel files are supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Process the file based on type
        if file.filename.endswith('.csv'):
            import csv
            import io
            
            # Parse CSV
            csv_data = io.StringIO(content.decode('utf-8'))
            reader = csv.DictReader(csv_data)
            
            created_employees = []
            errors = []
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                try:
                    # Map CSV columns to employee fields
                    employee_data = EmployeeCreate(
                        first_name=row.get('first_name', '').strip(),
                        last_name=row.get('last_name', '').strip(),
                        email=row.get('email', '').strip(),
                        position=row.get('position', '').strip() or None,
                        department=row.get('department', '').strip() or None,
                    )
                    
                    # Validate required fields
                    if not all([employee_data.first_name, employee_data.last_name, employee_data.email]):
                        errors.append(f"Row {row_num}: Missing required fields (first_name, last_name, email)")
                        continue
                    
                    # Create employee
                    employee = employee_service.create_employee(employee_data)
                    created_employees.append(employee.to_dict())
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            return {
                "message": f"Processed {len(created_employees)} employees successfully",
                "created_count": len(created_employees),
                "error_count": len(errors),
                "employees": created_employees,
                "errors": errors
            }
        
        else:
            # Excel files would be handled here
            raise HTTPException(status_code=400, detail="Excel support coming soon")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


# AI endpoints
@app.post("/ai/query", tags=["AI"])
def process_query(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),
):
    """Process a natural language query."""
    query = request.get("query", "")
    context = request.get("context")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    result = ai_service.process_query(query, context)
    return result


# Project endpoints
@app.get("/projects/", tags=["Projects"])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Get all projects."""
    projects = project_service.get_projects(skip=skip, limit=limit)
    return [project.to_dict() for project in projects]


@app.post("/projects/", tags=["Projects"])
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Create a new project."""
    project = project_service.create_project(project_data)
    return project.to_dict()


# Skills endpoints
@app.get("/skills/", tags=["Skills"])
def get_skills(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service),
):
    """Get all skills."""
    skills = skill_service.get_skills(skip=skip, limit=limit)
    return [skill.to_dict() for skill in skills]


@app.post("/skills/", tags=["Skills"])
def create_skill(
    skill_data: SkillCreate,
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service),
):
    """Create a new skill."""
    skill = skill_service.create_skill(skill_data)
    return skill.to_dict()


def run_api():
    """Run the FastAPI application."""
    import uvicorn
    logger.info("Starting API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run_api()