import os
import subprocess
import glob
from .config import SCRAPER_DIR, CHALLENGE_OUTPUT_PREFIX

def get_latest_challenge_excel():
    files = glob.glob(os.path.join(f"{SCRAPER_DIR}/Excel-Files", f"{CHALLENGE_OUTPUT_PREFIX}*.xlsx"))
    return max(files, key=os.path.getmtime) if files else None

def run_scraper(url):
    return subprocess.run(
        ["python", "web-scraping.py", url],
        cwd=SCRAPER_DIR,
        capture_output=True,
        text=True
    )
