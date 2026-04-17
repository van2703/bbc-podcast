"""
Web Interface - Streamlit app for podcast player.
"""
import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_database
from config.settings import ADMIN_PASSWORD, WEB_PORT

# Page config
st.set_page_config(
    page_title="BBC News Podcast",
    page_icon="🎙️",
    layout="wide"
)

# Session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'


def apply_theme(theme: str):
    """Apply theme CSS."""
    if theme == 'dark':
        st.markdown("""
            <style>
            .stApp { background-color: #1e1e1e; color: #ffffff; }
            .stButton>button { background-color: #4a4a4a; color: white; }
            h1, h2, h3 { color: #ffffff !important; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp { background-color: #ffffff; color: #1e1e1e; }
            </style>
        """, unsafe_allow_html=True)


def toggle_theme():
    """Toggle between light/dark theme."""
    current = st.session_state.theme
    st.session_state.theme = 'dark' if current == 'light' else 'light'
    apply_theme(st.session_state.theme)


def show_home():
    """Show home page with episode list."""
    st.title("🎙️ BBC News Podcast")
    
    # Theme toggle button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🌙" if st.session_state.theme == 'light' else "☀️"):
            toggle_theme()
            st.rerun()

    st.markdown("---")

    # Get episodes from database
    db = get_database()
    episodes = db.get_episodes()

    if not episodes:
        st.info("No episodes yet. Run the pipeline to generate your first podcast!")
        return

    # Episode cards
    for ep in episodes:
        with st.container():
            st.markdown(f"### {ep['title']}")
            
            # Episode info
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.caption(f"🕐 {ep['created_at']}")
            with col2:
                st.caption(f"⏱️ {ep.get('duration', 0) // 60} min")
            with col3:
                if ep['audio_url']:
                    try:
                        audio_path = Path(ep['audio_url'])
                        if audio_path.exists():
                            st.download_button(
                                "⬇️ Download",
                                data=audio_path.read_bytes(),
                                file_name=f"{ep['title']}.mp3",
                                mime="audio/mpeg"
                            )
                    except Exception:
                        pass

            # Summary
            st.write(ep.get('summary', 'No summary available'))

            # Audio player
            if ep.get('audio_url'):
                try:
                    audio_path = Path(ep['audio_url'])
                    if audio_path.exists():
                        st.audio(str(audio_path))
                except:
                    st.caption("Audio file unavailable")

            st.markdown("---")


def show_admin():
    """Admin panel."""
    st.title("🔧 Admin Panel")
    
    # Check password
    if 'admin_auth' not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        password = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Invalid password")
        return

    # Admin features
    st.success("Logged in as admin")

    # Generate button
    if st.button("🎙️ Generate Podcast Now"):
        st.info("Pipeline generation triggered! (This would run main.py)")
        
    st.markdown("---")

    # Episode management
    st.subheader("Episodes")
    db = get_database()
    episodes = db.get_episodes()
    
    for ep in episodes:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{ep['title']} - {ep['created_at']}")
        with col2:
            if st.button(f"Delete", key=f"del_{ep['id']}"):
                db.delete_episode(ep['id'])
                st.success("Deleted!")
                st.rerun()

    st.markdown("---")

    # Logs
    st.subheader("System Logs")
    logs = db.get_logs(50)
    for log in logs:
        color = "🔴" if log['level'] == 'ERROR' else "🟡" if log['level'] == 'WARNING' else "🟢"
        st.caption(f"{color} {log['created_at']} - {log['message']}")


def main():
    """Main app."""
    apply_theme(st.session_state.theme)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Admin"])

    if page == "Home":
        show_home()
    elif page == "Admin":
        show_admin()


if __name__ == "__main__":
    main()