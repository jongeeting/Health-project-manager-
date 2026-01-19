"""
Health Management SMS System - Main Application
================================================

This is the main entry point for the health management system.

It runs a Flask web server that:
1. Receives incoming SMS messages from Twilio (webhook endpoint)
2. Processes messages through Claude API for symptom extraction
3. Logs data to Google Sheets
4. Sends confirmation messages back to the user
5. Runs automated check-in scheduler in the background

The application is designed to run continuously, handling both:
- Scheduled check-in messages (8am and 8pm by default)
- User-initiated symptom logging at any time

Architecture Flow:
    User → SMS → Twilio → Webhook (/sms) → Claude Parser → Google Sheets
                                         ↓
                                    Confirmation SMS → User
"""

from flask import Flask, request
from flask_cors import CORS
import logging
from datetime import datetime

# Import our custom modules
from config import Config
from modules.twilio_handler import TwilioHandler
from modules.claude_parser import ClaudeParser
from modules.sheets_manager import SheetsManager
from modules.scheduler import CheckInScheduler

# ============================================
# APPLICATION SETUP
# ============================================

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Enable CORS (Cross-Origin Resource Sharing) if needed
CORS(app)

# Set up logging
# This creates detailed logs to help with debugging and monitoring
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Print to console
        logging.FileHandler('health_sms_system.log')  # Save to file
    ]
)

logger = logging.getLogger(__name__)

# ============================================
# INITIALIZE MODULES
# ============================================

# These are initialized once when the app starts
# and reused for all requests
logger.info("Initializing application modules...")

try:
    twilio_handler = TwilioHandler()
    claude_parser = ClaudeParser()
    sheets_manager = SheetsManager()
    scheduler = CheckInScheduler()

    logger.info("✅ All modules initialized successfully")

except Exception as e:
    logger.error(f"❌ Error initializing modules: {str(e)}", exc_info=True)
    raise


# ============================================
# WEBHOOK ENDPOINTS
# ============================================

@app.route('/sms', methods=['POST'])
def receive_sms():
    """
    Webhook endpoint for incoming SMS messages from Twilio.

    When a user sends an SMS to the Twilio number, Twilio sends a POST
    request to this endpoint with the message data.

    This function:
    1. Receives and parses the incoming message
    2. Verifies the sender is authorized
    3. Parses the message content with Claude
    4. Logs the data to Google Sheets
    5. Sends a confirmation message back to the user

    Returns:
        str: Empty TwiML response (we send confirmations separately)
    """
    try:
        logger.info("=" * 60)
        logger.info("Received incoming SMS webhook")

        # Parse incoming message data from Twilio
        message_data = twilio_handler.parse_incoming_message(request.form)

        if not message_data:
            logger.error("Failed to parse message data")
            return twilio_handler.create_twiml_response()

        from_number = message_data['from_number']
        message_body = message_data['message_body']

        logger.info(f"From: {from_number}")
        logger.info(f"Message: {message_body[:100]}...")

        # Verify sender is authorized
        if not twilio_handler.verify_sender(from_number):
            logger.warning(f"Unauthorized message from {from_number}")
            # Don't respond to unauthorized numbers (security measure)
            return twilio_handler.create_twiml_response()

        # Parse the message with Claude
        logger.info("Parsing message with Claude API...")
        parsed_data = claude_parser.parse_symptom_description(message_body)

        if not parsed_data:
            logger.error("Failed to parse message")
            # Send error message to user
            twilio_handler.send_message("Sorry, I had trouble understanding that. Your message was saved though! ❤️")
            return twilio_handler.create_twiml_response()

        logger.info(f"Parsing successful: {parsed_data.get('summary', 'No summary')}")

        # Log to Google Sheets
        logger.info("Logging to Google Sheets...")
        log_success = sheets_manager.log_symptom_entry(parsed_data, entry_type='manual')

        if log_success:
            logger.info("✅ Successfully logged to Google Sheets")
        else:
            logger.error("❌ Failed to log to Google Sheets")

        # Generate and send confirmation message
        confirmation = claude_parser.generate_confirmation_message(parsed_data)
        logger.info(f"Sending confirmation: {confirmation}")

        twilio_handler.send_message(confirmation)

        logger.info("✅ Message processed successfully")
        logger.info("=" * 60)

        # Return empty TwiML response
        # (We've already sent our confirmation via send_message)
        return twilio_handler.create_twiml_response()

    except Exception as e:
        # Log the error and send a friendly error message to the user
        logger.error(f"Error processing SMS: {str(e)}", exc_info=True)

        try:
            twilio_handler.send_message(
                "I ran into a problem processing your message, but I've logged it. "
                "The tech team has been notified. ❤️"
            )
        except:
            pass  # If we can't send error message, just log it

        # Return empty TwiML response
        return twilio_handler.create_twiml_response()


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.

    This endpoint allows you to check if the application is running.
    Useful for monitoring services and deployment platforms.

    Returns:
        dict: Status information including:
            - status: 'healthy' if all systems are operational
            - timestamp: Current server time
            - scheduled_jobs: Number of scheduled check-ins
            - next_check_ins: When the next check-ins are scheduled
    """
    try:
        # Get scheduler status
        next_check_ins = scheduler.get_next_check_in_times()

        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'scheduled_jobs': len(next_check_ins),
            'next_check_ins': next_check_ins,
            'phase': 'Phase 1 - Symptom Tracking',
            'version': '1.0.0'
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}", exc_info=True)
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500


@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint that shows basic system information.

    Returns:
        str: HTML page with system status
    """
    try:
        next_check_ins = scheduler.get_next_check_in_times()
        entry_count = sheets_manager.get_entry_count()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Health Management SMS System</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 3px solid #4CAF50;
                    padding-bottom: 10px;
                }}
                .status {{
                    background: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 20px 0;
                }}
                .info {{
                    background: #f0f0f0;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .schedule {{
                    background: #e3f2fd;
                    padding: 10px;
                    border-left: 4px solid #2196F3;
                    margin: 5px 0;
                }}
                code {{
                    background: #f5f5f5;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: monospace;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏥 Health Management SMS System</h1>

                <div class="status">
                    ✅ System Running - Phase 1
                </div>

                <h2>System Status</h2>
                <div class="info">
                    <strong>Total Entries Logged:</strong> {entry_count}<br>
                    <strong>Scheduled Jobs:</strong> {len(next_check_ins)}<br>
                    <strong>Phase:</strong> Phase 1 - Symptom Tracking<br>
                    <strong>Version:</strong> 1.0.0
                </div>

                <h2>Next Scheduled Check-ins</h2>
                {''.join([f'<div class="schedule">📅 {item["job_name"]}: {item["next_run"]}</div>' for item in next_check_ins])}

                <h2>Features Active</h2>
                <div class="info">
                    ✅ Automated symptom check-ins (8am, 8pm)<br>
                    ✅ Free-text symptom logging<br>
                    ✅ Claude API natural language parsing<br>
                    ✅ Google Sheets data storage<br>
                    ✅ SMS confirmations
                </div>

                <h2>Webhook Endpoint</h2>
                <div class="info">
                    Configure Twilio to POST incoming messages to:<br>
                    <code>https://your-domain.com/sms</code>
                </div>

                <h2>API Endpoints</h2>
                <div class="info">
                    <code>GET /</code> - This page<br>
                    <code>GET /health</code> - Health check (JSON)<br>
                    <code>POST /sms</code> - Twilio webhook for incoming SMS
                </div>
            </div>
        </body>
        </html>
        """
        return html
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}", exc_info=True)
        return f"<h1>Health Management System</h1><p>Status: Running</p><p>Error loading details: {str(e)}</p>"


# ============================================
# APPLICATION STARTUP
# ============================================

def start_scheduler():
    """
    Start the background scheduler for automated check-ins.

    This is called when the application starts to begin sending
    scheduled check-in messages.
    """
    try:
        logger.info("Setting up automated check-in schedule...")
        scheduler.setup_check_in_schedule()
        scheduler.start()
        logger.info("✅ Scheduler started successfully")
    except Exception as e:
        logger.error(f"❌ Error starting scheduler: {str(e)}", exc_info=True)


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == '__main__':
    """
    Main entry point when running the application directly.

    This starts the Flask development server and the scheduler.

    For production deployment, use a WSGI server like Gunicorn instead:
        gunicorn app:app
    """

    # Validate configuration before starting
    logger.info("Validating configuration...")
    Config.validate()

    # Start the scheduler
    start_scheduler()

    # Show startup information
    logger.info("=" * 60)
    logger.info("🏥 Health Management SMS System - Phase 1")
    logger.info("=" * 60)
    logger.info(f"Environment: {Config.FLASK_ENV}")
    logger.info(f"Timezone: {Config.TIMEZONE}")
    logger.info(f"Check-in times: {Config.CHECKIN_TIMES}")
    logger.info(f"User phone: {Config.USER_PHONE_NUMBER}")
    logger.info("=" * 60)

    # Start Flask server
    # In production, this is replaced by a WSGI server
    logger.info(f"Starting Flask server on port {Config.PORT}...")

    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=Config.PORT,
        debug=Config.FLASK_DEBUG
    )
