"""
Claude API Parser Module
=========================
This module uses the Claude API to parse free-text symptom descriptions
into structured data that can be stored and analyzed.

It extracts:
- List of symptoms mentioned
- Severity ratings (0-10 scale)
- Potential triggers (foods, activities, stress events)
- Mood and energy level notes
- Any other relevant health information

The module uses Claude's natural language understanding to handle various
ways people might describe symptoms naturally.
"""

import anthropic
from config import Config
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)


class ClaudeParser:
    """
    Handles parsing of symptom descriptions using Claude API.

    This class provides methods to send symptom text to Claude and receive
    structured data back, making it easy to log and analyze health information.
    """

    def __init__(self):
        """
        Initialize the Claude API client.

        Sets up the Anthropic client with the API key from configuration.
        """
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        logger.info("Claude API client initialized")

    def parse_symptom_description(self, message_text):
        """
        Parse a free-text symptom description into structured data.

        This method sends the user's message to Claude with specific instructions
        to extract symptom information in a structured format.

        Args:
            message_text (str): The user's free-text symptom description

        Returns:
            dict: Structured symptom data containing:
                - symptoms (list): List of symptoms with names and severity
                - triggers (list): Potential triggers mentioned
                - mood_notes (str): General mood/energy observations
                - raw_message (str): Original message text
                - parsed_successfully (bool): Whether parsing succeeded

        Example:
            >>> parser = ClaudeParser()
            >>> result = parser.parse_symptom_description("Bad bloating today, 7/10. Had dairy at lunch.")
            >>> print(result['symptoms'])
            [{'name': 'bloating', 'severity': 7}]
        """
        try:
            logger.info(f"Parsing symptom description: {message_text[:50]}...")

            # Create the prompt for Claude
            # This prompt instructs Claude to extract specific information
            # and return it in a JSON format we can easily parse
            system_prompt = """You are a health symptom parser. Extract health information from user messages.

Extract the following information:
1. SYMPTOMS: Any symptoms mentioned (bloating, nausea, pain, constipation, night sweats, etc.)
   - Include severity if mentioned (0-10 scale)
   - Note location if specified (e.g., "abdominal pain")

2. TRIGGERS: Potential causes or correlations mentioned
   - Foods eaten
   - Activities
   - Stress or emotional events
   - Sleep quality

3. MOOD/ENERGY: General wellbeing notes
   - Energy level
   - Mood
   - Sleep quality

Return ONLY a JSON object with this structure:
{
    "symptoms": [
        {"name": "symptom_name", "severity": number_or_null, "notes": "additional details"}
    ],
    "triggers": ["trigger1", "trigger2"],
    "mood_energy": "brief summary of mood/energy",
    "summary": "one-sentence summary of the report"
}

If the message is not health-related, return:
{
    "symptoms": [],
    "triggers": [],
    "mood_energy": "",
    "summary": "Non-health related message",
    "is_health_related": false
}

Be understanding and compassionate. Extract as much useful information as possible."""

            # Send the message to Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Using Claude 3.5 Sonnet for accurate parsing
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": message_text
                    }
                ]
            )

            # Extract the response text
            response_text = message.content[0].text

            logger.debug(f"Claude response: {response_text}")

            # Parse the JSON response
            try:
                parsed_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If Claude didn't return valid JSON, try to extract it
                # Sometimes Claude adds explanatory text around the JSON
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from Claude response")

            # Add metadata
            parsed_data['raw_message'] = message_text
            parsed_data['parsed_successfully'] = True

            # Ensure is_health_related defaults to True if not specified
            if 'is_health_related' not in parsed_data:
                parsed_data['is_health_related'] = True

            logger.info(f"Successfully parsed symptoms: {len(parsed_data.get('symptoms', []))} symptoms found")

            return parsed_data

        except Exception as e:
            # If anything goes wrong, return a safe default structure
            logger.error(f"Error parsing symptom description: {str(e)}", exc_info=True)
            return {
                'symptoms': [],
                'triggers': [],
                'mood_energy': '',
                'summary': 'Error parsing message',
                'raw_message': message_text,
                'parsed_successfully': False,
                'error': str(e)
            }

    def generate_confirmation_message(self, parsed_data):
        """
        Generate a friendly confirmation message to send back to the user.

        This creates a short, reassuring message that confirms what was logged,
        making the user feel heard and showing that the system understood them.

        Args:
            parsed_data (dict): The parsed symptom data from parse_symptom_description()

        Returns:
            str: A friendly confirmation message

        Example:
            >>> confirmation = parser.generate_confirmation_message(parsed_data)
            >>> print(confirmation)
            "Logged! Bloating (7/10), nausea. Trigger: dairy. Feel better ❤️"
        """
        if not parsed_data.get('parsed_successfully', False):
            return "Got your message! I had trouble parsing it, but it's saved. ❤️"

        if not parsed_data.get('is_health_related', True):
            # Non-health message - acknowledge but don't log as symptoms
            return "Got your message! 💙"

        # Build confirmation message parts
        parts = []

        # Add symptoms
        symptoms = parsed_data.get('symptoms', [])
        if symptoms:
            symptom_strs = []
            for symptom in symptoms:
                name = symptom.get('name', 'symptom')
                severity = symptom.get('severity')
                if severity is not None:
                    symptom_strs.append(f"{name} ({severity}/10)")
                else:
                    symptom_strs.append(name)
            parts.append(", ".join(symptom_strs))

        # Add triggers if any
        triggers = parsed_data.get('triggers', [])
        if triggers:
            if len(triggers) == 1:
                parts.append(f"Trigger: {triggers[0]}")
            else:
                parts.append(f"Triggers: {', '.join(triggers)}")

        # Add mood/energy if meaningful
        mood_energy = parsed_data.get('mood_energy', '').strip()
        if mood_energy and len(mood_energy) > 3:  # Only include if substantial
            parts.append(mood_energy)

        # Construct final message
        if parts:
            confirmation = "Logged! " + ". ".join(parts) + ". Feel better ❤️"
        else:
            confirmation = "Logged your update! ❤️"

        # Keep it under 160 characters for single SMS (if possible)
        if len(confirmation) > 160:
            # Simplify if too long
            if symptoms:
                symptom_names = [s.get('name', 'symptom') for s in symptoms[:3]]
                confirmation = f"Logged! {', '.join(symptom_names)}. Feel better ❤️"

        return confirmation


# Example usage and testing
if __name__ == "__main__":
    """
    Test the Claude parser with example symptom descriptions.
    Run this file directly to test: python modules/claude_parser.py
    """

    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)

    # Create parser instance
    parser = ClaudeParser()

    # Test cases
    test_messages = [
        "Bad bloating today, probably 7/10. Had dairy at lunch which might be the cause.",
        "Feeling pretty good! Energy is high, no major symptoms.",
        "Night sweats again. Constipation too. Feeling exhausted.",
        "Severe abdominal pain, 9/10. Can barely move. Started after dinner.",
    ]

    print("Testing Claude Parser")
    print("=" * 50)

    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: {message}")
        print("-" * 50)

        result = parser.parse_symptom_description(message)
        print(f"Parsed: {json.dumps(result, indent=2)}")

        confirmation = parser.generate_confirmation_message(result)
        print(f"Confirmation: {confirmation}")
