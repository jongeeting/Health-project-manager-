# Quick Start Guide
# Health Management SMS System

Get your health management system up and running in 30 minutes!

---

## What This System Does

This is a text-message-based health tracking system that helps you:
- Log symptoms naturally via SMS
- Get automated check-in prompts twice daily
- Track patterns in your health data
- Manage chronic conditions with less cognitive load

**Phase 1 Features:**
- ✅ Text "Feeling bloated, 7/10, had dairy" and it automatically logs symptoms, severity, and triggers
- ✅ Receive friendly check-ins at 8am and 8pm (customizable)
- ✅ All data stored in Google Sheets for easy viewing
- ✅ Natural language parsing - just text like you normally would!

---

## Prerequisites (5 minutes)

You'll need accounts for these services (all have free tiers):

1. **Twilio** - Sends/receives SMS
   - Free trial: $15 credit (~1000 messages)
   - Sign up: https://www.twilio.com/try-twilio

2. **Anthropic (Claude API)** - Parses your messages
   - Cost: ~$1-5/month for typical use
   - Sign up: https://console.anthropic.com

3. **Google Cloud** - For Google Sheets API
   - Free for this use case
   - Sign up: https://console.cloud.google.com

4. **GitHub** (optional but recommended for deployment)
   - Free
   - Sign up: https://github.com

---

## Installation Path

Choose your path based on your comfort level:

### Path A: Follow Detailed Guides (Recommended for Beginners)
**Time: 45-60 minutes**

1. [Complete Setup Guide](docs/SETUP.md) - Step-by-step instructions
2. [Testing Guide](docs/TESTING.md) - Verify everything works
3. [Deployment Guide](docs/DEPLOYMENT.md) - Get it running 24/7

### Path B: Quick Setup (For Experienced Developers)
**Time: 20-30 minutes**

```bash
# 1. Clone and install
git clone <repo-url> health-sms-system
cd health-sms-system
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your credentials (see below)

# 3. Set up Google Sheets credentials
# - Create service account in Google Cloud Console
# - Download JSON credentials
# - Save as credentials/google_sheets_credentials.json
# - Create Google Sheet named "Health Tracking Data"
# - Share sheet with service account email

# 4. Test
python3 config.py  # Validate configuration
python3 modules/claude_parser.py  # Test Claude
python3 modules/sheets_manager.py  # Test Google Sheets

# 5. Run
python3 app.py

# 6. Deploy (see DEPLOYMENT.md)
```

---

## What You Need in Your .env File

```bash
# Twilio (get from https://console.twilio.com)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+15551234567  # Twilio number
USER_PHONE_NUMBER=+15559876543    # Your personal phone

# Claude API (get from https://console.anthropic.com/settings/keys)
ANTHROPIC_API_KEY=sk-ant-...

# Google Sheets
GOOGLE_SHEET_NAME=Health Tracking Data
GOOGLE_CREDENTIALS_PATH=credentials/google_sheets_credentials.json

# App Configuration
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
CHECKIN_TIMES=08:00,20:00
TIMEZONE=America/New_York  # Your timezone
```

---

## Testing Your Setup

After installation, test each component:

```bash
# Activate virtual environment first
source venv/bin/activate

# Test 1: Configuration
python3 config.py
# Should see: ✅ Configuration validated successfully!

# Test 2: Claude parsing
python3 modules/claude_parser.py
# Should parse test symptom descriptions

# Test 3: Google Sheets
python3 modules/sheets_manager.py
# Should create sheet headers and log test entry

# Test 4: Full app
python3 app.py
# Should start server and scheduler
# Visit http://localhost:5000 to see status page
```

---

## Your First Text Message

Once deployed (or testing locally with ngrok):

1. **Text your Twilio number:**
   ```
   Feeling bloated today, probably 7/10. Had dairy at lunch which might be the cause.
   ```

2. **You should receive:**
   ```
   Logged! bloating (7/10). Trigger: dairy. Feel better ❤️
   ```

3. **Check your Google Sheet** - you'll see:
   - Timestamp
   - Symptoms: "bloating"
   - Severity: "bloating: 7"
   - Triggers: "dairy"
   - Summary and raw message

---

## Common Issues

### "Module not found"
```bash
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
```

### "Google Sheets credentials not found"
- Make sure file is at: `credentials/google_sheets_credentials.json`
- Download from Google Cloud Console (see SETUP.md Step 4)

### "Twilio authentication failed"
- Check Account SID starts with "AC"
- Verify Auth Token is correct
- No spaces in .env file

### Webhooks not working
- Need public URL (use ngrok for testing, or deploy)
- Webhook must be HTTPS
- URL must end with `/sms`
- Set to POST method in Twilio console

---

## Cost Breakdown

**Trial/Free Tier:**
- Twilio: $15 free credit (lasts months for 1 user)
- Claude API: ~$1-5/month
- Google Sheets: Free
- Hosting: Can be free with Render.com

**Recommended Production:**
- Twilio: ~$1-2/month
- Claude API: ~$1-5/month
- Hosting: $0-7/month (Render free tier or $7 paid)
- **Total: ~$2-14/month**

---

## Next Steps

### Immediate (Today)
1. Complete setup following [SETUP.md](docs/SETUP.md)
2. Test all components with [TESTING.md](docs/TESTING.md)
3. Send a few test messages

### This Week
1. Deploy to cloud platform using [DEPLOYMENT.md](docs/DEPLOYMENT.md)
2. Set check-in times that work for you
3. Use it daily to track symptoms

### After 1-2 Weeks
1. Review your Google Sheet data
2. Note what's working and what you'd improve
3. Consider moving to Phase 2 (Medication Tracking)

---

## File Structure Overview

```
health-sms-system/
├── app.py                   # Main application (start here)
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env                    # Your credentials (create from .env.example)
│
├── modules/                # Core functionality
│   ├── twilio_handler.py  # SMS sending/receiving
│   ├── claude_parser.py   # Natural language parsing
│   ├── sheets_manager.py  # Google Sheets integration
│   └── scheduler.py       # Automated check-ins
│
├── docs/                  # Comprehensive guides
│   ├── SETUP.md          # Complete setup instructions
│   ├── TESTING.md        # Testing procedures
│   └── DEPLOYMENT.md     # Deployment guide
│
└── credentials/          # Google API credentials
    └── google_sheets_credentials.json
```

---

## Getting Help

**For Setup Issues:**
- See [SETUP.md](docs/SETUP.md) for detailed instructions
- Check [TESTING.md](docs/TESTING.md) for troubleshooting

**For Deployment:**
- See [DEPLOYMENT.md](docs/DEPLOYMENT.md)
- Each platform has step-by-step instructions

**For Debugging:**
- Check logs: `tail -f health_sms_system.log`
- Check Twilio error logs in console
- Review Claude API usage in Anthropic console

---

## Philosophy

This system is designed specifically for:
- **ADHD-friendly:** Text-based, minimal friction, automatic prompts
- **Chronic condition management:** Track patterns over time
- **Low cognitive load:** Just text naturally, system handles the rest
- **Privacy-first:** Your data stays in your Google Sheet
- **Customizable:** Change times, add features as needed

---

## Future Phases (Coming Soon)

- **Phase 2:** Medication tracking & refill reminders
- **Phase 3:** Menstrual cycle tracking & symptom correlation
- **Phase 4:** Appointment management & email monitoring
- **Phase 5:** Provider coordination
- **Phase 6:** Insights & pattern detection
- **Phase 7:** Insurance & claims tracking

---

## Ready to Start?

1. **New to this?** → Start with [SETUP.md](docs/SETUP.md)
2. **Experienced developer?** → Jump to installation commands above
3. **Questions?** → Check the docs/ folder for detailed guides

Let's get you tracking your health more easily! 💙
