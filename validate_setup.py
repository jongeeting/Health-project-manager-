#!/usr/bin/env python3
"""
Setup Validation Script
=======================

This script validates that your health management system is properly configured.
Run this before starting the application to catch configuration issues early.

Usage:
    python3 validate_setup.py
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(text):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    """Print a success message."""
    print(f"✅ {text}")

def print_error(text):
    """Print an error message."""
    print(f"❌ {text}")

def print_warning(text):
    """Print a warning message."""
    print(f"⚠️  {text}")

def print_info(text):
    """Print an info message."""
    print(f"ℹ️  {text}")


def check_python_version():
    """Check Python version is 3.9 or higher."""
    print_header("Checking Python Version")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major == 3 and version.minor >= 9:
        print_success(f"Python {version_str} (meets requirement: 3.9+)")
        return True
    else:
        print_error(f"Python {version_str} (requires 3.9 or higher)")
        return False


def check_dependencies():
    """Check that all required packages are installed."""
    print_header("Checking Python Dependencies")

    required_packages = [
        'flask',
        'twilio',
        'anthropic',
        'gspread',
        'oauth2client',
        'apscheduler',
        'python-dotenv',
        'pytz',
        'gunicorn'
    ]

    # Some packages have different module names than package names
    package_to_module = {
        'python-dotenv': 'dotenv',
    }

    all_installed = True

    for package in required_packages:
        try:
            # Get the actual module name (some differ from package name)
            module_name = package_to_module.get(package, package.replace('-', '_'))
            __import__(module_name)
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - NOT INSTALLED")
            all_installed = False

    if not all_installed:
        print_info("Install missing packages with: pip install -r requirements.txt")

    return all_installed


def check_env_file():
    """Check that .env file exists and has required variables."""
    print_header("Checking Environment Configuration")

    env_path = Path('.env')

    if not env_path.exists():
        print_error(".env file not found")
        print_info("Create it with: cp .env.example .env")
        print_info("Then edit .env and add your credentials")
        return False

    print_success(".env file exists")

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Required variables
    required_vars = {
        'TWILIO_ACCOUNT_SID': 'Twilio Account SID (starts with AC)',
        'TWILIO_AUTH_TOKEN': 'Twilio Auth Token',
        'TWILIO_PHONE_NUMBER': 'Twilio phone number (e.g., +15551234567)',
        'USER_PHONE_NUMBER': 'Your phone number (e.g., +15559876543)',
        'ANTHROPIC_API_KEY': 'Claude API key (starts with sk-ant-)',
        'GOOGLE_SHEET_NAME': 'Google Sheet name',
    }

    all_set = True

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f'your_{var.lower()}_here' and 'your_value' not in value:
            print_success(f"{var}: {description}")
        else:
            print_error(f"{var}: {description} - NOT SET or using placeholder")
            all_set = False

    # Check optional but important variables
    optional_vars = {
        'SECRET_KEY': 'Flask secret key',
        'CHECKIN_TIMES': 'Check-in times (default: 08:00,20:00)',
        'TIMEZONE': 'Timezone (default: America/New_York)',
    }

    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print_success(f"{var}: {description} - {value}")
        else:
            print_warning(f"{var}: {description} - using default")

    return all_set


def check_google_credentials():
    """Check Google Sheets credentials file or environment variable."""
    print_header("Checking Google Sheets Credentials")

    # Check for environment variable (production)
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            if 'client_email' in creds_dict:
                print_success(f"Using GOOGLE_CREDENTIALS_JSON environment variable")
                print_info(f"Service account: {creds_dict['client_email']}")
                return True
            else:
                print_error("GOOGLE_CREDENTIALS_JSON is invalid (missing client_email)")
                return False
        except json.JSONDecodeError:
            print_error("GOOGLE_CREDENTIALS_JSON is not valid JSON")
            return False

    # Check for file (development)
    creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/google_sheets_credentials.json')
    creds_file = Path(creds_path)

    if not creds_file.exists():
        print_error(f"Credentials file not found: {creds_path}")
        print_info("Download from Google Cloud Console and place at this path")
        print_info("See docs/SETUP.md Step 4 for instructions")
        return False

    print_success(f"Credentials file exists: {creds_path}")

    # Try to load and validate
    try:
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)

        if 'client_email' in creds_data:
            print_success(f"Credentials file is valid JSON")
            print_info(f"Service account email: {creds_data['client_email']}")
            print_info("Make sure you've shared your Google Sheet with this email!")
            return True
        else:
            print_error("Credentials file is missing required fields")
            return False

    except json.JSONDecodeError:
        print_error("Credentials file is not valid JSON")
        return False


def check_file_structure():
    """Check that all required files and directories exist."""
    print_header("Checking Project Structure")

    required_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        '.env.example',
        'modules/__init__.py',
        'modules/twilio_handler.py',
        'modules/claude_parser.py',
        'modules/sheets_manager.py',
        'modules/scheduler.py',
    ]

    all_exist = True

    for file_path in required_files:
        if Path(file_path).exists():
            print_success(file_path)
        else:
            print_error(f"{file_path} - MISSING")
            all_exist = False

    # Check for credentials directory
    if Path('credentials').is_dir():
        print_success("credentials/ directory")
    else:
        print_warning("credentials/ directory - will be created automatically")

    return all_exist


def test_config_import():
    """Try to import and validate config."""
    print_header("Testing Configuration Module")

    try:
        from config import Config
        print_success("Config module imported successfully")

        # Try validation (this will exit if fails, so we catch that)
        try:
            Config.validate()
            print_success("Configuration validated successfully")
            return True
        except SystemExit:
            print_error("Configuration validation failed")
            print_info("Check error messages above for details")
            return False

    except ImportError as e:
        print_error(f"Failed to import config: {e}")
        return False


def run_validation():
    """Run all validation checks."""
    print("\n")
    print("🏥 Health Management SMS System - Setup Validation")
    print("=" * 60)

    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Environment File': check_env_file(),
        'Google Credentials': check_google_credentials(),
        'Project Structure': check_file_structure(),
        'Configuration': test_config_import(),
    }

    # Summary
    print_header("Validation Summary")

    passed = sum(results.values())
    total = len(results)

    for check, result in results.items():
        if result:
            print_success(f"{check}")
        else:
            print_error(f"{check}")

    print("\n" + "=" * 60)

    if passed == total:
        print_success(f"All checks passed! ({passed}/{total})")
        print("\n🚀 Your system is ready to run!")
        print("\nNext steps:")
        print("  1. Test individual modules (see docs/TESTING.md)")
        print("  2. Run the application: python3 app.py")
        print("  3. Deploy to production (see docs/DEPLOYMENT.md)")
        return True
    else:
        print_error(f"Some checks failed ({passed}/{total} passed)")
        print("\n⚠️  Please fix the issues above before running the application")
        print("\nFor help:")
        print("  - See docs/SETUP.md for setup instructions")
        print("  - See docs/TESTING.md for troubleshooting")
        return False


if __name__ == '__main__':
    success = run_validation()
    sys.exit(0 if success else 1)
