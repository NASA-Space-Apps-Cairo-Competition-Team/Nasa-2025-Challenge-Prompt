# Nasa-2025-Challenge-Prompt

## NASA Challenge Brief Tagger

A simple Streamlit app that uses **Gemini (Google Generative AI)** to analyze NASA Space Apps hackathon challenge briefs and extract structured metadata such as title, summary, relevant fields, skills, and more.

---

### App Preview

> Upload an Excel file
> Gemini generates structured insights for each challenge
> View results and download as Excel

---

Make sure your Excel file contains a column titled: `Challenge Brief`

---

### Features

* Upload `.xlsx` file with challenge briefs
* Uses **Gemini API** (`google-generativeai`) to extract:

  * Title
  * Summary
  * Relevant Fields
  * Required Skills
  * Workshop Topics
  * Mentor Specializations
  * Challenge Category
* Download results as a formatted Excel file

---

### Installation

#### 1. Clone the repository

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```
#### 3. Add your Gemini API key

Replace `"YOUR_API_KEY_HERE"` in `brief_tagger_app.py` with your actual key:

```python
genai.configure(api_key="YOUR_API_KEY_HERE")
```

---

### Run the App

```bash
streamlit run challenge_brief_app.py
```

---

### Dependencies

* `streamlit`
* `pandas`
* `openpyxl`
* `google-generativeai`
