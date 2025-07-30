import streamlit as st
import pandas as pd
import time
from io import BytesIO

from LLM_AND_UI.llm import analyze_brief
from LLM_AND_UI.parser import parse_output
from LLM_AND_UI.utils import get_latest_challenge_excel, run_scraper

st.set_page_config(page_title="NASA Brief Tagger", page_icon="nasa_logo.png", layout="wide")
st.title("🚀 NASA Space Apps - Challenge Brief Analyzer")

st.markdown("""
Welcome! This tool helps you collect, analyze, and organize NASA Space Apps Challenge briefs.  
Each section (Scrape, Upload, Manual) is separate with its own dataset and export options.
""")

# --------------------------
# Initialize session state
# --------------------------
default_keys = {
    "scrape_df": pd.DataFrame(),
    "upload_df": pd.DataFrame(),
    "manual_df": pd.DataFrame(),
    "active_section": None
}
for key, val in default_keys.items():
    if key not in st.session_state:
        st.session_state[key] = val


def freeze_ui_for_others(current_section):
    if st.session_state.active_section is not None and st.session_state.active_section != current_section:
        st.warning(f"🔒 '{st.session_state.active_section}' section is currently processing. Please wait.")
        st.stop()


def unlock_ui():
    st.session_state.active_section = None


tabs = st.tabs(["🌐 Scrape", "📤 Upload", "✍️ Manual Entry"])

# =====================================
# 🌐 SCRAPE TAB
# =====================================
with tabs[0]:
    SECTION = "Scrape"
    freeze_ui_for_others(SECTION)
    st.header("🌐 Scrape NASA Challenges")

    url = st.text_input("Enter NASA Challenge Page URL")

    if st.button("🔍 Scrape Now"):
        st.session_state.active_section = SECTION
        with st.spinner("Scraping and analyzing..."):
            result = run_scraper(url)
            if result.returncode == 0:
                file = get_latest_challenge_excel()
                if file:
                    st.session_state["scraped_excel_file"] = file
                    st.success("Scraping complete! Preview and analyze below.")
                else:
                    st.error("Excel not found.")
            else:
                st.error(result.stderr)
        unlock_ui()

    # =====================================
    # Preview Excel File and Analyze if requested
    # =====================================
    if "scraped_excel_file" in st.session_state:
        file = st.session_state["scraped_excel_file"]

        excel_data = pd.ExcelFile(file)
        sheet_names = excel_data.sheet_names

        selected_sheet = st.selectbox("📄 Select sheet to preview", sheet_names)

        try:
            df = excel_data.parse(selected_sheet)
            df.columns = df.columns.astype(str).str.strip()

            st.subheader("📄 Raw Excel Preview (Before AI Processing)")
            st.dataframe(df)

            if st.button("🤖 Analyze Previewed Sheet with AI"):
                st.session_state.active_section = SECTION
                with st.spinner("Analyzing..."):
                    if "Title" in df.columns:
                        parsed = []
                        for _, row in df.iterrows():
                            out = analyze_brief(row)
                            result = parse_output(out)
                            result["Title"] = row["Title"]
                            parsed.append(result)
                            time.sleep(1)
                        st.session_state.scrape_df = pd.DataFrame(parsed)
                        st.success("Analysis complete!")
                    else:
                        st.error("Missing 'Title' column in scraped data.")
                unlock_ui()
        except Exception as e:
            st.error(f"Failed to load sheet: {e}")

    # =====================================
    # Show Analyzed Data
    # =====================================
    if not st.session_state.scrape_df.empty:
        st.subheader("🧾 Scraped Dataset Preview")
        st.dataframe(st.session_state.scrape_df)

        st.subheader("✏️ Add or Replace Challenge in Scraped Data")
        title_input = st.text_input("Title", key="scrape_title_input")
        brief_input = st.text_area("Brief", height=200, key="scrape_brief_input")

        if st.button("➕ Add/Replace in Scraped Data"):
            if not title_input.strip() or not brief_input.strip():
                st.warning("Both title and brief are required.")
            else:
                st.session_state.active_section = SECTION
                with st.spinner("Analyzing new entry..."):
                    row = {"Title": title_input.strip(), "Brief": brief_input.strip()}
                    out = analyze_brief(row)
                    parsed = parse_output(out)
                    parsed["Title"] = title_input.strip()

                    df = st.session_state.scrape_df.copy()
                    df["Title"] = df["Title"].astype(str)

                    idx = df[df["Title"].str.lower() == title_input.strip().lower()].index
                    if not idx.empty:
                        df.loc[idx[0]] = parsed
                    else:
                        df = pd.concat([df, pd.DataFrame([parsed])], ignore_index=True)

                    st.session_state.scrape_df = df
                    st.success("Challenge added or replaced.")
                unlock_ui()

        out = BytesIO()
        st.session_state.scrape_df.to_excel(out, index=False, sheet_name="Scraped")
        out.seek(0)
        st.download_button("📁 Download Scraped Data", out, "scraped_challenges.xlsx")

# =====================================
# 📤 UPLOAD TAB
# =====================================
with tabs[1]:
    SECTION = "Upload"
    st.header("📤 Upload Challenge Excel")

    file = st.file_uploader("Upload `.xlsx` with 'Title' and 'Brief'", type=["xlsx"])
    
    if file:
        # ✅ Do NOT freeze yet (we're just letting user browse sheet)
        excel_data = pd.ExcelFile(file)
        sheet_names = excel_data.sheet_names

        selected_sheet = st.selectbox("📄 Select sheet to preview", sheet_names)

        if selected_sheet:
            df = excel_data.parse(selected_sheet)
            df.columns = df.columns.astype(str).str.strip()
            st.subheader("📄 Raw Excel Preview (Before AI Processing)")
            st.dataframe(df)

            if st.button("🔍 Process Sheet with AI"):
                freeze_ui_for_others(SECTION)
                st.session_state.active_section = SECTION
                with st.spinner("Processing uploaded file..."):
                    if "Title" in df.columns and "Brief" in df.columns:
                        parsed = []
                        for _, row in df.iterrows():
                            out = analyze_brief(row)
                            result = parse_output(out)
                            result["Title"] = row["Title"]
                            parsed.append(result)
                            time.sleep(1)
                        st.session_state.upload_df = pd.DataFrame(parsed)
                        st.success("Upload and analysis complete!")
                    else:
                        st.error("File must include 'Title' and 'Brief'")
                unlock_ui()

    if not st.session_state.upload_df.empty:
        st.subheader("📊 Uploaded Data Preview")
        st.dataframe(st.session_state.upload_df)

        st.subheader("✏️ Add or Replace Challenge in Uploaded Data")
        title_input = st.text_input("Title", key="upload_title_input")
        brief_input = st.text_area("Brief", height=200, key="upload_brief_input")

        if st.button("➕ Add/Replace in Uploaded Data"):
            if not title_input.strip() or not brief_input.strip():
                st.warning("Both title and brief are required.")
            else:
                freeze_ui_for_others(SECTION)
                st.session_state.active_section = SECTION
                with st.spinner("Analyzing new entry..."):
                    row = {"Title": title_input.strip(), "Brief": brief_input.strip()}
                    out = analyze_brief(row)
                    parsed = parse_output(out)
                    parsed["Title"] = title_input.strip()

                    df = st.session_state.upload_df.copy()
                    df["Title"] = df["Title"].astype(str)

                    idx = df[df["Title"].str.lower() == title_input.strip().lower()].index
                    if not idx.empty:
                        df.loc[idx[0]] = parsed
                    else:
                        df = pd.concat([df, pd.DataFrame([parsed])], ignore_index=True)

                    st.session_state.upload_df = df
                    st.success("Challenge added or replaced.")
                unlock_ui()

        out = BytesIO()
        st.session_state.upload_df.to_excel(out, index=False, sheet_name="Uploaded")
        out.seek(0)
        st.download_button("📁 Download Uploaded Data", out, "uploaded_challenges.xlsx")

# =====================================
# ✍️ MANUAL ENTRY TAB
# =====================================
with tabs[2]:
    SECTION = "Manual"
    freeze_ui_for_others(SECTION)
    st.header("✍️ Add a Challenge Manually")

    title = st.text_input("Challenge Title", key="manual_title")
    brief = st.text_area("Challenge Brief", height=250, key="manual_brief")

    if st.button("➕ Analyze and Add Manually"):
        if not title.strip() or not brief.strip():
            st.warning("Both title and brief are required.")
        else:
            st.session_state.active_section = SECTION
            with st.spinner("Analyzing manual entry..."):
                row = {"Title": title.strip(), "Brief": brief.strip()}
                out = analyze_brief(row)
                parsed = parse_output(out)
                parsed["Title"] = title.strip()

                df = st.session_state.manual_df.copy()
                df["Title"] = df.get("Title", pd.Series([], dtype=str)).astype(str)

                idx = df[df["Title"].str.lower() == title.strip().lower()].index
                if not idx.empty:
                    df.loc[idx[0]] = parsed
                else:
                    df = pd.concat([df, pd.DataFrame([parsed])], ignore_index=True)
                st.session_state.manual_df = df
                st.success("Manual entry added or replaced.")
            unlock_ui()

    if not st.session_state.manual_df.empty:
        st.subheader("📋 Manual Entries Preview")
        st.dataframe(st.session_state.manual_df)

        out = BytesIO()
        st.session_state.manual_df.to_excel(out, index=False, sheet_name="Manual")
        out.seek(0)
        st.download_button("📁 Download Manual Data", out, "manual_challenges.xlsx")
