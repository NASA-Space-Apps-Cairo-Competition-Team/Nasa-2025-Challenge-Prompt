import streamlit as st
import pandas as pd
from io import BytesIO

from LLM_AND_UI.state import freeze_ui_for_others, unlock_ui
from LLM_AND_UI.llm import analyze_brief
from LLM_AND_UI.parser import parse_output

def render_upload_tab():
    SECTION = "Upload"
    freeze_ui_for_others(SECTION)
    st.header("📤 Upload Excel File with Challenge Briefs")

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    if uploaded_file:
        try:
            st.subheader("📄 Raw Excel Preview (Before AI Processing)")
            excel_data = pd.ExcelFile(uploaded_file)
            sheet_names = excel_data.sheet_names
            selected_sheet = st.selectbox("📄 Select sheet to preview", sheet_names, key="upload_sheet_selector")

            df = excel_data.parse(selected_sheet)
            df.columns = df.columns.astype(str).str.strip()
            st.session_state.upload_raw_df = df
            st.dataframe(df)

            if st.button("🤖 Analyze Uploaded Sheet with AI", key="upload_analyze_btn"):
                st.session_state.active_section = SECTION

                if "Title" not in df.columns:
                    st.error("Missing 'Title' column in uploaded file.")
                    unlock_ui()
                    return
                progress_bar = st.progress(0, text="Starting analysis...")

                parsed = []
                total = len(df)
                for i, (_, row) in enumerate(df.iterrows(), 1):
                    progress_bar.progress(i / total, text=f"Analyzing {i} of {total} challenges...")
                    out = analyze_brief(row)
                    result = parse_output(out)
                    result["Title"] = row["Title"]
                    parsed.append(result)

                st.session_state.upload_df = pd.DataFrame(parsed)
                st.success("✅ Upload analysis complete!")
                progress_bar.empty()
                unlock_ui()

        except Exception as e:
            st.error(f"❌ Error reading Excel file: {e}")

    if st.session_state.get("upload_df") is not None and not st.session_state.upload_df.empty:
        _render_add_replace_ui("upload_df", "Uploaded", "upload_title_input", "upload_brief_input")

def _render_add_replace_ui(state_key, sheet_name, title_key, brief_key):
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
                st.success("✅ Challenge added or replaced.")
                st.rerun()

    out = BytesIO()
    st.session_state[state_key].to_excel(out, index=False, sheet_name=sheet_name)
    out.seek(0)
    st.download_button(f"📁 Download {sheet_name} Data", out, f"{sheet_name.lower()}_challenges.xlsx")
