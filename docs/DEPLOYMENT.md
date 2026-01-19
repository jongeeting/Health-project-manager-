# Deployment Guide
# Health Management SMS System - Phase 1

This guide covers deploying your health management system to run 24/7 in the cloud.

We'll cover three platforms:
1. **Render.com** (Recommended - Free tier, easiest setup)
2. **Railway.app** (Alternative - Good free trial)
3. **Heroku** (Classic option - $5/month minimum)

---

## Why Deploy to the Cloud?

Your local computer:
- Can't run 24/7 (you turn it off, it sleeps, etc.)
- Isn't always connected to the internet
- Can't receive webhooks when offline

A cloud server:
- Runs continuously
- Always accessible for Twilio webhooks
- Automatically restarts if it crashes
- Provides HTTPS (required for Twilio webhooks)

---

## Pre-Deployment Checklist

Before deploying to any platform:

- [x] All local tests pass (see TESTING.md)
- [x] You have a Twilio account with a phone number
- [x] You have Claude API key with credits
- [x] You have Google Sheets set up and shared
- [x] You have a GitHub account (for easy deployment)
- [x] Your code is in a git repository

---

## Option 1: Render.com (Recommended)

**Pros:**
- Free tier (750 hours/month - effectively 24/7 for one app)
- Easy setup
- Automatic deploys from GitHub
- Good for beginners

**Cons:**
- Free tier apps "spin down" after 15 minutes of inactivity
- Cold start takes ~30 seconds (not ideal but manageable)

### Step 1.1: Push Code to GitHub

```bash
# If you haven't already initialized git:
git init
git add .
git commit -m "Initial commit - Phase 1 complete"

# Create a new repository on GitHub (via website)
# Then connect it:
git remote add origin https://github.com/YOUR-USERNAME/health-sms-system.git
git branch -M main
git push -u origin main
```

### Step 1.2: Create Render Account

1. Go to https://render.com
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### Step 1.3: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name:** health-sms-system
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free

### Step 1.4: Add Environment Variables

In Render dashboard, go to "Environment" tab and add each variable from your .env file:

```
TWILIO_ACCOUNT_SID=your_value
TWILIO_AUTH_TOKEN=your_value
TWILIO_PHONE_NUMBER=your_value
USER_PHONE_NUMBER=your_value
ANTHROPIC_API_KEY=your_value
GOOGLE_SHEET_NAME=Health Tracking Data
GOOGLE_CREDENTIALS_PATH=credentials/google_sheets_credentials.json
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_secret_key
CHECKIN_TIMES=08:00,20:00
TIMEZONE=America/New_York
LOG_LEVEL=INFO
PORT=10000
```

**Important:** For PORT, use `10000` (Render's default).

### Step 1.5: Upload Google Credentials

Unfortunately, Render doesn't have a simple file upload for credentials. Options:

**Option A: Use environment variable (easier)**

1. Open your `google_sheets_credentials.json`
2. Copy the entire contents (it's one line of JSON)
3. In Render, add new environment variable:
   - **Key:** GOOGLE_CREDENTIALS_JSON
   - **Value:** (paste the entire JSON)

4. Update `config.py` to handle this:

```python
# Add this to config.py, in the Config class:
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')

# And update sheets_manager.py to use it:
# In modules/sheets_manager.py, replace the credentials loading:

if Config.GOOGLE_CREDENTIALS_JSON:
    # Load from environment variable
    import json
    import tempfile
    creds_dict = json.loads(Config.GOOGLE_CREDENTIALS_JSON)
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(creds_dict, f)
        temp_creds_path = f.name
    creds = ServiceAccountCredentials.from_json_keyfile_name(temp_creds_path, scope)
else:
    # Load from file (local development)
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        Config.GOOGLE_CREDENTIALS_PATH,
        scope
    )
```

**Option B: Use Render disk (advanced)**

See Render's documentation on persistent disks.

### Step 1.6: Deploy

1. Click **"Create Web Service"**
2. Render will automatically build and deploy
3. Watch the logs for any errors
4. Once deployed, you'll get a URL like: `https://health-sms-system.onrender.com`

### Step 1.7: Configure Twilio Webhook

1. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click your phone number
3. Under "Messaging Configuration" → "A message comes in":
   - URL: `https://health-sms-system.onrender.com/sms`
   - Method: POST
4. Click **Save**

### Step 1.8: Test

Send a text to your Twilio number:
```
Testing from Render! Feeling bloated, 6/10.
```

You should:
- Receive a confirmation SMS
- See it logged in Google Sheets
- See logs in Render dashboard

### Step 1.9: Keep Alive (Prevent Sleep)

Free Render apps sleep after 15 minutes of no activity. Options:

**Option A: Upgrade to paid tier** ($7/month for always-on)

**Option B: Use a keep-alive service** (free)
- Use https://uptimerobot.com
- Monitor your `/health` endpoint every 5 minutes
- Free tier allows 50 monitors

Set up UptimeRobot:
1. Create account at https://uptimerobot.com
2. Add new monitor
3. Monitor Type: HTTPS
4. URL: `https://health-sms-system.onrender.com/health`
5. Monitoring Interval: 5 minutes

This will ping your app regularly, keeping it awake.

**Note:** Even with sleep, the app will wake up when Twilio sends a webhook (takes ~30 seconds for first message after sleep).

---

## Option 2: Railway.app

**Pros:**
- $5 free trial credit (good for ~1 month)
- No sleep/wake cycle
- Very easy setup
- Great for testing

**Cons:**
- Free trial expires (need to pay $5/month after)
- More expensive than Render for long-term

### Step 2.1: Push to GitHub

(Same as Render Step 1.1)

### Step 2.2: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub
3. You'll get $5 in free trial credits

### Step 2.3: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your health-sms-system repository

### Step 2.4: Configure

Railway auto-detects Python. No build commands needed!

1. Go to **Settings** tab
2. Add environment variables (same as Render)
3. For Google credentials:
   - Use the GOOGLE_CREDENTIALS_JSON environment variable approach
   - Or use Railway Volumes (see their docs)

### Step 2.5: Deploy

- Railway automatically deploys
- You'll get a URL like: `https://health-sms-system-production.up.railway.app`

### Step 2.6: Configure Twilio

Same as Render, but use your Railway URL.

---

## Option 3: Heroku (Classic)

**Pros:**
- Very reliable
- Excellent documentation
- No sleep on paid tier

**Cons:**
- No free tier (minimum $5/month for eco dynos)
- More complex setup

### Step 3.1: Install Heroku CLI

```bash
# Mac:
brew tap heroku/brew && brew install heroku

# Windows:
# Download from https://devcenter.heroku.com/articles/heroku-cli

# Linux:
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 3.2: Login

```bash
heroku login
```

### Step 3.3: Create Heroku App

```bash
cd /path/to/health-sms-system
heroku create health-sms-system-yourusername
```

### Step 3.4: Add Buildpack

```bash
heroku buildpacks:set heroku/python
```

### Step 3.5: Set Environment Variables

```bash
# Set each variable:
heroku config:set TWILIO_ACCOUNT_SID=your_value
heroku config:set TWILIO_AUTH_TOKEN=your_value
heroku config:set TWILIO_PHONE_NUMBER=your_value
heroku config:set USER_PHONE_NUMBER=your_value
heroku config:set ANTHROPIC_API_KEY=your_value
heroku config:set GOOGLE_SHEET_NAME="Health Tracking Data"
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your_secret_key
heroku config:set CHECKIN_TIMES=08:00,20:00
heroku config:set TIMEZONE=America/New_York

# For Google credentials:
heroku config:set GOOGLE_CREDENTIALS_JSON="$(cat credentials/google_sheets_credentials.json)"
```

### Step 3.6: Create Procfile

```bash
# Create Procfile in project root:
echo "web: gunicorn app:app" > Procfile
```

### Step 3.7: Deploy

```bash
git add Procfile
git commit -m "Add Procfile for Heroku"
git push heroku main
```

### Step 3.8: Scale Up

```bash
# Start one web dyno (eco tier - $5/month)
heroku ps:scale web=1
```

### Step 3.9: View Logs

```bash
heroku logs --tail
```

### Step 3.10: Configure Twilio

Use your Heroku URL: `https://health-sms-system-yourusername.herokuapp.com/sms`

---

## Post-Deployment Configuration

### Update Your Code to Handle JSON Credentials

If using the GOOGLE_CREDENTIALS_JSON environment variable approach, update `sheets_manager.py`:

```python
# In modules/sheets_manager.py, update __init__ method:

def __init__(self):
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive'
        ]

        # Check if credentials are in environment variable (production)
        if Config.GOOGLE_CREDENTIALS_JSON:
            logger.info("Loading Google credentials from environment variable")
            import json
            creds_dict = json.loads(Config.GOOGLE_CREDENTIALS_JSON)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # Load from file (local development)
            logger.info(f"Loading Google credentials from file: {Config.GOOGLE_CREDENTIALS_PATH}")
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                Config.GOOGLE_CREDENTIALS_PATH,
                scope
            )

        self.client = gspread.authorize(creds)
        # ... rest of the code
```

And update `config.py`:

```python
# Add to Config class:
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')
```

Commit and push:

```bash
git add modules/sheets_manager.py config.py
git commit -m "Support Google credentials from environment variable"
git push origin main  # Triggers auto-deploy on Render/Railway
# OR
git push heroku main  # For Heroku
```

---

## Testing Your Deployment

### Test 1: Health Check

```bash
curl https://your-app-url.com/health
```

Should return JSON with status "healthy".

### Test 2: View Web Interface

Open `https://your-app-url.com` in a browser.

Should see the system status page.

### Test 3: Send Test SMS

Text your Twilio number:
```
Deployed! Testing bloating 5/10.
```

Should receive confirmation and see data in Google Sheets.

### Test 4: Check Scheduled Messages

Wait for your next scheduled check-in time (or set CHECKIN_TIMES to a time a few minutes from now).

You should receive the check-in message automatically.

---

## Monitoring Your Deployment

### Check Logs

**Render:**
- Dashboard → Logs tab

**Railway:**
- Project → Deployments → View Logs

**Heroku:**
```bash
heroku logs --tail
```

### Set Up Alerts

**Render:**
- Doesn't have built-in alerts on free tier
- Use UptimeRobot (see above)

**Railway:**
- Has built-in monitoring

**Heroku:**
- Add Papertrail (log monitoring):
  ```bash
  heroku addons:create papertrail
  ```

### Monitor Costs

**Check API usage:**
- Twilio: https://console.twilio.com/us1/monitor/usage
- Claude: https://console.anthropic.com/settings/billing
- Google Cloud: https://console.cloud.google.com/billing

**Expected monthly costs:**
- Twilio: $1-2 (trial credits cover more)
- Claude API: $1-5
- Hosting: $0-7 (depending on platform)
- **Total: ~$2-14/month**

---

## Troubleshooting Deployment Issues

### App crashes immediately after deploy

**Check logs for:**
- Missing environment variables
- Module import errors
- Invalid Google credentials

**Fix:**
- Review all environment variables are set
- Make sure requirements.txt has all dependencies
- Verify Google credentials JSON is valid

### Webhooks not working

**Check:**
1. Twilio webhook URL is correct and uses HTTPS
2. URL includes `/sms` at the end
3. Method is set to POST
4. App is running (check logs)

**Test webhook directly:**
```bash
curl -X POST https://your-app-url.com/sms \
  -d "From=+15559876543" \
  -d "Body=Test message"
```

### Scheduled messages not sending

**Check:**
1. Timezone is correct in environment variables
2. App hasn't crashed (check logs around scheduled time)
3. Scheduler started successfully (check startup logs)

**Verify scheduler is running:**

Add this endpoint to `app.py` for debugging:

```python
@app.route('/scheduler-status', methods=['GET'])
def scheduler_status():
    jobs = scheduler.get_next_check_in_times()
    return {
        'jobs': jobs,
        'scheduler_running': scheduler.scheduler.running
    }
```

### Google Sheets authentication failing

**If using GOOGLE_CREDENTIALS_JSON:**
1. Verify the JSON is valid (paste into jsonlint.com)
2. Check for escaped quotes or formatting issues
3. Make sure the entire JSON is on one line

**If error persists:**
- Re-download credentials JSON from Google Cloud Console
- Double-check service account has Editor role
- Verify sheet is shared with service account email

### High latency / slow responses

**On Render free tier:**
- Expected if app was sleeping (30s wake time)
- Use UptimeRobot to keep alive
- Or upgrade to paid tier

**On other platforms:**
- Check API response times in logs
- Verify network connectivity
- Check if APIs (Claude, Twilio) are experiencing outages

---

## Security Best Practices for Production

1. **Use HTTPS everywhere** (automatic on Render/Railway/Heroku)

2. **Protect your environment variables:**
   - Never commit .env to git
   - Use platform's secret management
   - Rotate keys if compromised

3. **Enable Twilio request validation** (optional but recommended):

Add to `app.py`:

```python
from twilio.request_validator import RequestValidator

@app.route('/sms', methods=['POST'])
def receive_sms():
    # Validate request is from Twilio
    validator = RequestValidator(Config.TWILIO_AUTH_TOKEN)
    url = request.url
    signature = request.headers.get('X-Twilio-Signature', '')

    if not validator.validate(url, request.form, signature):
        logger.warning("Invalid Twilio signature")
        return '', 403

    # ... rest of code
```

4. **Monitor your costs:**
   - Set up billing alerts in each service
   - Claude: Set usage limits in console
   - Twilio: Set budget alerts

5. **Back up your data regularly:**
   - Google Sheets is already backed up by Google
   - Download exports monthly as extra backup
   - Save credential files securely offline

---

## Scaling Considerations

Current Phase 1 setup handles:
- 2 scheduled messages/day
- Unlimited incoming messages (within API limits)
- 1 user

For future phases:
- Multiple users: Add user management to database
- Higher message volume: Consider upgrading hosting tier
- More complex parsing: May need Claude API rate limit increases

---

## Maintenance Tasks

### Weekly
- Check logs for errors
- Verify scheduled messages are sending
- Review Google Sheet data

### Monthly
- Check API costs and usage
- Review and clear old logs
- Backup Google Sheet data
- Update dependencies if needed:
  ```bash
  pip list --outdated
  ```

### As Needed
- Rotate API keys (every 3-6 months)
- Update check-in times if schedule changes
- Add new symptoms to tracking as needed

---

## Rolling Back / Redeploying

### Render/Railway (GitHub integration)
```bash
# Fix issue in code
git add .
git commit -m "Fix issue"
git push origin main
# Auto-deploys automatically
```

### Heroku
```bash
# Rollback to previous version
heroku rollback

# Or deploy new fix
git add .
git commit -m "Fix issue"
git push heroku main
```

---

## When Something Goes Wrong

**App is down:**
1. Check platform status page
2. Check logs for crash reason
3. Verify environment variables are set
4. Try manual restart (platform dashboard)

**Messages not being received:**
1. Check Twilio status: https://status.twilio.com
2. Verify webhook URL is correct
3. Check app is running
4. Review Twilio error logs

**Scheduled messages stopped:**
1. Check if app crashed around that time
2. Verify timezone settings
3. Check scheduler logs
4. Manually trigger one to test: visit `/scheduler-status`

**Can't fix it quickly:**
1. Send manual text responses in the meantime
2. Log symptoms directly in Google Sheet
3. Fix at your own pace - health data is safe in the sheet

---

## Success Criteria

Your deployment is successful when:

- [x] App is accessible via HTTPS URL
- [x] Health endpoint returns "healthy"
- [x] Can send SMS and receive confirmation
- [x] Data appears in Google Sheets
- [x] Scheduled messages send at correct times
- [x] App stays running 24/7
- [x] Logs are accessible and readable

---

## Next Steps After Deployment

1. **Use it daily for 1-2 weeks** to validate it meets your needs
2. **Review your Google Sheet** regularly
3. **Adjust check-in times** if needed
4. **Add notes** about what's working and what you'd like to improve
5. **When ready:** Move on to **Phase 2: Medication Tracking**!

---

## Cost Summary

**Free tier options:**
- Render (with sleep): $0/month + $1-5 Claude API
- Railway trial: $0 for first month

**Recommended paid setup:**
- Render ($7/month) or Heroku ($5/month)
- Claude API: ~$1-5/month
- Twilio: ~$1-2/month (after trial credits)
- **Total: ~$7-14/month**

**Cost-saving tips:**
- Render free tier + UptimeRobot = $0 hosting
- Twilio trial credits last a long time for 1 user
- Claude Sonnet is cost-effective for this use case

---

## You're Deployed! 🚀

Congratulations! Your health management system is now running in the cloud, accessible 24/7, and ready to help you track your health consistently.

Remember:
- Check it daily for the first week
- Review logs weekly
- Keep your credentials secure
- Back up your data monthly

When you're comfortable with Phase 1, see the main README for what's coming in future phases!
