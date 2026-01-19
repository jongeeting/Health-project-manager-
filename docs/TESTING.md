# Testing Guide
# Health Management SMS System - Phase 1

This guide helps you test each component of the system and debug any issues.

---

## Testing Philosophy

Each module can be tested independently, which makes it easier to identify exactly where problems occur. Always test in this order:

1. **Configuration** (do credentials load?)
2. **Individual modules** (does each service work?)
3. **Integration** (do they work together?)
4. **End-to-end** (does the full workflow work?)

---

## Pre-Test Checklist

Before running any tests:

```bash
# 1. Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 2. Verify you're in the project directory
pwd  # Should show path to health-sms-system

# 3. Check .env file exists and has all values
cat .env | grep "="  # Should show all your configured values
```

---

## Test 1: Configuration Validation

**What this tests:** Whether all environment variables are properly set.

```bash
python3 config.py
```

**Expected output:**
```
✅ Configuration validated successfully!
```

**If it fails:**
- Check for missing environment variables (error will tell you which ones)
- Verify .env file exists in the project root
- Check for typos in variable names
- Ensure no extra spaces around the `=` in .env file

---

## Test 2: Claude API Parser

**What this tests:** Claude API connection and symptom parsing.

```bash
python3 modules/claude_parser.py
```

**Expected output:**
```
Testing Claude Parser
==================================================

Test 1: Bad bloating today, probably 7/10...
--------------------------------------------------
Parsed: {
  "symptoms": [
    {"name": "bloating", "severity": 7, "notes": ""}
  ],
  "triggers": ["dairy"],
  "mood_energy": "",
  "summary": "Bloating after eating dairy"
}
Confirmation: Logged! bloating (7/10). Trigger: dairy. Feel better ❤️

[... more test cases ...]
```

**If it fails:**

**Error: "Module 'anthropic' not found"**
```bash
pip install anthropic
```

**Error: "Authentication error"**
- Check your ANTHROPIC_API_KEY in .env
- Verify it starts with "sk-ant-"
- Try creating a new API key at https://console.anthropic.com/settings/keys

**Error: "Insufficient credits"**
- Add credits at https://console.anthropic.com/settings/billing
- Need at least $1-5 to start

**API call succeeds but parsing fails:**
- This is okay if it's handling the error gracefully
- Check the `parsed_successfully` field in the output
- The system will still save the raw message

---

## Test 3: Google Sheets Manager

**What this tests:** Google Sheets API connection and data logging.

```bash
python3 modules/sheets_manager.py
```

**Expected output:**
```
Testing Google Sheets Manager
==================================================
Authenticating with Google Sheets using: credentials/google_sheets_credentials.json
Opened existing sheet: Health Tracking Data
Found existing 'Symptom Tracking' worksheet
Headers already exist
Google Sheets connection established successfully

Current entry count: 5

Logging test entry...
Successfully logged symptom entry: Bloating and nausea after lunch
Log successful: True

New entry count: 6

Recent entries:
1. 2024-01-15 - Previous entry summary
2. 2024-01-15 - Another entry
3. 2024-01-15 - Bloating and nausea after lunch
```

**Then check your actual Google Sheet:**
1. Open https://sheets.google.com
2. Find "Health Tracking Data"
3. You should see the test entry with all columns filled

**If it fails:**

**Error: "Credentials file not found"**
```bash
# Verify file exists
ls credentials/google_sheets_credentials.json

# If missing, review Step 4 of SETUP.md
```

**Error: "Failed to authenticate"**
- Make sure you enabled Google Sheets API AND Google Drive API
- Verify the credentials JSON file is valid:
  ```bash
  cat credentials/google_sheets_credentials.json
  # Should show valid JSON, not an error page
  ```

**Error: "Spreadsheet not found"**
- Make sure the sheet is named exactly "Health Tracking Data"
- Or update GOOGLE_SHEET_NAME in .env to match your sheet name
- Verify you shared the sheet with the service account email

**Error: "Permission denied"**
- Open the Google Sheet
- Click Share
- Find the service account email (from the JSON file: `client_email` field)
- Make sure it has Editor permissions

**Headers not appearing in sheet:**
- Delete the sheet completely and run the test again
- The script will recreate it with proper headers

---

## Test 4: Twilio SMS Handler

**What this tests:** Twilio API connection and SMS sending.

**⚠️ WARNING:** This test sends a REAL SMS to your phone and uses Twilio credits!

```bash
python3 modules/twilio_handler.py
```

**Expected output:**
```
Testing Twilio Handler
==================================================
Twilio client initialized successfully
Configured to send from +15551234567 to +15559876543

⚠️  This will send a real SMS to your configured number!
Recipient: +15559876543

Proceed with sending test message? (yes/no):
```

**Type `yes` to continue**

```
Sending test message...
Message sent successfully. SID: SM1234567890abcdef
✅ Test message sent successfully!
Check your phone (+15559876543) for the message.
```

**Check your phone** - you should receive:
```
This is a test message from your Health Management System! 💙
```

**If it fails:**

**Error: "Unable to create record"**
- With error code 21608: Verify the phone number is formatted correctly
  - Must include country code: `+15551234567`
  - No spaces, dashes, or parentheses
- With error code 21211: You're using a trial account and need to verify the recipient number:
  1. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/verified
  2. Click "Add a new number"
  3. Verify your personal phone number

**Error: "Authentication failed"**
- Verify TWILIO_ACCOUNT_SID starts with "AC"
- Verify TWILIO_AUTH_TOKEN is correct
- Check for extra spaces in .env file
- Try regenerating the auth token in Twilio console

**No error but message not received:**
- Check Twilio logs: https://console.twilio.com/us1/monitor/logs/sms
- Verify the recipient phone number
- Check if message is in your phone's spam folder
- If using trial account, make sure recipient is verified

---

## Test 5: Scheduler

**What this tests:** Automated check-in scheduling.

```bash
python3 modules/scheduler.py
```

**Expected output:**
```
Testing Check-In Scheduler
==================================================
Scheduler initialized with timezone: America/New_York

Setting up check-in schedule...
✅ Scheduled daily check-in at 08:00 (America/New_York)
✅ Scheduled daily check-in at 20:00 (America/New_York)

Starting scheduler...
✅ Scheduler started successfully
Scheduled jobs: 2
  - Daily Check-in at 08:00 (next run: 2024-01-16 08:00:00 EST)
  - Daily Check-in at 20:00 (next run: 2024-01-15 20:00:00 EST)

Next scheduled check-ins:
  Daily Check-in at 08:00: 2024-01-16 08:00:00 EST
  Daily Check-in at 20:00: 2024-01-15 20:00:00 EST

Scheduler is now running. Press Ctrl+C to stop.
```

**Verify:**
- Next run times are in the future
- Times are in your configured timezone
- Both check-ins are scheduled

**To test manual check-in (sends real SMS):**

Edit the file to uncomment this line near the bottom:
```python
success = scheduler.trigger_manual_check_in()
```

Then run again. You should receive the check-in message immediately.

**If it fails:**

**Error: "Timezone not found"**
- Check TIMEZONE in .env
- Use a valid timezone from: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

**Next run times are wrong:**
- Verify your system clock is correct
- Check the timezone setting

---

## Test 6: Full Application

**What this tests:** The complete integrated system.

### 6.1 Start the Application

```bash
python3 app.py
```

**Expected output:**
```
Validating configuration...
✅ Configuration validated successfully!
Initializing application modules...
Twilio client initialized successfully
Claude API client initialized
Google Sheets connection established successfully
✅ All modules initialized successfully
Setting up automated check-in schedule...
✅ Scheduled daily check-in at 08:00 (America/New_York)
✅ Scheduled daily check-in at 20:00 (America/New_York)
✅ Scheduler started successfully
============================================================
🏥 Health Management SMS System - Phase 1
============================================================
Environment: production
Timezone: America/New_York
Check-in times: ['08:00', '20:00']
User phone: +15559876543
============================================================
Starting Flask server on port 5000...
 * Serving Flask app 'app'
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

### 6.2 Test Web Interface

**Open in browser:** http://localhost:5000

You should see:
- System status (green "System Running" badge)
- Entry count
- Next scheduled check-ins
- Active features list

**Open health endpoint:** http://localhost:5000/health

Should return JSON:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00",
  "scheduled_jobs": 2,
  "next_check_ins": [...],
  "phase": "Phase 1 - Symptom Tracking",
  "version": "1.0.0"
}
```

### 6.3 Test Webhook Locally with ngrok

See Step 8 in SETUP.md for ngrok setup. Then:

1. **Start ngrok:**
   ```bash
   ngrok http 5000
   ```

2. **Configure Twilio webhook** with the ngrok URL + /sms

3. **Send test message** to your Twilio number:
   ```
   Terrible bloating today, 8/10. Very uncomfortable. Had dairy at lunch.
   ```

4. **Watch the logs** in your app.py terminal:
   ```
   Received incoming SMS webhook
   From: +15559876543
   Message: Terrible bloating today, 8/10...
   Parsing message with Claude API...
   Parsing successful: Severe bloating after dairy
   Logging to Google Sheets...
   ✅ Successfully logged to Google Sheets
   Sending confirmation: Logged! bloating (8/10)...
   ✅ Message processed successfully
   ```

5. **Check your phone** - should receive confirmation:
   ```
   Logged! bloating (8/10). Trigger: dairy. Feel better ❤️
   ```

6. **Check Google Sheet** - should have new row with all data

### 6.4 Test Error Handling

**Send non-health message:**
```
Hey, just testing!
```

Should receive:
```
Got your message! 💙
```

(Won't be logged as a symptom)

**Send from different number:**
- Message should be ignored (security feature)
- Check logs for "Unauthorized message from..."

---

## Debugging Common Issues

### Issue: Messages are logged but no confirmation received

**Check:**
1. Twilio logs: https://console.twilio.com/us1/monitor/logs/sms
2. App logs for errors when sending confirmation
3. Your trial account limits (trial accounts have restrictions)

**Fix:**
- Upgrade from trial account, OR
- Make sure recipient number is verified in Twilio console

### Issue: Confirmation received but not logged to Sheet

**Check:**
1. App logs for Google Sheets errors
2. Service account still has access to sheet
3. Sheet name matches .env configuration

**Fix:**
- Re-share sheet with service account
- Verify sheet name is exact match
- Check that sheets_manager.log_symptom_entry() returns True in logs

### Issue: Scheduled messages not sending

**Check:**
1. Is the app running? (Can't send if app is stopped)
2. Are you in the right timezone?
3. Check logs at the scheduled time

**Fix:**
- Keep app running 24/7 (need to deploy - see DEPLOYMENT.md)
- Verify TIMEZONE in .env
- Check CHECKIN_TIMES format (must be HH:MM)

### Issue: Claude can't parse certain messages

**This is okay!** The system will:
1. Still save the raw message
2. Mark it as "parsed_successfully: false"
3. Send a confirmation acknowledging the message

**You can:**
- Review raw messages in the Google Sheet
- Try different wording in future messages
- Add manual notes to the sheet

---

## Advanced Testing: Load Testing

Want to test with lots of messages?

```python
# Create a test script: test_load.py
from modules.twilio_handler import TwilioHandler
from modules.claude_parser import ClaudeParser
from modules.sheets_manager import SheetsManager

test_messages = [
    "Bloating 7/10, had dairy",
    "Nausea and cramping after dinner",
    "Night sweats again, feeling exhausted",
    "Abdominal pain, 6/10, constipation",
    "Feeling good today! No major symptoms",
]

parser = ClaudeParser()
sheets = SheetsManager()

for msg in test_messages:
    parsed = parser.parse_symptom_description(msg)
    success = sheets.log_symptom_entry(parsed, 'manual')
    print(f"✅ Logged: {msg[:30]}... - Success: {success}")
```

Run with:
```bash
python3 test_load.py
```

Then check your Google Sheet - should have 5 new entries!

---

## Testing Checklist

Before considering Phase 1 complete, verify:

- [x] Configuration validates without errors
- [x] Claude parser successfully parses various symptom descriptions
- [x] Google Sheets logs entries with all columns
- [x] Twilio sends and receives messages
- [x] Scheduler shows correct next run times
- [x] Web interface loads and shows status
- [x] Full workflow: Text → Parse → Log → Confirm
- [x] Error handling: Bad messages don't crash the system
- [x] Security: Unauthorized numbers are rejected
- [x] Google Sheet has proper headers and formatting

---

## Performance Benchmarks

Expected performance for Phase 1:

- **Message processing time:** 2-5 seconds from receive to confirmation sent
- **Claude API response:** 1-3 seconds
- **Google Sheets write:** 0.5-2 seconds
- **Twilio send:** 0.5-1 second

If you're seeing much slower times:
- Check your internet connection
- Verify API keys are correct (wrong keys cause retries)
- Check for rate limiting (shouldn't happen at this scale)

---

## Log Files

The app creates logs in:
- **Console output:** Real-time logs while app is running
- **health_sms_system.log:** Persistent log file

**View recent logs:**
```bash
tail -f health_sms_system.log
```

**Search logs for errors:**
```bash
grep ERROR health_sms_system.log
```

**Clear old logs:**
```bash
# Backup first
cp health_sms_system.log health_sms_system.log.backup

# Clear
> health_sms_system.log
```

---

## Getting Logs from Different Sources

### Twilio Logs
https://console.twilio.com/us1/monitor/logs/sms
- Shows all sent/received messages
- Shows delivery status
- Shows webhook errors

### Claude API Logs
https://console.anthropic.com/settings/logs
- Shows API calls
- Shows token usage
- Shows any errors

### Google Sheets Audit Log
1. Open your sheet
2. File → Version history → See version history
3. Shows all edits with timestamps

---

## What to Do When Everything Works

Once all tests pass:

1. **Leave it running locally for a day** to verify scheduled messages work
2. **Send a few real symptom logs** to build initial data
3. **Review your Google Sheet** to make sure data looks good
4. **Proceed to deployment** (see DEPLOYMENT.md)

---

## What to Do When Things Don't Work

1. **Don't panic!** Most issues are simple configuration mistakes
2. **Read error messages carefully** - they usually tell you exactly what's wrong
3. **Check one thing at a time** - use the individual module tests
4. **Review SETUP.md** - make sure you didn't skip a step
5. **Check service status:**
   - Twilio: https://status.twilio.com
   - Anthropic: https://status.anthropic.com
   - Google: https://status.cloud.google.com

---

## You're Ready!

If all tests pass, your Phase 1 system is fully functional!

**Next steps:**
1. Deploy to a server (DEPLOYMENT.md)
2. Use it daily for a week or two
3. Review what's working and what could be better
4. Move on to Phase 2 when ready!
