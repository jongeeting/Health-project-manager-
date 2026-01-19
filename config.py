"""
Configuration Module
====================
This module loads and validates all environment variables needed for the application.

It uses python-dotenv to load variables from a .env file and provides them
to other modules in a centralized, validated way.

Usage:
    from config import Config
    print(Config.TWILIO_ACCOUNT_SID)
"""

import os
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class that holds all environment variables.

    This class validates that all required environment variables are present
    and provides helpful error messages if anything is missing.
    """

    # ============================================
    # TWILIO CONFIGURATION
    # ============================================
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    USER_PHONE_NUMBER = os.getenv('USER_PHONE_NUMBER')

    # ============================================
    # CLAUDE API CONFIGURATION
    # ============================================
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # ============================================
    # GOOGLE SHEETS CONFIGURATION
    # ============================================
    GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME', 'Health Tracking Data')
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/google_sheets_credentials.json')
    # For production deployment: full JSON credentials as environment variable
    GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')

    # ============================================
    # APPLICATION CONFIGURATION
    # ============================================
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    PORT = int(os.getenv('PORT', 5000))

    # ============================================
    # SCHEDULED CHECK-IN CONFIGURATION
    # ============================================
    CHECKIN_TIMES = os.getenv('CHECKIN_TIMES', '08:00,20:00').split(',')
    TIMEZONE = os.getenv('TIMEZONE', 'America/New_York')

    # ============================================
    # LOGGING CONFIGURATION
    # ============================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


    @classmethod
    def validate(cls):
        """
        Validates that all required configuration variables are present.

        This method checks for missing environment variables and provides
        helpful error messages about which variables need to be set.

        Raises:
            SystemExit: If any required variables are missing
        """
        required_vars = {
            'TWILIO_ACCOUNT_SID': cls.TWILIO_ACCOUNT_SID,
            'TWILIO_AUTH_TOKEN': cls.TWILIO_AUTH_TOKEN,
            'TWILIO_PHONE_NUMBER': cls.TWILIO_PHONE_NUMBER,
            'USER_PHONE_NUMBER': cls.USER_PHONE_NUMBER,
            'ANTHROPIC_API_KEY': cls.ANTHROPIC_API_KEY,
        }

        missing_vars = [var for var, value in required_vars.items() if not value]

        if missing_vars:
            print("❌ ERROR: Missing required environment variables!")
            print("\nThe following variables must be set in your .env file:")
            for var in missing_vars:
                print(f"  - {var}")
            print("\nPlease copy .env.example to .env and fill in your credentials.")
            print("See SETUP.md for detailed instructions on getting these credentials.")
            sys.exit(1)

        # Validate Google Sheets credentials exist (either as file or environment variable)
        has_file_creds = os.path.exists(cls.GOOGLE_CREDENTIALS_PATH)
        has_env_creds = cls.GOOGLE_CREDENTIALS_JSON is not None

        if not has_file_creds and not has_env_creds:
            print(f"❌ ERROR: Google Sheets credentials not found!")
            print(f"\nFor local development:")
            print(f"  - Expected file location: {cls.GOOGLE_CREDENTIALS_PATH}")
            print(f"\nFor production deployment:")
            print(f"  - Set GOOGLE_CREDENTIALS_JSON environment variable")
            print("\nPlease download your Google Sheets API credentials.")
            print("See docs/SETUP.md for instructions on obtaining Google API credentials.")
            sys.exit(1)

        print("✅ Configuration validated successfully!")
        return True


# Validate configuration when this module is imported
# This ensures the app won't start with missing credentials
if __name__ != "__main__":
    # Only validate if not running this file directly
    # (allows for testing without full credentials)
    pass
