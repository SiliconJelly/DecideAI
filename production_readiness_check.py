#!/usr/bin/env python3
"""
DecideAI Production Readiness Check
Comprehensive check for micro SaaS deployment readiness
"""

import os
import sys
from pathlib import Path
import subprocess

def check_essential_files():
    """Check if all essential files exist."""
    essential_files = [
        'README.md',
        'LICENSE', 
        '.gitignore',
        '.env.example',
        'requirements.txt',
        'docker-compose.yml',
        'Dockerfile'
    ]
    
    missing_files = []
    for file in essential_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    return missing_files

def check_sensitive_files():
    """Check for sensitive files that shouldn't be in repo."""
    sensitive_patterns = [
        '.env',
        '*.db', 
        '*.sqlite*',
        '*.log',
        '*.key',
        '*.pem'
    ]
    
    found_sensitive = []
    
    # Check for .env specifically
    if Path('.env').exists():
        found_sensitive.append('.env')
    
    # Check for database files
    for db_file in Path('.').rglob('*.db'):
        if not any(ignore in str(db_file) for ignore in ['.git', '__pycache__', '.venv']):
            found_sensitive.append(str(db_file))
    
    # Check for log files
    for log_file in Path('.').rglob('*.log'):
        if not any(ignore in str(log_file) for ignore in ['.git', '__pycache__', '.venv']):
            found_sensitive.append(str(log_file))
    
    return found_sensitive

def check_license_consistency():
    """Check if LICENSE and README are consistent."""
    issues = []
    
    # Check LICENSE file
    if Path('LICENSE').exists():
        with open('LICENSE', 'r') as f:
            license_content = f.read()
            if 'DecideAI' not in license_content:
                issues.append("LICENSE doesn't mention DecideAI")
            if 'MIT License' not in license_content:
                issues.append("LICENSE is not MIT (recommended for micro SaaS)")
    
    # Check README
    if Path('README.md').exists():
        with open('README.md', 'r') as f:
            readme_content = f.read()
            if 'proprietary' in readme_content.lower():
                issues.append("README mentions proprietary license but LICENSE is MIT")
    
    return issues

def check_env_example():
    """Check .env.example for placeholder values."""
    issues = []
    
    if Path('.env.example').exists():
        with open('.env.example', 'r') as f:
            content = f.read()
            
            # Check for real secrets (bad)
            if any(secret in content for secret in ['sk_live_', 'pk_live_', 'real-password']):
                issues.append(".env.example contains real secrets")
            
            # Check for proper placeholders (good)
            if not any(placeholder in content for placeholder in ['your-', 'change-in-production', 'example.com']):
                issues.append(".env.example might not have proper placeholders")
    
    return issues

def check_core_imports():
    """Check if core package imports work."""
    try:
        import ai_employee_decision_system
        return True, None
    except ImportError as e:
        return False, str(e)

def check_micro_saas_readiness():
    """Check specific micro SaaS requirements."""
    issues = []
    
    # Check for pricing/business model in README
    if Path('README.md').exists():
        with open('README.md', 'r') as f:
            readme_content = f.read()
            if 'Business Model' not in readme_content and 'Pricing' not in readme_content:
                issues.append("README missing business model/pricing information")
    
    # Check for Docker deployment
    if not Path('docker-compose.yml').exists():
        issues.append("Missing docker-compose.yml for easy deployment")
    
    # Check for requirements.txt
    if not Path('requirements.txt').exists():
        issues.append("Missing requirements.txt")
    
    return issues

def main():
    """Main check function."""
    print("🔍 DecideAI Production Readiness Check for Micro SaaS")
    print("=" * 60)
    
    all_good = True
    
    # Check essential files
    print("\n📁 Essential Files Check:")
    missing_files = check_essential_files()
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        all_good = False
    else:
        print("✅ All essential files present")
    
    # Check for sensitive files
    print("\n🔒 Security Check:")
    sensitive_files = check_sensitive_files()
    if sensitive_files:
        print(f"⚠️  Sensitive files found: {', '.join(sensitive_files)}")
        print("   These should be in .gitignore or removed")
        all_good = False
    else:
        print("✅ No sensitive files in repository")
    
    # Check license consistency
    print("\n📄 License Consistency:")
    license_issues = check_license_consistency()
    if license_issues:
        for issue in license_issues:
            print(f"⚠️  {issue}")
        all_good = False
    else:
        print("✅ License files are consistent")
    
    # Check .env.example
    print("\n🔧 Environment Configuration:")
    env_issues = check_env_example()
    if env_issues:
        for issue in env_issues:
            print(f"⚠️  {issue}")
        all_good = False
    else:
        print("✅ .env.example has proper placeholder values")
    
    # Check core imports
    print("\n🐍 Core Package Check:")
    import_success, import_error = check_core_imports()
    if not import_success:
        print(f"❌ Import error: {import_error}")
        all_good = False
    else:
        print("✅ Core package imports successfully")
    
    # Check micro SaaS readiness
    print("\n💼 Micro SaaS Readiness:")
    saas_issues = check_micro_saas_readiness()
    if saas_issues:
        for issue in saas_issues:
            print(f"⚠️  {issue}")
        # These are warnings, not blockers
    else:
        print("✅ Ready for micro SaaS deployment")
    
    print("\n" + "=" * 60)
    
    if all_good:
        print("🎉 PRODUCTION READY! ✅")
        print("✅ Safe to push to GitHub")
        print("✅ Ready for micro SaaS deployment")
        return True
    else:
        print("❌ Issues found - please fix before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)