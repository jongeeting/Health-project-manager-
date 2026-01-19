# Google Sheets Credentials

This directory should contain your Google Sheets API credentials file.

## Setup Instructions

1. Follow Step 4 in [docs/SETUP.md](../docs/SETUP.md) to create a Google Cloud service account
2. Download the JSON credentials file
3. Place it in this directory and name it: `google_sheets_credentials.json`

## Security

⚠️ **IMPORTANT:** This file contains sensitive credentials!

- Never commit this file to git (it's already in .gitignore)
- Never share this file publicly
- Keep it secure and backed up safely offline

## File Location

Expected file path:
```
credentials/google_sheets_credentials.json
```

This path is configured in your `.env` file as `GOOGLE_CREDENTIALS_PATH`.

## Production Deployment

For deployment to cloud platforms (Render, Railway, Heroku), you'll use the `GOOGLE_CREDENTIALS_JSON` environment variable instead of this file. See [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md) for details.
