"""
Twilio SMS Handler Module
==========================
This module handles all SMS communication via Twilio.

It manages:
- Sending SMS messages to the user
- Receiving incoming SMS messages (via webhook)
- Formatting messages for readability
- Error handling and retry logic

Twilio is the SMS gateway that allows the system to send and receive
text messages programmatically.
"""

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from config import Config
import logging

# Set up logging
logger = logging.getLogger(__name__)


class TwilioHandler:
    """
    Handles SMS messaging through Twilio API.

    This class provides methods to send messages to the user and process
    incoming messages from Twilio webhooks.
    """

    def __init__(self):
        """
        Initialize the Twilio client.

        Sets up the Twilio REST API client using credentials from configuration.
        """
        try:
            self.client = Client(
                Config.TWILIO_ACCOUNT_SID,
                Config.TWILIO_AUTH_TOKEN
            )
            self.from_number = Config.TWILIO_PHONE_NUMBER
            self.to_number = Config.USER_PHONE_NUMBER

            logger.info("Twilio client initialized successfully")
            logger.info(f"Configured to send from {self.from_number} to {self.to_number}")

        except Exception as e:
            logger.error(f"Error initializing Twilio client: {str(e)}", exc_info=True)
            raise

    def send_message(self, message_text, to_number=None):
        """
        Send an SMS message to the user.

        Args:
            message_text (str): The message content to send
            to_number (str, optional): Phone number to send to.
                                      Defaults to USER_PHONE_NUMBER from config.

        Returns:
            bool: True if message sent successfully, False otherwise

        Example:
            >>> handler = TwilioHandler()
            >>> handler.send_message("How are you feeling today?")
            True
        """
        try:
            # Use configured user number if none specified
            recipient = to_number or self.to_number

            # Send the message via Twilio API
            message = self.client.messages.create(
                body=message_text,
                from_=self.from_number,
                to=recipient
            )

            logger.info(f"Message sent successfully. SID: {message.sid}")
            logger.debug(f"Message content: {message_text[:50]}...")

            return True

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}", exc_info=True)
            return False

    def send_check_in_message(self):
        """
        Send the automated symptom check-in message.

        This is the message sent twice daily asking the user how they're feeling.
        It's friendly and open-ended to encourage natural responses.

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        # The check-in message is intentionally simple and friendly
        # Users with ADHD often respond better to brief, clear prompts
        message = (
            "How are you feeling today? 💙\n\n"
            "Share any symptoms, how you're doing, or just say hi!"
        )

        logger.info("Sending automated check-in message")
        return self.send_message(message)

    def create_twiml_response(self, message_text=None):
        """
        Create a TwiML response for Twilio webhook.

        TwiML (Twilio Markup Language) is XML that tells Twilio how to respond
        to incoming messages. This is used in the webhook endpoint.

        Args:
            message_text (str, optional): Message to send back immediately.
                                         If None, no immediate response is sent.

        Returns:
            str: TwiML XML response

        Note:
            In most cases, we'll process the message and send a response separately
            using send_message() rather than using immediate TwiML responses.
            This gives us more control and better error handling.
        """
        response = MessagingResponse()

        if message_text:
            response.message(message_text)

        return str(response)

    def parse_incoming_message(self, request_data):
        """
        Parse incoming message data from Twilio webhook.

        When Twilio receives an SMS, it POSTs data to our webhook endpoint.
        This method extracts the relevant information from that request.

        Args:
            request_data (dict): The form data from Twilio's webhook POST request

        Returns:
            dict: Parsed message data containing:
                - from_number (str): Sender's phone number
                - message_body (str): Text content of the message
                - message_sid (str): Twilio's unique message identifier
                - timestamp (str): When the message was received

        Example:
            >>> # In Flask webhook:
            >>> message_data = handler.parse_incoming_message(request.form)
            >>> print(message_data['message_body'])
            "Feeling bloated today, 7/10"
        """
        try:
            parsed_data = {
                'from_number': request_data.get('From', ''),
                'message_body': request_data.get('Body', ''),
                'message_sid': request_data.get('MessageSid', ''),
                'to_number': request_data.get('To', ''),
                'timestamp': request_data.get('DateSent', '')
            }

            logger.info(f"Received message from {parsed_data['from_number']}")
            logger.debug(f"Message body: {parsed_data['message_body'][:50]}...")

            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing incoming message: {str(e)}", exc_info=True)
            return None

    def verify_sender(self, from_number):
        """
        Verify that an incoming message is from the authorized user.

        This is a security measure to ensure only the user's phone number
        can log health data.

        Args:
            from_number (str): Phone number that sent the message

        Returns:
            bool: True if sender is authorized, False otherwise
        """
        # Normalize phone numbers for comparison
        # Remove spaces, dashes, parentheses
        def normalize_number(number):
            return ''.join(filter(str.isdigit, number))

        authorized = normalize_number(self.to_number)
        sender = normalize_number(from_number)

        is_verified = (sender == authorized)

        if not is_verified:
            logger.warning(f"Unauthorized message from {from_number}")
        else:
            logger.info(f"Verified message from authorized user")

        return is_verified


# Example usage and testing
if __name__ == "__main__":
    """
    Test the Twilio handler.
    Run this file directly to test: python modules/twilio_handler.py

    WARNING: This will send a real SMS if your Twilio credentials are configured!
    """

    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)

    print("\nTesting Twilio Handler")
    print("=" * 50)

    # Create handler instance
    handler = TwilioHandler()

    # Test sending a message
    print("\n⚠️  This will send a real SMS to your configured number!")
    print(f"Recipient: {Config.USER_PHONE_NUMBER}")

    response = input("\nProceed with sending test message? (yes/no): ")

    if response.lower() == 'yes':
        print("\nSending test message...")
        success = handler.send_message("This is a test message from your Health Management System! 💙")

        if success:
            print("✅ Test message sent successfully!")
            print(f"Check your phone ({Config.USER_PHONE_NUMBER}) for the message.")
        else:
            print("❌ Failed to send test message. Check your Twilio credentials.")
    else:
        print("Test cancelled.")

    # Test TwiML response creation
    print("\nTesting TwiML response creation...")
    twiml = handler.create_twiml_response("Thanks for your message!")
    print(f"TwiML response:\n{twiml}")

    # Test incoming message parsing (simulated data)
    print("\nTesting incoming message parsing...")
    simulated_webhook_data = {
        'From': '+1234567890',
        'Body': 'Feeling good today!',
        'MessageSid': 'SM1234567890abcdef',
        'To': Config.TWILIO_PHONE_NUMBER,
        'DateSent': '2024-01-15 10:30:00'
    }

    parsed = handler.parse_incoming_message(simulated_webhook_data)
    print(f"Parsed message data: {parsed}")

    # Test sender verification
    print("\nTesting sender verification...")
    is_verified = handler.verify_sender(Config.USER_PHONE_NUMBER)
    print(f"User's number verified: {is_verified}")

    is_verified = handler.verify_sender('+9999999999')
    print(f"Unknown number verified: {is_verified}")
