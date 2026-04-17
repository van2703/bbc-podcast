# BBC News AI Podcast - Requirements Specification

**Version:** 3.0 (Simplified) | **Date:** April 2026

---

## 1. Project Overview

The BBC News AI Podcast is an automated system that:
- Fetches 8 newest BBC news articles daily at 6:00 AM (UTC+7)
- Uses AI to write a podcast script from the articles
- Uses AI to convert script to audio (MP3)
- Auto-uploads to GitHub Pages
- Provides a web interface with theme toggle and episode info

---

## 2. Functional Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-01 | News Fetcher | Fetch 8 latest articles from BBC Technology RSS feed |
| FR-02 | Content Extractor | Get full article text (not just summaries) |
| FR-03 | AI Script Generator | Transform 8 articles into 5-minute podcast script |
| FR-04 | Text-to-Speech | Convert script text to MP3 audio |
| FR-05 | Storage Manager | Upload MP3 to GitHub Releases |
| FR-06 | Auto Publisher | Deploy to GitHub Pages automatically |
| FR-07 | Daily Scheduler | Run at 6:00 AM UTC+7 every day |

---

## 3. Web Interface Requirements

| ID | Feature | Description |
|----|---------|-------------|
| UI-01 | Theme Toggle | Switch between light/dark mode |
| UI-02 | Episode List | Show all episodes, newest first |
| UI-03 | Episode Info | Display: update time, title, short summary |
| UI-04 | Audio Player | Play episode in browser |
| UI-05 | Download Button | Download MP3 file |

---

## 4. Non-Functional Requirements

- **Performance:** Pipeline completes in < 20 minutes
- **Reliability:** Daily success rate > 95%
- **Cost:** < $10/month
- **Uptime:** Web available 24/7

---

## 5. Technical Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| News Fetch | feedparser, BeautifulSoup |
| AI Script | OpenRouter API |
| AI Voice | Edge-TTS (free) |
| Storage | GitHub Releases |
| Web | Streamlit |
| Scheduler | APScheduler |

---

## 6. Data Flow

```
6:00 AM daily
    │
    ▼
[1. Fetch BBC RSS] → 8 articles
    │
    ▼
[2. AI Script Gen] → podcast script
    │
    ▼
[3. AI TTS] → MP3 audio
    │
    ▼
[4. Upload GitHub] → release asset
    │
    ▼
[5. Deploy Pages] → live website
```

---

## 7. Out of Scope (Phase 1)

- Multiple news sources (BBC only)
- User accounts
- Comments/ratings
- Video podcasts
- Monetization

---

## 8. Success Criteria

- [ ] Podcast runs daily at 6:00 AM
- [ ] 8 articles per episode
- [ ] Audio duration ~5 minutes
- [ ] Web shows: time, title, summary
- [ ] Theme toggle works
- [ ] Cost < $10/month