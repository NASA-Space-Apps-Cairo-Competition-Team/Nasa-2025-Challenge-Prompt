import sys
import os
import time
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from datetime import datetime

# ---------- Handle Command-Line Arguments ----------
if len(sys.argv) != 2:
    print("Usage: python web-scraping.py <challenge_list_url>")
    sys.exit(1)

url = sys.argv[1]

# ---------- Setup Selenium ----------
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--log-level=3')

driver_path = os.path.join(os.path.dirname(__file__), '../driver/msedgedriver.exe')
service = Service(executable_path=driver_path)
driver = webdriver.Edge(service=service, options=options)

# ---------- Scrape ----------
driver.get(url)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')
container = soup.find('div', class_='challenge-index_results__z_Zp5')
challenge_links = container.find_all('a', href=True)

print(f"\n Found {len(challenge_links)} challenges.\n")

basic_info = []
detailed_info = []

def extract_meta_info(detail_soup):
    result = {}
    meta_sections = detail_soup.select('.challenge-info_meta__gZ65p')

    for section in meta_sections:
        label = section.select_one('.challenge-info_label__qTNb0')
        if not label:
            continue
        label_text = label.text.strip()

        tags = section.select('.challenge-info_tag__G_QQv')
        if tags:
            result[label_text] = [tag.text.strip() for tag in tags]
        else:
            span = section.select_one('span')
            if span:
                result[label_text] = span.text.strip()
    return result

def extract_html_sections(detail_soup):
    content = detail_soup.select_one('.challenge-details_content__218__')
    if not content:
        return {}

    children = content.find_all(recursive=False)
    sections = {}
    brief_parts = []
    current_section = None

    for el in children:
        if el.name == 'h2':
            current_section = el.get_text(strip=True)
            sections[current_section] = ''
        elif current_section:
            if el.name == 'ul':
                items = [f"- {li.get_text(strip=True)}" for li in el.find_all('li')]
                sections[current_section] += '\n'.join(items) + '\n'
            else:
                text = el.get_text(strip=True)
                if text:
                    sections[current_section] += text + '\n'
        elif el.name == 'p':
            text = el.get_text(strip=True)
            if text:
                brief_parts.append(text)

    if brief_parts:
        sections["Brief"] = '\n'.join(brief_parts)

    return sections

wanted_sections = ["Brief", "Background", "Objectives", "Potential Considerations"]

for i, a in enumerate(challenge_links):
    try:
        title = a.h2.get_text(strip=True)
        href = a['href']
        full_url = f"https://www.spaceappschallenge.org{href}" if href.startswith('/') else href

        basic_info.append({"Title": title, "URL": full_url})

        driver.get(full_url)
        time.sleep(2)
        detail_soup = BeautifulSoup(driver.page_source, 'html.parser')

        section_data = {}
        detailed_entry = {"Title": title, "URL": full_url}

        script_tag = detail_soup.find("script", id="__NEXT_DATA__", type="application/json")
        if script_tag:
            data = json.loads(script_tag.string)
            challenge_data = data["props"]["pageProps"]["challenge"]
            data_blocks = challenge_data.get("dataBlocks", [])

            for block in data_blocks:
                block_title = block.get("title", "").strip()
                block_text = block.get("text", "").strip()
                if block_title in wanted_sections:
                    section_data[block_title] = block_text

            detailed_entry.update({
                "Theme": challenge_data.get("challengeTheme", {}).get("title", ""),
                "Type": challenge_data.get("challengeType", {}).get("title", ""),
                "Category": challenge_data.get("challengeCategory", {}).get("title", "")
            })

        meta_info = extract_meta_info(detail_soup)
        detailed_entry["Difficulty"] = ", ".join(meta_info.get("Difficulty", []))
        detailed_entry["Subjects"] = ", ".join(meta_info.get("Subjects", []))

        html_sections = extract_html_sections(detail_soup)
        for sec in wanted_sections:
            if sec not in section_data and sec in html_sections:
                section_data[sec] = html_sections[sec]

        detailed_entry.update(section_data)
        detailed_info.append(detailed_entry)

        print(f" {i+1}. {title} scraped.")

    except Exception as e:
        print(f" Error on challenge {i+1}: {e}")
        continue

driver.quit()

# ---------- Save Excel to Excel-Files ----------
excel_dir = os.path.join(os.path.dirname(__file__), "Excel-Files")
os.makedirs(excel_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
excel_filename = f"nasa_challenges_{timestamp}.xlsx"
full_path = os.path.join(excel_dir, excel_filename)

df_basic = pd.DataFrame(basic_info)
df_detailed = pd.DataFrame(detailed_info)

with pd.ExcelWriter(full_path) as writer:
    df_basic.to_excel(writer, sheet_name="Basic Info", index=False)
    df_detailed.to_excel(writer, sheet_name="Challenge Details", index=False)

print(f"\n Data saved to: {full_path}")
