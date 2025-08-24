#!/usr/bin/env python3
"""
Initialize the AI Employee Decision System.
"""
import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "data/uploads", 
        "data/models",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    return True

def init_database():
    """Initialize the database."""
    try:
        from ai_employee_decision_system.models import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def create_admin_user():
    """Create initial admin user."""
    try:
        from ai_employee_decision_system.auth import AuthService, UserCreate
        from ai_employee_decision_system.models import db_session
        
        with db_session() as session:
            auth_service = AuthService(session)
            
            # Check if admin already exists
            existing_admin = auth_service.get_user_by_username("admin")
            if existing_admin:
                print("⚠️  Admin user already exists")
                return True
            
            admin_data = UserCreate(
                email="admin@example.com",
                username="admin",
                password="AdminPassword123!",
                first_name="System",
                last_name="Administrator",
                is_admin=True
            )
            
            user = auth_service.create_user(admin_data)
            if user:
                print("✅ Admin user created successfully")
                print("   Username: admin")
                print("   Password: AdminPassword123!")
                print("   Email: admin@example.com")
                return True
            else:
                print("❌ Admin user creation failed")
                return False
                
    except Exception as e:
        print(f"❌ Admin user creation error: {e}")
        return False

def setup_environment():
    """Set up environment file if it doesn't exist."""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from .env.example")
            print("⚠️  Please review and update the .env file with your settings")
        else:
            # Create a basic .env file
            env_content = """# AI Employee Decision System Configuration
EMPLOYEE_SYSTEM_DB_URL=sqlite:///./data/employee_system.db
EMPLOYEE_SYSTEM_SECRET_KEY=change-this-secret-key-in-production
EMPLOYEE_SYSTEM_DEBUG=true
EMPLOYEE_SYSTEM_DATA_DIR=./data
EMPLOYEE_SYSTEM_UPLOAD_DIR=./data/uploads
"""
            with open(".env", "w") as f:
                f.write(env_content)
            print("✅ Created basic .env file")
    else:
        print("✅ .env file already exists")
    return True

def main():
    """Main initialization function."""
    print("🚀 Initializing AI Employee Decision System...\n")
    
    steps = [
        ("Setting up environment", setup_environment),
        ("Creating directories", create_directories),
        ("Initializing database", init_database),
        ("Creating admin user", create_admin_user),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"--- {step_name} ---")
        try:
            if step_func():
                success_count += 1
            else:
                print(f"❌ {step_name} failed")
        except Exception as e:
            print(f"❌ {step_name} error: {e}")
        print()
    
    if success_count == len(steps):
        print("🎉 System initialization completed successfully!")
        print("\nNext steps:")
        print("1. Review the .env file and update settings as needed")
        print("2. Start the API server:")
        print("   python -m uvicorn ai_employee_decision_system.api.app:app --reload")
        print("3. Visit http://localhost:8000/docs to see the API documentation")
        print("4. Run the deployment test:")
        print("   python test_deployment.py")
        return True
    else:
        print(f"⚠️  Initialization completed with {len(steps) - success_count} issues")
        print("Please check the errors above and try again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)