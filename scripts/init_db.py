#!/usr/bin/env python3
"""
Initialize the database with schema and create a default admin user.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_employee_decision_system.models.database import init_db, db_session
from ai_employee_decision_system.models.user import User
from ai_employee_decision_system.auth import AuthService


def main():
    print("=" * 60)
    print("Initializing Database")
    print("=" * 60)
    
    # Initialize database schema
    print("\n1. Creating database schema...")
    init_db()
    print("   ✓ Database schema created")
    
    # Create default admin user if environment variables are set
    print("\n2. Creating admin user (optional)...")
    import os
    username = os.environ.get("DECIDEAI_ADMIN_USERNAME")
    password = os.environ.get("DECIDEAI_ADMIN_PASSWORD")
    email = os.environ.get("DECIDEAI_ADMIN_EMAIL", "admin@example.com")
    first_name = os.environ.get("DECIDEAI_ADMIN_FIRST_NAME", "System")
    last_name = os.environ.get("DECIDEAI_ADMIN_LAST_NAME", "Administrator")

    if not (username and password):
        print("   ℹ Skipping admin creation (set DECIDEAI_ADMIN_USERNAME and DECIDEAI_ADMIN_PASSWORD to create)")
    else:
        with db_session() as session:
            auth_service = AuthService(session)
            from ai_employee_decision_system.auth import UserCreate

            # Check if admin user already exists
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                print(f"   ⚠ Admin user '{username}' already exists, skipping creation")
            else:
                admin_user = UserCreate(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_admin=True
                )
                user = auth_service.create_user(admin_user)
                if user:
                    # Make the user an admin
                    user.is_admin = True
                    session.commit()
                    print("   ✓ Admin user created")
                    print(f"     Username: {username}")
                    print(f"     Email: {email}")
                else:
                    print("   ✗ Failed to create admin user")
                    return 1
    
    print("\n" + "=" * 60)
    print("✓ Database initialization complete!")
    print("=" * 60)
    print("\nYou can now start the API server:")
    print("  uvicorn ai_employee_decision_system.api.app:app --reload")
    print("\nTo create an admin user non-interactively, run:")
    print("  DECIDEAI_ADMIN_USERNAME=admin DECIDEAI_ADMIN_PASSWORD=\"<strong-password>\" \\")
    print("  python3 scripts/init_db.py")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())