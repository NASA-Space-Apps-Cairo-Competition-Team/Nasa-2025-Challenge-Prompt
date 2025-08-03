import streamlit as st
import pandas as pd
from io import BytesIO

from LLM_AND_UI.state import freeze_ui_for_others, unlock_ui
from LLM_AND_UI.llm import analyze_brief
from LLM_AND_UI.parser import parse_output

def render_manual_tab():
    SECTION = "Manual"
    freeze_ui_for_others(SECTION)
    st.header("✍️ Manually Enter Challenge Brief")

    # Ensure manual_df exists and is initialized
    if "manual_df" not in st.session_state or st.session_state.manual_df is None:
        st.session_state.manual_df = pd.DataFrame(columns=["Title", "Summary"])

    title = st.text_input("Challenge Title", key="manual_title_input")
    brief = st.text_area("Challenge Brief", height=200, key="manual_brief_input")

    if st.button("🤖 Analyze and Add"):
        st.session_state.active_section = SECTION

        if not title.strip() or not brief.strip():
            st.warning("Both title and brief are required.")
        else:
            with st.spinner("Analyzing manual entry..."):
                row = {"Title": title.strip(), "Brief": brief.strip()}
                out = analyze_brief(row)
                parsed = parse_output(out)

                # Debugging output structure
                st.write("🔍 Parsed Output:", parsed)

                # Ensure 'Title' is in parsed output
                parsed["Title"] = title.strip()

                df = st.session_state.manual_df.copy()

                # Ensure 'Title' column exists
                if "Title" not in df.columns:
                    st.warning("🧹 Reinitializing manual_df to have proper columns.")
                    df = pd.DataFrame(columns=["Title", "Summary"])

                # Ensure correct types
                df["Title"] = df["Title"].astype(str)

                # Check for existing title (case-insensitive)
                idx = df[df["Title"].str.lower() == title.strip().lower()].index
                if not idx.empty:
                    df.loc[idx[0]] = parsed
                else:
                    df = pd.concat([df, pd.DataFrame([parsed])], ignore_index=True)

                st.session_state.manual_df = df
                st.success("✅ Challenge added or updated.")
        unlock_ui()

    if not st.session_state.manual_df.empty:
        st.subheader("🧾 Manually Added Challenges")
        st.dataframe(st.session_state.manual_df)

        out = BytesIO()
        st.session_state.manual_df.to_excel(out, index=False, sheet_name="Manual")
        out.seek(0)
        st.download_button("📁 Download Manual Data", out, "manual_challenges.xlsx")
