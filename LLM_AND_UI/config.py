import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env variables
load_dotenv()

# Setup Gemini
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("MODEL_NAME", "gemini-1.5-pro-latest")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name=model_name)

# Directory Configs
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SCRAPER_DIR = os.path.join(BASE_DIR, "scraping_challenges_info")
CHALLENGE_OUTPUT_PREFIX = "nasa_challenges_"
