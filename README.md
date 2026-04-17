# BBC News AI Podcast 🎙️

Welcome to the **BBC News AI Podcast** project! This is an automated system that fetches the latest news from the BBC RSS feed, uses AI to generate a continuous podcast script, converts the script to lifelike audio using Edge-TTS, and presents the resulting podcasts via a beautiful Streamlit Web Dashboard.

## Features ✨

- **News Fetcher:** Autonomously fetches the newest BBC Technology articles via RSS.
- **AI Script Generation:** Uses OpenRouter API to produce a structured, high-quality script summing up the top 8 articles.
- **Text-to-Speech:** Converts the podcast script into an MP3 audio file using Edge-TTS.
- **Web Dashboard:** A Streamlit-based interface that provides episode listings, short summaries, an audio player, download functionalities, and a Light/Dark theme toggle.
- **Admin Panel:** Built-in admin panel within the dashboard for manually triggering podcast generation, deleting episodes, and viewing system logs.
- **Job Scheduler:** Extensible architecture capable of automatically scheduling pipeline execution on a daily basis.

## Architecture & Tech Stack 🏗️

The project operates through a highly modular pipeline:
1. `scraper.py`: Fetches and parses RSS feed data.
2. `script_gen.py`: Transforms articles into conversational scripts via LLM interfaces.
3. `tts_gen.py`: Synthesizes voice audio and saves as MP3.
4. `database.py`: Stores episode metadata implicitly using SQLite.
5. `web/app.py`: The web frontend for the user listening experience.

**Tech Used:** Python 3.9+, Streamlit, OpenRouter API (OpenAI compatible), Edge-TTS, BeautifulSoup.

## Installation 🚀

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd OpenPodcsat
   ```

2. **Set up a Virtual Environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Linux/MacOS:
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Copy the example environment file and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   *Note: Ensure you include your `OPENROUTER_API_KEY` for AI script generation, and define an `ADMIN_PASSWORD` to secure the Streamlit admin panel.*

## Usage 🎧

### Running the Podcast Builder Pipeline
To manually run the pipeline to fetch news, generate scripts, and create your podcast audio file:
```bash
python main.py
```
This process takes approximately 1-2 minutes to complete and saves the resulting MP3 audio to `audio/episodes/` alongside database entries.

### Starting the Web Player
Once an episode is generated, launch the Streamlit frontend to interact with and listen to your podcasts:
```bash
streamlit run web/app.py
```
The application will automatically open in your browser, typically accessible at `http://localhost:8501`.

## Documentation 📚

Refer to the included markdown specifications for further project design details:
- [Architecture Design](ARCHITECTURE_DESIGN.md)
- [Requirements Specification](REQUIREMENTS_SPECIFICATION.md)
- [Deployment Instructions](DEPLOY.md)