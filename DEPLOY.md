# Deploy to GitHub Pages

This runs automatically when you push to GitHub.

## Setup:

1. Create a new repo on GitHub (e.g., `van2703/bbc-podcast`)
2. Update `.env` with:
   ```
   GITHUB_REPO=van2703/bbc-podcast
   ```
3. Push code to GitHub
4. Go to repo **Settings → Pages**
5. Source: **Deploy from branch**
6. Branch: `main`, folder: `/ (root)`
7. Save

The web app will be live at: `https://van2703.github.io/bbc-podcast`

## For daily auto-push:

Add to `.github/workflows/deploy.yml` (create folder .github/workflows first)