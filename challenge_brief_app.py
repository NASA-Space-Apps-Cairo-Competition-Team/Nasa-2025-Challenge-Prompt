import streamlit as st
import pandas as pd
import time
from io import BytesIO

from LLM_AND_UI.llm import analyze_brief, smart_merge_rows
from LLM_AND_UI.parser import parse_output
from LLM_AND_UI.utils import get_latest_challenge_excel, run_scraper

st.set_page_config(page_title="NASA Brief Tagger", layout="wide")
st.title("🚀 NASA Space Apps - Challenge Brief Analyzer")

st.markdown("""
Welcome! This tool helps you collect, analyze, and organize NASA Space Apps Challenge briefs.  
You can **scrape**, **upload**, or **manually enter** challenges, and we'll extract structured insights using AI.
""")

# --- Scrape Section ---
st.header("🌐 Scrape NASA Challenges")
st.markdown("Use this section to **automatically collect challenges** from the official NASA Space Apps site.")

url = st.text_input("Enter NASA Challenges Page URL", help="Paste the official NASA challenge list URL here.")

if st.button("🔍 Scrape"):
    with st.spinner("Scraping the challenge data from the website..."):
        result = run_scraper(url)
        if result.returncode == 0:
            file = get_latest_challenge_excel()
            if file:
                st.success(f"Scraped and loaded: {file}")
                st.session_state.uploaded_file = open(file, "rb")
            else:
                st.error("Scrape finished, but no Excel file was found.")
        else:
            st.error(result.stderr)

# --- Upload Excel Section ---
st.header("📤 Upload an Existing Excel File")
st.markdown("If you already have a file from previous scraping or manual creation, upload it here.")

file = st.file_uploader("Upload a `.xlsx` file", type=["xlsx"], help="The Excel file should contain at least 'Title' and 'Brief' columns.")
if file:
    st.session_state.uploaded_file = file

# --- Analyze Uploaded/Scraped File ---
if "uploaded_file" in st.session_state and st.session_state.uploaded_file:
    df = pd.read_excel(st.session_state.uploaded_file, sheet_name="Challenge Details")
    if "Brief" not in df.columns or "Title" not in df.columns:
        st.error("Uploaded file must contain both 'Title' and 'Brief' columns.")
    else:
        st.header("🧠 AI Analysis of Uploaded Challenges")
        st.markdown("This will process the uploaded data and extract structured tags and information using AI.")

        if "analyzed_df" not in st.session_state:
            with st.spinner("Analyzing briefs... please wait."):
                results = []
                for _, row in df.iterrows():
                    output = analyze_brief(row)
                    parsed = parse_output(output)
                    parsed["Title"] = row["Title"]
                    results.append(parsed)
                    time.sleep(1)
                st.session_state.analyzed_df = pd.DataFrame(results)
        st.success("Challenges successfully analyzed!")
        st.subheader("🔍 Preview of Analyzed Data")
        st.dataframe(st.session_state.analyzed_df.head(10))

# --- Manual Fix/Entry Section ---
if "analyzed_df" in st.session_state:
    st.header("🛠️ Add or Fix a Challenge Entry")
    st.markdown("Use this to **correct mistakes** or **add new challenges** if scraping or uploading didn't cover them.")

    title_input = st.text_input("Challenge Title", help="Title of the new or existing challenge.")
    brief_input = st.text_area("Challenge Brief", height=300, help="Full description of the challenge.")

    if st.button("➕ Add/Update Challenge"):
        if not title_input.strip() or not brief_input.strip():
            st.warning("Both title and brief are required.")
        else:
            new_row = {"Title": title_input.strip(), "Brief": brief_input.strip()}
            llm_result = analyze_brief(new_row)
            parsed_new = parse_output(llm_result)
            parsed_new["Title"] = title_input.strip()

            existing_df = st.session_state.analyzed_df
            match = existing_df[existing_df["Title"].str.lower() == title_input.strip().lower()]

            if not match.empty:
                st.subheader("🔍 Challenge Already Exists - Review Differences")
                old_row = match.iloc[0].to_dict()
                new_merged = smart_merge_rows(old_row, parsed_new)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("#### Existing Entry")
                    st.json(old_row)
                with col2:
                    st.markdown("#### New Analysis")
                    st.json(parsed_new)
                with col3:
                    st.markdown("#### Merged Result")
                    st.json(new_merged)

                if st.button("✅ Confirm Merge"):
                    existing_df.loc[match.index[0]] = new_merged
                    st.success("Challenge successfully updated.")
            else:
                st.session_state.analyzed_df = pd.concat(
                    [existing_df, pd.DataFrame([parsed_new])], ignore_index=True
                )
                st.success("New challenge added successfully.")

# --- Manual Entry from Scratch ---
st.header("✍️ Start from Scratch - Manual Entry")
st.markdown("No Excel? No scrape? Just enter challenges manually below.")

if "manual_df" not in st.session_state:
    st.session_state.manual_df = pd.DataFrame()

manual_title = st.text_input("📝 Manual Title", key="manual_title", help="Enter the challenge title.")
manual_brief = st.text_area("🧾 Manual Brief", height=250, key="manual_brief", help="Full challenge brief description.")

if st.button("➕ Analyze and Add Manually"):
    if not manual_title.strip() or not manual_brief.strip():
        st.warning("Please enter both title and brief.")
    else:
        manual_input = {"Title": manual_title.strip(), "Brief": manual_brief.strip()}
        result = analyze_brief(manual_input)
        parsed_manual = parse_output(result)
        parsed_manual["Title"] = manual_title.strip()

        existing_manual_df = st.session_state.manual_df
        match_manual = existing_manual_df[existing_manual_df["Title"].str.lower() == manual_title.strip().lower()]

        if not match_manual.empty:
            st.subheader("⚠️ Duplicate Detected - Review Merge")
            old_row = match_manual.iloc[0].to_dict()
            merged = smart_merge_rows(old_row, parsed_manual)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("#### Existing")
                st.json(old_row)
            with col2:
                st.markdown("#### New")
                st.json(parsed_manual)
            with col3:
                st.markdown("#### Merged")
                st.json(merged)

            if st.button("✅ Confirm Manual Merge"):
                existing_manual_df.loc[match_manual.index[0]] = merged
                st.success("Manually merged and saved.")
        else:
            st.session_state.manual_df = pd.concat(
                [existing_manual_df, pd.DataFrame([parsed_manual])], ignore_index=True
            )
            st.success("Manually added challenge.")

# --- Final Download Section ---
final_df = None
if "analyzed_df" in st.session_state and not st.session_state.analyzed_df.empty:
    final_df = st.session_state.analyzed_df

if "manual_df" in st.session_state and not st.session_state.manual_df.empty:
    if final_df is not None:
        final_df = pd.concat([final_df, st.session_state.manual_df], ignore_index=True)
    else:
        final_df = st.session_state.manual_df

st.header("📥 Export Analyzed Challenges")
st.markdown("Click the button below to **download all AI-tagged challenges** as one Excel file.")

if final_df is not None:
    out = BytesIO()
    final_df.to_excel(out, index=False)
    out.seek(0)
    st.download_button("📁 Download Final Dataset", out, "final_tagged_challenges.xlsx")
else:
    st.info("No data yet! Scrape, upload, or add manually to enable exporting.")
