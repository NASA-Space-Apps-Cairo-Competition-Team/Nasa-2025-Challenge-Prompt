import streamlit as st
import pandas as pd
import time
from io import BytesIO

from LLM_AND_UI.llm import analyze_brief
from LLM_AND_UI.parser import parse_output
from LLM_AND_UI.utils import get_latest_challenge_excel, run_scraper
from LLM_AND_UI.state import freeze_ui_for_others, unlock_ui

def render_scrape_tab():
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

    if st.session_state.scrape_df is not None and not st.session_state.scrape_df.empty:
        _render_add_replace_ui("scrape_df", "Scraped", "scrape_title_input", "scrape_brief_input")


def _render_add_replace_ui(state_key, sheet_name, title_key, brief_key):
    from LLM_AND_UI.llm import analyze_brief
    from LLM_AND_UI.parser import parse_output

    st.subheader(f"🧾 {sheet_name} Dataset Preview")
    st.dataframe(st.session_state[state_key])

    st.subheader("✏️ Add or Replace Challenge")
    title_input = st.text_input("Title", key=title_key)
    brief_input = st.text_area("Brief", height=200, key=brief_key)

    if st.button(f"➕ Add/Replace in {sheet_name} Data"):
        if not title_input.strip() or not brief_input.strip():
            st.warning("Both title and brief are required.")
        else:
            with st.spinner("Analyzing new entry..."):
                row = {"Title": title_input.strip(), "Brief": brief_input.strip()}
                out = analyze_brief(row)
                parsed = parse_output(out)
                parsed["Title"] = title_input.strip()

                df = st.session_state[state_key].copy()
                df["Title"] = df["Title"].astype(str)

                idx = df[df["Title"].str.lower() == title_input.strip().lower()].index
                if not idx.empty:
                    df.loc[idx[0]] = parsed
                else:
                    df = pd.concat([df, pd.DataFrame([parsed])], ignore_index=True)

                st.session_state[state_key] = df
                st.success("Challenge added or replaced.")
                st.rerun()
  # 🔁 Force re-render to update preview

    out = BytesIO()
    st.session_state[state_key].to_excel(out, index=False, sheet_name=sheet_name)
    out.seek(0)
    st.download_button(f"📁 Download {sheet_name} Data", out, f"{sheet_name.lower()}_challenges.xlsx")
