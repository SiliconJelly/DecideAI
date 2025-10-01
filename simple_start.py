#!/usr/bin/env python3
"""
Simplified DecideAI Startup Script
Creates a working system without complex dependencies
"""

import os
import sys
import sqlite3
from pathlib import Path

def create_simple_database():
    """Create a simple SQLite database with basic tables."""
    db_path = Path("data/simple_decideai.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create simple users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create simple employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            position TEXT,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create admin user
    import hashlib
    admin_password = hashlib.sha256("admin123".encode()).hexdigest()
    
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, username, email, password_hash, role)
        VALUES ('admin-001', 'admin', 'admin@decideai.com', ?, 'admin')
    """, (admin_password,))
    
    # Add sample employee
    cursor.execute("""
        INSERT OR REPLACE INTO employees (id, first_name, last_name, email, position, department)
        VALUES ('emp-001', 'John', 'Doe', 'john.doe@company.com', 'Software Engineer', 'IT')
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Simple database created successfully")
    return str(db_path)

def start_simple_api():
    """Start a simple FastAPI server."""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn
        
        app = FastAPI(title="DecideAI Simple API", version="1.0.0")
        
        # Add CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        def read_root():
            return {"message": "DecideAI Simple API is running!", "version": "1.0.0"}
        
        @app.get("/health")
        def health_check():
            return {"status": "healthy", "database": "connected"}
        
        @app.get("/employees")
        def get_employees():
            """Get all employees from the simple database."""
            db_path = "data/simple_decideai.db"
            if not os.path.exists(db_path):
                raise HTTPException(status_code=500, detail="Database not found")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees")
            rows = cursor.fetchall()
            conn.close()
            
            employees = []
            for row in rows:
                employees.append({
                    "id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "position": row[4],
                    "department": row[5],
                    "created_at": row[6]
                })
            
            return {"employees": employees, "count": len(employees)}
        
        @app.post("/auth/login")
        def login(credentials: dict):
            """Simple login endpoint."""
            username = credentials.get("username")
            password = credentials.get("password")
            
            if username == "admin" and password == "admin123":
                return {
                    "access_token": "simple-token-123",
                    "token_type": "bearer",
                    "user": {"username": "admin", "role": "admin"}
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
        
        print("🚀 Starting DecideAI Simple API on http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔑 Login: username=admin, password=admin123")
        
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please install: pip install fastapi uvicorn")
        return False
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        return False

def start_simple_frontend():
    """Instructions for starting the frontend."""
    print("\n" + "="*60)
    print("🌐 FRONTEND SETUP")
    print("="*60)
    print("To start the React frontend:")
    print("1. cd frontend")
    print("2. npm install")
    print("3. npm run dev")
    print("4. Open http://localhost:3000")
    print("="*60)

def main():
    """Main startup function."""
    print("🎯 DecideAI - Simplified Startup")
    print("="*50)
    
    # Create simple database
    print("\n📊 Setting up database...")
    db_path = create_simple_database()
    
    # Show frontend instructions
    start_simple_frontend()
    
    # Start API server
    print("\n🚀 Starting backend API...")
    start_simple_api()

if __name__ == "__main__":
    main()