import streamlit as st
from LLM_AND_UI.UI.scrape_tab import render_scrape_tab
from LLM_AND_UI.UI.upload_tab import render_upload_tab
from LLM_AND_UI.UI.manual_tab import render_manual_tab
from LLM_AND_UI.state import init_session_state,freeze_ui_for_others, unlock_ui

st.set_page_config(page_title="NASA Brief Tagger", page_icon="nasa_logo.png", layout="wide")
st.title("🚀 NASA Space Apps - Challenge Brief Analyzer")

st.markdown("""
Welcome! This tool helps you collect, analyze, and organize NASA Space Apps Challenge briefs.  
Each section (Scrape, Upload, Manual) is separate with its own dataset and export options.
""")

# Init state
init_session_state()

# Tabs
tabs = st.tabs(["🌐 Scrape", "📤 Upload", "✍️ Manual Entry"])

# Render tabs
with tabs[0]:
    render_scrape_tab()
with tabs[1]:
    render_upload_tab()
with tabs[2]:
    render_manual_tab()