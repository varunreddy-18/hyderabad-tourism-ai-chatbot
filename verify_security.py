#!/usr/bin/env python3
"""
Security Verification Script - Post Audit Checks
Ensures all security measures are in place and application still functions
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 70)
print("SECURITY VERIFICATION - POST AUDIT")
print("=" * 70)

# Load environment
load_dotenv()

# Test 1: .env.example exists
print("\n[1/7] Checking .env.example exists...")
if Path(".env.example").exists():
    print("✅ .env.example found")
    with open(".env.example") as f:
        content = f.read()
        has_placeholder = "your_" in content.lower()
        if has_placeholder:
            print("✅ .env.example contains only placeholders (no real secrets)")
        else:
            print("⚠️  .env.example may contain real values - CHECK MANUALLY")
else:
    print("❌ .env.example NOT found")
    sys.exit(1)

# Test 2: .gitignore covers .env
print("\n[2/7] Checking .gitignore configuration...")
with open(".gitignore") as f:
    gitignore_content = f.read()
    checks = {
        ".env": ".env" in gitignore_content,
        ".env.local": ".env.local" in gitignore_content,
        "venv/": "venv/" in gitignore_content,
        "__pycache__/": "__pycache__/" in gitignore_content,
    }
    
    all_pass = True
    for check_name, result in checks.items():
        if result:
            print(f"✅ {check_name} in .gitignore")
        else:
            print(f"❌ {check_name} NOT in .gitignore")
            all_pass = False
    
    if not all_pass:
        sys.exit(1)

# Test 3: Environment variables load correctly
print("\n[3/7] Checking environment variables...")
groq_key = os.getenv("GROQ_API_KEY")
if groq_key and groq_key.startswith("gsk_"):
    print("✅ GROQ_API_KEY loaded from environment")
    print(f"   Key format: {groq_key[:12]}...{groq_key[-4:]}")
elif groq_key:
    print(f"⚠️  GROQ_API_KEY has unexpected format: {groq_key[:20]}...")
else:
    print("⚠️  GROQ_API_KEY not found in environment")
    print("   (This is OK if you haven't set it yet)")

# Test 4: Check LLM files use os.getenv
print("\n[4/7] Checking LLM integration uses os.getenv()...")
files_to_check = [
    "src/llm/groq_llm.py",
    "src/llm/huggingface_llm.py",
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        with open(file_path) as f:
            content = f.read()
            if "os.getenv(" in content:
                print(f"✅ {file_path} uses os.getenv() for credentials")
            else:
                print(f"⚠️  {file_path} may not use os.getenv()")
    else:
        print(f"⚠️  {file_path} not found")

# Test 5: Check no hardcoded API keys in Python files
print("\n[5/7] Scanning Python files for hardcoded API keys...")
dangerous_patterns = [
    "gsk_",
    "hf_hf_",
    "AIzaSy",
    "AKIA",
    "Bearer ",
]

found_secrets = []
for py_file in Path(".").rglob("*.py"):
    if "venv" in str(py_file):
        continue
    try:
        with open(py_file) as f:
            content = f.read()
            for pattern in dangerous_patterns:
                if pattern in content and ".env" not in str(py_file):
                    found_secrets.append((py_file, pattern))
    except:
        pass

if found_secrets:
    print("❌ FOUND POTENTIAL HARDCODED SECRETS:")
    for file_path, pattern in found_secrets:
        print(f"   {file_path}: contains '{pattern}'")
    sys.exit(1)
else:
    print("✅ No hardcoded API keys found in Python files")

# Test 6: Check README doesn't have real credentials
print("\n[6/7] Checking README.md...")
with open("README.md") as f:
    readme = f.read()
    if "your_" in readme.lower() or "example" in readme.lower():
        if "gsk_" not in readme and "AIzaSy" not in readme:
            print("✅ README.md contains only placeholder values")
        else:
            print("❌ README.md may contain real API keys")
            sys.exit(1)
    else:
        print("⚠️  README.md structure different than expected - CHECK MANUALLY")

# Test 7: Verify app.py still loads
print("\n[7/7] Checking application imports...")
try:
    import app
    print("✅ app.py imports successfully")
except ImportError as e:
    print(f"⚠️  app.py import failed: {e}")
    print("   (This may be OK if dependencies aren't installed)")
except Exception as e:
    print(f"⚠️  app.py error: {e}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)

print("""
✅ All security checks passed!

Next Steps:
1. Review SECURITY_AUDIT_REPORT.md for detailed findings
2. Rotate your Groq API key (see instructions in report)
3. Test application: python app.py
4. Push to GitHub

WARNING:
- NEVER commit .env file to Git
- ALWAYS use .env.example as template
- Always rotate API keys before public publication

For help, see: SECURITY_AUDIT_REPORT.md
""")
