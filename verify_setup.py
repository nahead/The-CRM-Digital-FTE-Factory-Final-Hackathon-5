#!/usr/bin/env python3
"""
Project Verification Script
Checks if all required files and configurations are in place
"""

import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"{GREEN}✅{RESET} {description}: {filepath}")
        return True
    else:
        print(f"{RED}❌{RESET} {description}: {filepath} (MISSING)")
        return False

def check_directory(dirpath, description):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        print(f"{GREEN}✅{RESET} {description}: {dirpath}")
        return True
    else:
        print(f"{RED}❌{RESET} {description}: {dirpath} (MISSING)")
        return False

def check_env_variable(var_name):
    """Check if environment variable is set in .env"""
    if not os.path.exists('.env'):
        return False

    with open('.env', 'r') as f:
        content = f.read()
        if f"{var_name}=" in content and not f"{var_name}=your_" in content:
            return True
    return False

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🔍 Customer Success FTE - Project Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    results = []

    # Check core documentation
    print(f"\n{YELLOW}📚 Documentation Files{RESET}")
    results.append(check_file("README.md", "Main README"))
    results.append(check_file("SETUP.md", "Setup instructions"))
    results.append(check_file("PROJECT_STATUS.md", "Project status"))
    results.append(check_file("FINAL_SUMMARY.md", "Final summary"))

    # Check configuration files
    print(f"\n{YELLOW}⚙️  Configuration Files{RESET}")
    results.append(check_file(".env", "Environment variables"))
    results.append(check_file(".env.example", "Environment template"))
    results.append(check_file(".gitignore", "Git ignore"))
    results.append(check_file("requirements.txt", "Python dependencies"))
    results.append(check_file("docker-compose.yml", "Docker Compose"))
    results.append(check_file("Dockerfile", "Docker image"))

    # Check context files (Phase 1)
    print(f"\n{YELLOW}📁 Context Files (Phase 1 - Incubation){RESET}")
    results.append(check_file("context/company-profile.md", "Company profile"))
    results.append(check_file("context/product-docs.md", "Product docs"))
    results.append(check_file("context/sample-tickets.json", "Sample tickets"))
    results.append(check_file("context/escalation-rules.md", "Escalation rules"))
    results.append(check_file("context/brand-voice.md", "Brand voice"))

    # Check agent implementation
    print(f"\n{YELLOW}🤖 AI Agent Implementation{RESET}")
    results.append(check_file("src/agent/gemini_agent.py", "Gemini agent"))
    results.append(check_file("src/agent/tools.py", "Agent tools"))
    results.append(check_file("src/agent/prompts.py", "System prompts"))

    # Check channel handlers
    print(f"\n{YELLOW}📡 Channel Handlers{RESET}")
    results.append(check_file("src/channels/gmail_handler.py", "Gmail handler"))
    results.append(check_file("src/channels/whatsapp_handler.py", "WhatsApp handler"))
    results.append(check_file("src/channels/web_form_handler.py", "Web form handler"))

    # Check API
    print(f"\n{YELLOW}🚀 FastAPI Application{RESET}")
    results.append(check_file("src/api/main.py", "Main API"))

    # Check database
    print(f"\n{YELLOW}🗄️  Database{RESET}")
    results.append(check_file("src/database/schema.sql", "Database schema"))
    results.append(check_file("src/database/queries.py", "Database queries"))

    # Check web form (REQUIRED)
    print(f"\n{YELLOW}🌐 Web Support Form (REQUIRED DELIVERABLE){RESET}")
    results.append(check_file("src/web-form/src/SupportForm.jsx", "Support form component"))
    results.append(check_file("src/web-form/pages/index.js", "Next.js page"))
    results.append(check_file("src/web-form/pages/_app.js", "Next.js app"))
    results.append(check_file("src/web-form/styles/globals.css", "Global styles"))
    results.append(check_file("src/web-form/package.json", "Package config"))
    results.append(check_file("src/web-form/next.config.js", "Next.js config"))
    results.append(check_file("src/web-form/tailwind.config.js", "Tailwind config"))

    # Check Kafka
    print(f"\n{YELLOW}📨 Event Streaming{RESET}")
    results.append(check_file("src/kafka_client.py", "Kafka client"))

    # Check tests
    print(f"\n{YELLOW}🧪 Tests{RESET}")
    results.append(check_file("src/tests/test_api.py", "API tests"))
    results.append(check_file("test_api.py", "Quick test script"))

    # Check Kubernetes
    print(f"\n{YELLOW}☸️  Kubernetes{RESET}")
    results.append(check_file("k8s/deployment.yaml", "K8s manifests"))

    # Check helper scripts
    print(f"\n{YELLOW}🛠️  Helper Scripts{RESET}")
    results.append(check_file("start.sh", "Start script (Linux/Mac)"))
    results.append(check_file("start.bat", "Start script (Windows)"))

    # Check directories
    print(f"\n{YELLOW}📂 Directory Structure{RESET}")
    results.append(check_directory("context", "Context folder"))
    results.append(check_directory("src", "Source folder"))
    results.append(check_directory("src/agent", "Agent folder"))
    results.append(check_directory("src/channels", "Channels folder"))
    results.append(check_directory("src/api", "API folder"))
    results.append(check_directory("src/database", "Database folder"))
    results.append(check_directory("src/web-form", "Web form folder"))
    results.append(check_directory("src/tests", "Tests folder"))
    results.append(check_directory("k8s", "Kubernetes folder"))
    results.append(check_directory("credentials", "Credentials folder"))

    # Check environment variables
    print(f"\n{YELLOW}🔑 Environment Variables{RESET}")
    if check_env_variable("GEMINI_API_KEY"):
        print(f"{GREEN}✅{RESET} GEMINI_API_KEY is configured")
        results.append(True)
    else:
        print(f"{YELLOW}⚠️{RESET}  GEMINI_API_KEY not configured (REQUIRED)")
        print(f"   Get from: https://makersuite.google.com/app/apikey")
        results.append(False)

    if check_env_variable("TWILIO_ACCOUNT_SID"):
        print(f"{GREEN}✅{RESET} Twilio credentials configured")
    else:
        print(f"{YELLOW}⚠️{RESET}  Twilio credentials not configured (optional)")

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}📊 Verification Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100

    print(f"Files checked: {total}")
    print(f"Files present: {passed}")
    print(f"Completion: {percentage:.1f}%\n")

    if percentage == 100:
        print(f"{GREEN}🎉 Perfect! All files are in place.{RESET}")
        print(f"{GREEN}✅ Project is ready for deployment!{RESET}\n")
        return 0
    elif percentage >= 90:
        print(f"{YELLOW}⚠️  Almost there! A few files are missing.{RESET}")
        print(f"{YELLOW}Check the list above and create missing files.{RESET}\n")
        return 1
    else:
        print(f"{RED}❌ Several files are missing.{RESET}")
        print(f"{RED}Please review the setup instructions.{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
