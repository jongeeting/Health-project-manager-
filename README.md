# Health Management SMS System

A comprehensive text-message-based health management system for tracking symptoms, medications, appointments, and coordinating care for chronic health conditions.

## Overview

This system helps manage chronic health conditions (umbilical hernia, suspected endometriosis, PMDD) with ADHD-friendly text-based interactions. It uses SMS as the primary interface, with automated check-ins, natural language processing, and intelligent data tracking.

## Current Status: Phase 1 - Symptom Tracking ✅

### What You Can Do Right Now

**Text naturally, the system understands:**
```
You: "Bad bloating today, 7/10. Had dairy at lunch."
System: "Logged! bloating (7/10). Trigger: dairy. Feel better ❤️"
```

**Get automatic check-ins:**
```
System (8am): "How are you feeling today? 💙"
You: "Night sweats again, feeling exhausted"
System: "Logged! night sweats, low energy. Feel better ❤️"
```

**View all your data in Google Sheets** - easily see patterns, export, analyze

### Completed Features
- ✅ Automated twice-daily symptom check-ins (8am, 8pm)
- ✅ Free-text symptom logging via SMS
- ✅ Claude API integration for natural language parsing
- ✅ Extracts symptoms, severity, triggers, mood/energy
- ✅ Google Sheets data storage with timestamped entries
- ✅ Friendly confirmation messages
- ✅ Manual symptom logging anytime
- ✅ Handles various natural language descriptions

### Upcoming Phases
- **Phase 2:** Medication tracking & refill reminders
- **Phase 3:** Menstrual cycle tracking & correlation
- **Phase 4:** Appointment scheduling & email monitoring
- **Phase 5:** Provider coordination & communication
- **Phase 6:** Reporting & insights
- **Phase 7:** Insurance & admin tracking

See **[PHASES.md](PHASES.md)** for detailed descriptions of each phase.

## Why This System?

Managing chronic health conditions with ADHD can be overwhelming:
- 📝 **Hard to remember** to track symptoms consistently
- 🧠 **Executive dysfunction** makes traditional health apps difficult
- 📊 **Pattern recognition** is impossible without data
- 👨‍⚕️ **Doctor appointments** require synthesizing scattered information
- 💊 **Medication management** requires constant vigilance

**This system solves these problems by:**
- ✅ **Automatic prompts** - you don't have to remember
- ✅ **Text-based** - lowest friction possible (you already text)
- ✅ **Natural language** - no forms, dropdowns, or structured input
- ✅ **Intelligent parsing** - Claude understands how you naturally describe symptoms
- ✅ **Automatic organization** - data structured without you doing extra work
- ✅ **Privacy-first** - your data stays in YOUR Google Sheet

**Built specifically for:**
- People with ADHD and executive function challenges
- Managing multiple chronic conditions simultaneously
- Tracking symptoms across menstrual cycles
- Coordinating care between multiple providers

## 🚀 Quick Start

**New to this project?** Start here: **[QUICKSTART.md](QUICKSTART.md)**

### Setup & Documentation

1. **[QUICKSTART.md](QUICKSTART.md)** - High-level overview and 30-minute setup path
2. **[docs/SETUP.md](docs/SETUP.md)** - Complete step-by-step installation guide
3. **[docs/TESTING.md](docs/TESTING.md)** - Testing procedures and debugging
4. **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deploy to cloud platforms (Render, Railway, Heroku)
5. **[PHASES.md](PHASES.md)** - Roadmap for all 7 phases

### Before You Start

Run the validation script to check your setup:

```bash
python3 validate_setup.py
```

This will verify:
- Python version and dependencies
- Environment variables
- Google Sheets credentials
- Project file structure

## Architecture

```
┌─────────────┐
│   User      │
│  (SMS)      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Twilio API     │
│  (SMS Gateway)  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Flask App      │
│  (Webhook)      │
└──────┬──────────┘
       │
       ├──────────► Claude API (Parse symptoms)
       │
       └──────────► Google Sheets (Store data)
```

## Tech Stack

- **Python 3.9+**: Main application language
- **Flask**: Web framework for Twilio webhooks
- **Twilio**: SMS messaging platform
- **Claude API**: Natural language processing
- **Google Sheets API**: Data storage
- **APScheduler**: Scheduled check-ins
- **python-dotenv**: Environment variable management

## Project Structure

```
health-sms-system/
├── app.py                    # Main application entry point
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variable template
├── modules/
│   ├── __init__.py
│   ├── twilio_handler.py    # Twilio SMS integration
│   ├── claude_parser.py     # Claude API for NLP
│   ├── sheets_manager.py    # Google Sheets integration
│   └── scheduler.py         # Automated check-in scheduler
├── docs/
│   ├── SETUP.md            # Complete setup guide
│   ├── TESTING.md          # Testing procedures
│   └── DEPLOYMENT.md       # Deployment instructions
└── credentials/
    └── google_sheets_credentials.json  # Google API credentials (gitignored)
```

## 💰 Cost Breakdown

**One-time costs:** None (all services have free trials)

**Monthly costs (estimated):**
- Twilio SMS: $1-2/month (free trial covers ~1000 messages)
- Claude API: $1-5/month for typical usage
- Hosting: $0-7/month (Render free tier or $7 paid)
- **Total: ~$2-14/month**

**Free tier options:**
- Use Render.com free tier (with UptimeRobot to keep it awake)
- Twilio trial credits last months for single user
- Google Sheets is free

## 🤔 FAQ

**Q: Do I need to know how to code?**
A: Not really! The setup guide has step-by-step instructions. If you can copy/paste and follow directions, you can set this up.

**Q: Where is my health data stored?**
A: In YOUR Google Sheet. You own and control all your data.

**Q: Can multiple people use this?**
A: Phase 1 is designed for one user. Multi-user support could be added in a future phase.

**Q: What if Claude misunderstands my message?**
A: The raw message is always saved, even if parsing fails. You can review and manually categorize in the Google Sheet.

**Q: Is this HIPAA compliant?**
A: This is a personal tool, not a healthcare provider service, so HIPAA doesn't apply. However, your data is protected: stored in your private Google account, transmitted via HTTPS, and credentials are secured.

**Q: Can I customize the check-in times?**
A: Yes! Just edit the `CHECKIN_TIMES` in your `.env` file (e.g., "07:00,14:00,21:00" for 3 times daily).

**Q: What if I want to stop using it?**
A: Your data remains in your Google Sheet. You can export it anytime and shut down the service with no data loss.

## 🆘 Support & Troubleshooting

For issues or questions:
1. Check **[docs/SETUP.md](docs/SETUP.md)** for configuration issues
2. Check **[docs/TESTING.md](docs/TESTING.md)** for debugging procedures
3. Run `python3 validate_setup.py` to diagnose problems
4. Review error logs in your hosting platform or `health_sms_system.log`

## 🙏 Acknowledgments

Built with:
- [Twilio](https://www.twilio.com) for SMS infrastructure
- [Anthropic's Claude](https://www.anthropic.com) for natural language understanding
- [Google Sheets API](https://developers.google.com/sheets/api) for data storage
- Various open-source Python libraries (see requirements.txt)

## License

This is a personal health management tool. Use and modify as needed for your own health tracking needs.
