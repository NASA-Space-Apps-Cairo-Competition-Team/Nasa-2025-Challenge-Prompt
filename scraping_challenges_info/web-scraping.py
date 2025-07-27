from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup

import pandas as pd
import time

# The driver is used because NASA's website uses JS to generate HTML components
# and getting the url using the normal requests methods will not work because components
# are not generated untill the page is fully loaded
options = Options()
options.add_argument('--headless')

# Change the driver for your prefered/available browser
driver_path = '../driver/msedgedriver.exe'
service = Service(executable_path = driver_path)
driver = webdriver.Edge(service=service, options=options)

# Change the url to the current year's challenges url
url = 'https://www.spaceappschallenge.org/nasa-space-apps-2024/challenges/'
driver.get(url)
# if the components are empty it could be due to loading delay or issue with your connection
# try increasing time.sleep to give it a chance to load with your crappy internet
time.sleep(5)

print(driver.title)

soup = BeautifulSoup(driver.page_source, 'html.parser')
container = soup.find('div', class_='challenge-index_results__z_Zp5')
challenge_links = container.find_all('a', href=True)

print(f"number of challenges: {len(challenge_links)}\n")


challenges = []
for a in challenge_links:
    title = a.h2.get_text(strip=True)
    href = a['href']
    full_url = f"https://www.spaceappschallenge.org{href}" if href.startswith('/') else href
    print(f"➡{title}\n➡ {full_url}\n")
    challenges.append({
        "Title":title,
        "url": full_url
        })

# Creating a DataFrame
df = pd.DataFrame(challenges)

# Saving the DataFrame to an Excel file
excel_file = 'challenges.xlsx'
df.to_excel(excel_file, index=False)

driver.quit()