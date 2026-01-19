"""
Google Sheets Manager Module
=============================
This module handles all interactions with Google Sheets for data storage.

It manages:
- Creating and accessing the health tracking spreadsheet
- Writing symptom data to the sheet
- Setting up proper column headers
- Data validation and formatting

The sheet serves as the database for all health tracking information,
making it easy to view, analyze, and export data.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging
import pytz
from config import Config

# Set up logging
logger = logging.getLogger(__name__)


class SheetsManager:
    """
    Manages Google Sheets integration for health data storage.

    This class handles authentication with Google Sheets API and provides
    methods to log symptom data in a structured format.
    """

    def __init__(self):
        """
        Initialize the Google Sheets client and connect to the tracking sheet.

        Sets up authentication using the service account credentials and
        opens the specified Google Sheet. Creates the sheet if it doesn't exist.
        """
        try:
            # Define the scope for Google Sheets and Drive access
            # These scopes allow us to read and write to Google Sheets
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/drive'
            ]

            # Authenticate using service account credentials
            # Support both file-based (local dev) and environment variable (production) credentials
            if hasattr(Config, 'GOOGLE_CREDENTIALS_JSON') and Config.GOOGLE_CREDENTIALS_JSON:
                # Production: Load from environment variable
                logger.info("Loading Google credentials from environment variable")
                import json
                creds_dict = json.loads(Config.GOOGLE_CREDENTIALS_JSON)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            else:
                # Development: Load from file
                logger.info(f"Loading Google credentials from file: {Config.GOOGLE_CREDENTIALS_PATH}")
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    Config.GOOGLE_CREDENTIALS_PATH,
                    scope
                )

            # Create gspread client
            self.client = gspread.authorize(creds)

            # Open or create the health tracking spreadsheet
            self.sheet = self._get_or_create_sheet()

            # Set up the worksheet with proper headers
            self.worksheet = self._setup_worksheet()

            logger.info("Google Sheets connection established successfully")

        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {str(e)}", exc_info=True)
            raise

    def _get_or_create_sheet(self):
        """
        Get the existing health tracking sheet or create it if it doesn't exist.

        Returns:
            gspread.Spreadsheet: The health tracking spreadsheet

        Raises:
            Exception: If unable to access or create the sheet
        """
        try:
            # Try to open existing sheet
            sheet = self.client.open(Config.GOOGLE_SHEET_NAME)
            logger.info(f"Opened existing sheet: {Config.GOOGLE_SHEET_NAME}")
            return sheet
        except gspread.SpreadsheetNotFound:
            # Create new sheet if it doesn't exist
            logger.info(f"Sheet not found. Creating new sheet: {Config.GOOGLE_SHEET_NAME}")
            sheet = self.client.create(Config.GOOGLE_SHEET_NAME)

            # Share with yourself (optional - add your email here)
            # sheet.share('your-email@gmail.com', perm_type='user', role='writer')

            logger.info(f"Created new sheet: {Config.GOOGLE_SHEET_NAME}")
            return sheet

    def _setup_worksheet(self):
        """
        Set up the symptom tracking worksheet with proper column headers.

        Creates the "Symptom Tracking" worksheet if it doesn't exist and
        sets up column headers for all the data we'll be tracking.

        Returns:
            gspread.Worksheet: The symptom tracking worksheet
        """
        try:
            # Try to get the "Symptom Tracking" worksheet
            try:
                worksheet = self.sheet.worksheet("Symptom Tracking")
                logger.info("Found existing 'Symptom Tracking' worksheet")
            except gspread.WorksheetNotFound:
                # Create the worksheet if it doesn't exist
                worksheet = self.sheet.add_worksheet(
                    title="Symptom Tracking",
                    rows="1000",  # Start with 1000 rows
                    cols="20"     # 20 columns for our data
                )
                logger.info("Created new 'Symptom Tracking' worksheet")

            # Check if headers exist (check first row)
            try:
                existing_headers = worksheet.row_values(1)
                if existing_headers:
                    logger.info("Headers already exist")
                    return worksheet
            except:
                pass  # No headers exist yet

            # Set up column headers
            # These define what data we're tracking for each symptom log entry
            headers = [
                'Timestamp',           # When the symptom was logged
                'Date',                # Date only (for easier filtering)
                'Time',                # Time only (for time-of-day analysis)
                'Raw Message',         # Original text message from user
                'Symptoms List',       # Comma-separated list of symptoms
                'Severity Scores',     # Severity ratings (e.g., "bloating: 7, nausea: 5")
                'Triggers',            # Potential triggers identified
                'Mood/Energy',         # Mood and energy level notes
                'Summary',             # One-line summary of the entry
                'Parsed Successfully', # Whether Claude successfully parsed the message
                'Entry Type',          # 'automated_checkin' or 'manual'
                # Reserved for future phases:
                'Cycle Day',           # (Phase 3) Day of menstrual cycle
                'Cycle Phase',         # (Phase 3) Follicular/Ovulatory/Luteal/Menstrual
                'Medications Taken',   # (Phase 2) Medications logged that day
                'Notes',               # Additional notes or observations
            ]

            # Write headers to first row
            worksheet.update('A1:O1', [headers])

            # Format header row (bold, frozen)
            worksheet.format('A1:O1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })

            # Freeze the header row so it stays visible when scrolling
            worksheet.freeze(rows=1)

            logger.info("Worksheet headers configured successfully")
            return worksheet

        except Exception as e:
            logger.error(f"Error setting up worksheet: {str(e)}", exc_info=True)
            raise

    def log_symptom_entry(self, parsed_data, entry_type='manual'):
        """
        Log a symptom entry to the Google Sheet.

        Takes the parsed symptom data from Claude and writes it as a new row
        in the spreadsheet with proper formatting and timestamps.

        Args:
            parsed_data (dict): Parsed symptom data from ClaudeParser
            entry_type (str): 'automated_checkin' or 'manual' - how the entry was created

        Returns:
            bool: True if successfully logged, False otherwise

        Example:
            >>> manager = SheetsManager()
            >>> parsed_data = {
            ...     'symptoms': [{'name': 'bloating', 'severity': 7}],
            ...     'triggers': ['dairy'],
            ...     'mood_energy': 'tired',
            ...     'summary': 'Bloating after lunch',
            ...     'raw_message': 'Bad bloating, 7/10, had dairy'
            ... }
            >>> manager.log_symptom_entry(parsed_data, 'manual')
            True
        """
        try:
            # Get current timestamp in user's timezone
            tz = pytz.timezone(Config.TIMEZONE)
            now = datetime.now(tz)

            # Format timestamp components
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
            date_only = now.strftime('%Y-%m-%d')
            time_only = now.strftime('%H:%M:%S')

            # Extract data from parsed_data
            raw_message = parsed_data.get('raw_message', '')

            # Format symptoms list
            symptoms = parsed_data.get('symptoms', [])
            symptoms_list = ', '.join([s.get('name', '') for s in symptoms if s.get('name')])

            # Format severity scores
            severity_scores = ', '.join([
                f"{s.get('name')}: {s.get('severity')}"
                for s in symptoms
                if s.get('name') and s.get('severity') is not None
            ])

            # Format triggers
            triggers = ', '.join(parsed_data.get('triggers', []))

            # Get mood/energy and summary
            mood_energy = parsed_data.get('mood_energy', '')
            summary = parsed_data.get('summary', '')

            # Parse success flag
            parsed_successfully = 'Yes' if parsed_data.get('parsed_successfully', False) else 'No'

            # Create row data
            # This must match the order of headers in _setup_worksheet()
            row_data = [
                timestamp,
                date_only,
                time_only,
                raw_message,
                symptoms_list,
                severity_scores,
                triggers,
                mood_energy,
                summary,
                parsed_successfully,
                entry_type,
                '',  # Cycle Day (Phase 3)
                '',  # Cycle Phase (Phase 3)
                '',  # Medications Taken (Phase 2)
                '',  # Notes
            ]

            # Append row to worksheet
            self.worksheet.append_row(row_data)

            logger.info(f"Successfully logged symptom entry: {summary}")
            return True

        except Exception as e:
            logger.error(f"Error logging symptom entry: {str(e)}", exc_info=True)
            return False

    def get_recent_entries(self, num_entries=10):
        """
        Retrieve the most recent symptom entries from the sheet.

        Useful for generating reports or showing recent history.

        Args:
            num_entries (int): Number of recent entries to retrieve

        Returns:
            list: List of dictionaries containing recent entries

        Example:
            >>> manager = SheetsManager()
            >>> recent = manager.get_recent_entries(5)
            >>> for entry in recent:
            ...     print(entry['Date'], entry['Symptoms List'])
        """
        try:
            # Get all records from the sheet
            all_records = self.worksheet.get_all_records()

            # Return the last N records
            recent_records = all_records[-num_entries:] if all_records else []

            logger.info(f"Retrieved {len(recent_records)} recent entries")
            return recent_records

        except Exception as e:
            logger.error(f"Error retrieving recent entries: {str(e)}", exc_info=True)
            return []

    def get_entry_count(self):
        """
        Get the total number of entries logged (excluding header row).

        Returns:
            int: Number of symptom entries in the sheet
        """
        try:
            # Get number of rows (subtract 1 for header)
            row_count = len(self.worksheet.get_all_values()) - 1
            return max(0, row_count)  # Don't return negative numbers
        except Exception as e:
            logger.error(f"Error getting entry count: {str(e)}", exc_info=True)
            return 0


# Example usage and testing
if __name__ == "__main__":
    """
    Test the Google Sheets manager.
    Run this file directly to test: python modules/sheets_manager.py
    """

    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)

    # Create manager instance
    manager = SheetsManager()

    # Test logging an entry
    test_data = {
        'symptoms': [
            {'name': 'bloating', 'severity': 7},
            {'name': 'nausea', 'severity': 5}
        ],
        'triggers': ['dairy', 'stress'],
        'mood_energy': 'tired, low energy',
        'summary': 'Bloating and nausea after lunch',
        'raw_message': 'Bad bloating today, 7/10. Nausea too, maybe 5/10. Had dairy at lunch and stressed about work.',
        'parsed_successfully': True
    }

    print("\nTesting Google Sheets Manager")
    print("=" * 50)

    print(f"\nCurrent entry count: {manager.get_entry_count()}")

    print("\nLogging test entry...")
    success = manager.log_symptom_entry(test_data, entry_type='manual')
    print(f"Log successful: {success}")

    print(f"\nNew entry count: {manager.get_entry_count()}")

    print("\nRecent entries:")
    recent = manager.get_recent_entries(3)
    for i, entry in enumerate(recent, 1):
        print(f"{i}. {entry.get('Date')} - {entry.get('Summary')}")
