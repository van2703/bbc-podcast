# Adding GitHub Secrets

Since we cannot set secrets automatically, please add them manually:

## Step 1: Go to Secrets
https://github.com/van2703/bbc-podcast/settings/secrets/actions

## Step 2: Add each secret

Click **"New repository secret"** and add:

| Name | Secret |
|------|--------|
| OPENROUTER_API_KEY | `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` |
| GITHUB_TOKEN | `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` |
| GITHUB_REPO | `van2703/bbc-podcast` |

## Step 3: Run workflow
Go to https://github.com/van2703/bbc-podcast/actions/workflows/daily.yml
Click "Run workflow" → "Run workflow"

The workflow will:
1. Fetch 8 BBC news articles
2. Generate podcast script with AI
3. Convert to audio
4. Save to database (stored in repo)
5. Auto-commit new episodes