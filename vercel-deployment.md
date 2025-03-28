# Vercel Deployment Instructions

The project is configured to deploy on Vercel. The simplest way to deploy is through the Vercel web interface:

1. Go to https://vercel.com/new
2. Import your GitHub repository (data-room-prompt-generator)
3. Configure the project:
   - Build Command: Leave empty
   - Output Directory: Leave empty (.)
   - Root Directory: Leave empty (/)
   - Framework Preset: Select "Other"

4. Add environment variables if needed (ANTHROPIC_API_KEY)

5. Click Deploy

## What this deploys

The deployment uses the serverless Flask app in `api/index.py`. Vercel will:
1. Install dependencies from requirements.txt
2. Set up a serverless function for the Flask app
3. Route all traffic to this function through the configuration in vercel.json

## Troubleshooting

If you encounter "The projectSettings object is required" error using the CLI:
- Deploy through the Vercel web interface instead
- Log in to the Vercel dashboard, link your GitHub repository, and set up the project there

The Flask app includes fallback mechanisms and error reporting to help diagnose issues.