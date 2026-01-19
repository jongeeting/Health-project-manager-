# Complete Setup Guide
# Health Management SMS System - Phase 1

This guide will walk you through setting up the health management system from scratch. Follow each step carefully, and you'll have a fully functional symptom tracking system running in about 30-45 minutes.

## Prerequisites

Before you begin, make sure you have:
- A computer with internet access
- A Gmail account (for Google Sheets and Calendar)
- A phone number that can receive SMS (your personal phone)
- Credit card for Twilio (though you'll start with free credits)
- Basic comfort with using a terminal/command line

---

## Step 1: Install Python and Dependencies

### 1.1 Install Python 3.9 or Higher

**On Mac:**
```bash
# Install using Homebrew (recommended)
brew install python@3.11

# Verify installation
python3 --version
```

**On Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **Important:** Check "Add Python to PATH" during installation
4. Verify: Open Command Prompt and run `python --version`

**On Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3-pip
python3 --version
```

### 1.2 Set Up Project Directory

```bash
# Navigate to where you want the project
cd ~

# Clone or download the project
# If you have git:
git clone <your-repo-url> health-sms-system
cd health-sms-system

# Or if you downloaded a zip:
unzip health-sms-system.zip
cd health-sms-system
```

### 1.3 Create Virtual Environment

A virtual environment keeps this project's dependencies separate from other Python projects.

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Your terminal prompt should now show (venv) at the beginning
```

### 1.4 Install Required Packages

```bash
# Install all dependencies
pip install -r requirements.txt

# This will take a few minutes
# You should see all packages installing successfully
```

---

## Step 2: Set Up Twilio (SMS Service)

Twilio is the service that sends and receives text messages. You'll get free trial credits to start.

### 2.1 Create Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Sign up with your email
3. Verify your email and phone number
4. You'll get **$15 in free trial credits** (enough for ~1000 messages)

### 2.2 Get Your Twilio Phone Number

1. After signing up, you'll be prompted to "Get a Trial Number"
2. Click **"Get a Trial Number"**
3. Twilio will assign you a number - click **"Choose this Number"**
4. **Write this number down** - you'll need it for configuration

### 2.3 Find Your Account Credentials

1. From the Twilio Console dashboard (https://console.twilio.com)
2. You'll see:
   - **Account SID** (starts with "AC...")
   - **Auth Token** (click to reveal)
3. **Copy both of these** - you'll need them in Step 5

### 2.4 Configure Webhook (We'll come back to this after deployment)

We'll set up the webhook URL after deploying the application. For now, just remember you'll need to do this.

---

## Step 3: Set Up Claude API

Claude is the AI that understands your symptom descriptions naturally.

### 3.1 Create Anthropic Account

1. Go to https://console.anthropic.com
2. Sign up with your email
3. Verify your email

### 3.2 Get API Key

1. Go to https://console.anthropic.com/settings/keys
2. Click **"Create Key"**
3. Give it a name like "Health SMS System"
4. **Copy the API key** - you'll only see it once!
5. Store it safely (you'll add it to .env file in Step 5)

### 3.3 Add Credits

1. Go to https://console.anthropic.com/settings/billing
2. Add a payment method
3. You'll be charged based on usage (very low for this use case)
4. Typical cost: ~$0.01-0.05 per day for twice-daily check-ins

---

## Step 4: Set Up Google Sheets

Google Sheets will store all your health data in an easy-to-view spreadsheet.

### 4.1 Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Click **"Select a Project"** → **"New Project"**
3. Name it "Health SMS System"
4. Click **"Create"**

### 4.2 Enable Google Sheets API

1. In the Google Cloud Console, click **"APIs & Services"** → **"Library"**
2. Search for **"Google Sheets API"**
3. Click on it and click **"Enable"**
4. Also search for and enable **"Google Drive API"**

### 4.3 Create Service Account

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"Service Account"**
3. Name it "health-sms-bot"
4. Click **"Create and Continue"**
5. For role, select **"Editor"**
6. Click **"Continue"** then **"Done"**

### 4.4 Download Credentials JSON

1. On the Credentials page, find your service account (health-sms-bot@...)
2. Click on it
3. Go to **"Keys"** tab
4. Click **"Add Key"** → **"Create New Key"**
5. Choose **JSON** format
6. Click **"Create"** - a JSON file will download

### 4.5 Set Up Credentials File

```bash
# Create credentials directory in your project
mkdir -p credentials

# Move the downloaded JSON file to the credentials folder
# Replace YOUR-PROJECT-NAME and path with your actual file
mv ~/Downloads/health-sms-system-*.json credentials/google_sheets_credentials.json

# Verify the file is there
ls credentials/
```

### 4.6 Create Your Health Tracking Spreadsheet

1. Go to https://sheets.google.com
2. Create a new spreadsheet
3. Name it **"Health Tracking Data"** (exactly this name, or update .env later)
4. Open the JSON credentials file you downloaded:
   ```bash
   cat credentials/google_sheets_credentials.json
   ```
5. Look for the "client_email" field (looks like: health-sms-bot@...iam.gserviceaccount.com)
6. Copy that email address
7. In your Google Sheet, click **Share**
8. Paste the service account email
9. Give it **Editor** access
10. Uncheck "Notify people"
11. Click **Share**

**Important:** The sheet will be auto-configured with proper columns when you first run the app!

---

## Step 5: Configure Environment Variables

Now we'll put all your credentials into a configuration file.

### 5.1 Create .env File

```bash
# Copy the example file
cp .env.example .env
```

### 5.2 Edit .env File

Open the .env file in a text editor:

```bash
# On Mac/Linux:
nano .env

# On Windows:
notepad .env

# Or use any text editor you prefer
```

### 5.3 Fill in Your Credentials

Replace all the placeholder values with your actual credentials:

```bash
# ============================================
# TWILIO CONFIGURATION
# ============================================
TWILIO_ACCOUNT_SID=AC1234567890abcdef...  # From Step 2.3
TWILIO_AUTH_TOKEN=your_auth_token_here     # From Step 2.3
TWILIO_PHONE_NUMBER=+15551234567           # From Step 2.2 (include +1)

# Your personal phone number (where you'll receive messages)
USER_PHONE_NUMBER=+15559876543             # Your cell phone (include +1)

# ============================================
# CLAUDE API CONFIGURATION
# ============================================
ANTHROPIC_API_KEY=sk-ant-...               # From Step 3.2

# ============================================
# GOOGLE SHEETS CONFIGURATION
# ============================================
GOOGLE_SHEET_NAME=Health Tracking Data     # From Step 4.6
GOOGLE_CREDENTIALS_PATH=credentials/google_sheets_credentials.json

# ============================================
# APPLICATION CONFIGURATION
# ============================================
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_random_secret_key_here     # Generate below

# ============================================
# SCHEDULED CHECK-IN TIMES
# ============================================
CHECKIN_TIMES=08:00,20:00                  # 8am and 8pm
TIMEZONE=America/New_York                  # Your timezone
```

### 5.4 Generate Secret Key

```bash
# Run this to generate a secure secret key:
python3 -c "import secrets; print(secrets.token_hex(32))"

# Copy the output and paste it as your SECRET_KEY in .env
```

### 5.5 Set Your Timezone

Find your timezone from this list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

Common examples:
- `America/New_York` (Eastern Time)
- `America/Chicago` (Central Time)
- `America/Denver` (Mountain Time)
- `America/Los_Angeles` (Pacific Time)
- `America/Phoenix` (Arizona)

### 5.6 Customize Check-in Times (Optional)

You can change when you receive check-in messages:

```bash
# Default (8am and 8pm):
CHECKIN_TIMES=08:00,20:00

# Morning and evening:
CHECKIN_TIMES=07:00,21:00

# Three times a day:
CHECKIN_TIMES=08:00,14:00,20:00

# Just once a day:
CHECKIN_TIMES=20:00
```

Use 24-hour format (00:00 to 23:59).

---

## Step 6: Test the Installation

Let's make sure everything is working before deploying.

### 6.1 Validate Configuration

```bash
# Make sure virtual environment is activated
# You should see (venv) in your terminal prompt

# Test configuration validation
python3 config.py
```

You should see: `✅ Configuration validated successfully!`

If you see errors, double-check your .env file.

### 6.2 Test Claude Parser

```bash
# Test the Claude API integration
python3 modules/claude_parser.py
```

You should see test messages being parsed successfully.

### 6.3 Test Google Sheets

```bash
# Test Google Sheets connection
python3 modules/sheets_manager.py
```

This will:
- Connect to your Google Sheet
- Create the proper column headers
- Log a test entry
- Show recent entries

Go to your Google Sheet and verify you see the test data!

### 6.4 Test Twilio (Optional - sends real SMS)

```bash
# Test sending an SMS
python3 modules/twilio_handler.py

# When prompted, type 'yes' to send a test message
# Check your phone - you should receive a test SMS!
```

**Note:** This uses your Twilio trial credits. Only run if you want to test SMS.

---

## Step 7: Run the Application Locally

Let's run the full application on your computer first.

### 7.1 Start the Application

```bash
# Make sure you're in the project directory with venv activated
python3 app.py
```

You should see:
```
✅ Configuration validated successfully!
✅ All modules initialized successfully
✅ Scheduler started successfully
🏥 Health Management SMS System - Phase 1
Starting Flask server on port 5000...
```

### 7.2 Check the Web Interface

Open a web browser and go to: http://localhost:5000

You should see a status page showing:
- System running
- Next scheduled check-ins
- Active features

### 7.3 Test the Health Endpoint

Go to: http://localhost:5000/health

You should see JSON with system status.

### 7.4 Keep It Running

The application is now running on your computer! But it's only accessible locally.

**To stop it:** Press `Ctrl+C` in the terminal

**Important:** For the system to work 24/7, you need to deploy it to a server (see Step 8).

---

## Step 8: Quick Local Testing

Before deploying, let's test receiving a message locally using ngrok.

### 8.1 Install ngrok

ngrok creates a temporary public URL to your local server (for testing).

1. Go to https://ngrok.com/download
2. Sign up for free account
3. Download ngrok for your operating system
4. Follow their installation instructions

### 8.2 Start ngrok Tunnel

```bash
# In a NEW terminal window (keep app.py running in the first one)
ngrok http 5000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5000
```

Copy that HTTPS URL (e.g., `https://abc123.ngrok.io`).

### 8.3 Configure Twilio Webhook Temporarily

1. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click on your Twilio phone number
3. Scroll to "Messaging Configuration"
4. Under "A message comes in":
   - Set the URL to: `https://YOUR-NGROK-URL.ngrok.io/sms`
   - Set method to: `POST`
5. Click **Save**

### 8.4 Send a Test Message

Send an SMS from your phone to your Twilio number:

```
Feeling bloated today, maybe 7/10. Had dairy at lunch.
```

You should:
1. See the message appear in your app.py terminal logs
2. Receive a confirmation SMS back
3. See the data logged in your Google Sheet!

**Troubleshooting:**
- Check the app.py terminal for error messages
- Check the ngrok terminal for incoming requests
- Verify your webhook URL is correct in Twilio console
- Make sure you're texting FROM the number you set as USER_PHONE_NUMBER

---

## Next Steps

You're all set up! Now you need to deploy the application to run 24/7.

See **DEPLOYMENT.md** for instructions on deploying to:
- **Render.com** (Recommended - Free tier, easiest)
- **Railway.app** (Alternative - Free trial)
- **Heroku** (Classic option)
- **DigitalOcean** (More control, $5/month)

---

## Common Issues and Solutions

### "Module not found" errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "Google Sheets credentials not found"
```bash
# Verify the file exists
ls credentials/google_sheets_credentials.json

# Check the path in .env matches
cat .env | grep GOOGLE_CREDENTIALS_PATH
```

### "Failed to authenticate with Google Sheets"
- Make sure you shared the spreadsheet with the service account email
- Check that the JSON file is valid JSON (open it in a text editor)
- Verify you enabled both Google Sheets API and Google Drive API

### "Twilio authentication failed"
- Double-check your Account SID starts with "AC"
- Verify your Auth Token is correct (it's sensitive to copy/paste errors)
- Make sure there are no extra spaces in your .env file

### "Claude API error"
- Verify your API key starts with "sk-ant-"
- Check you have credits in your Anthropic account
- Visit https://console.anthropic.com/settings/billing

### Messages not being received
- Verify webhook URL is set correctly in Twilio console
- Make sure webhook URL is HTTPS (not HTTP)
- Check that your app is running and accessible
- Look at Twilio's error logs: https://console.twilio.com/us1/monitor/logs/errors

---

## Security Best Practices

1. **Never commit your .env file to git** (it's already in .gitignore)
2. **Never share your credentials** publicly
3. **Rotate your API keys** if you think they've been compromised
4. **Use HTTPS** for your webhook URL in production
5. **Keep your service account credentials** safe

---

## Getting Help

If you run into issues:

1. Check the logs: `tail -f health_sms_system.log`
2. Review the error messages carefully
3. Verify each step in this guide
4. Check that all services (Twilio, Claude, Google) are active
5. Review the TESTING.md guide for debugging procedures

---

## You Did It! 🎉

If you made it through all the tests, your Phase 1 system is ready!

You can now:
- ✅ Receive automated check-in messages
- ✅ Text symptom descriptions naturally
- ✅ Get intelligent parsing and data extraction
- ✅ Have everything logged to Google Sheets automatically
- ✅ Receive friendly confirmations

**Next:** Deploy the system (see DEPLOYMENT.md) so it runs 24/7!
