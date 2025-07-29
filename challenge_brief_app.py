import streamlit as st
import pandas as pd
import re
import google.generativeai as genai
from io import BytesIO

# ------------------ CONFIG ------------------
genai.configure(api_key="AIzaSyC-6SVeD3XZ17RQ0lXG2sJErg6mP1RCP0A")
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

prompt_template = """
You will be given a NASA Space Apps hackathon challenge brief.

Extract and fill the following structured fields based on the challenge:

1. Challenge Title (short and clear)
2. Challenge Summary: 2-3 lines summarizing the challenge with the core problem and context
3. Relevant Fields: Choose from:
   - GIS / Remote Sensing
   - AI / Machine Learning
   - 3D Modeling / Animation
   - Software Engineering
   - Augmented & Virtual Reality (AR/VR)
   - Storytelling / Video Editing
   - Data Science / Data Analysis
   - Mobile App Development
   - Web Development
   - Artificial Intelligence (AI)
   - Game Development
   - UI & UX Design
4. Required Technical Skills (e.g., Python, Unity, TensorFlow, Blender)
5. Potential Workshop/Session Topics (relevant training or crash courses)
6. Recommended Mentor Specializations
7. Overall Category (e.g., Earth, Space, Health, Humans, Climate, Oceans, etc.)

Challenge Brief:
\"\"\"
{brief}
\"\"\"

Respond in the following format:

Title: ...
Summary: ...
Fields: ...
Skills: ...
Workshops: ...
Mentors: ...
Category: ...
"""

# -------------- Gemini API Call --------------
def analyze_brief(brief):
    prompt = prompt_template.format(brief=brief)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return str(e)

# -------------- Output Parser ----------------
def parse_output(output):
    def extract(field):
        match = re.search(f"{field}: (.*?)(?=\n[A-Z]|$)", output, re.DOTALL)
        return match.group(1).strip() if match else ""

    return pd.Series({
        "Title": extract("Title"),
        "Summary": extract("Summary"),
        "Fields": extract("Fields"),
        "Skills": extract("Skills"),
        "Workshops": extract("Workshops"),
        "Mentors": extract("Mentors"),
        "Category": extract("Category")
    })

# --------------- Streamlit App ---------------
st.set_page_config(page_title="NASA Brief Tagger", layout="wide")
st.title("🚀 NASA Space Apps - Challenge Brief Analyzer")

uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    if "Challenge Brief" not in df.columns:
        st.error("❌ The Excel file must contain a 'Challenge Brief' column.")
    else:
        st.success("✅ File uploaded and recognized successfully!")
        
        if st.button("🧠 Analyze Briefs"):
            with st.spinner("Analyzing challenge briefs using Gemini..."):
                results = []
                progress_bar = st.progress(0)  # Initialize progress bar
                total = len(df)

                for i, brief in enumerate(df["Challenge Brief"]):
                    result = analyze_brief(brief)
                    results.append(result)
                    progress_bar.progress((i + 1) / total)  # Update bar

                result_series = pd.Series(results)
                parsed_df = result_series.apply(parse_output)
                final_df = pd.concat([df, parsed_df], axis=1)
            
            
            st.success("✅ Analysis complete!")
            st.dataframe(final_df)

            output = BytesIO()
            final_df.to_excel(output, index=False)
            output.seek(0)

            st.download_button(
                label="📥 Download Results as Excel",
                data=output,
                file_name="challenge_outputs.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
