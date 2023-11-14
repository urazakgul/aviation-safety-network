from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd
from io import StringIO

driver = webdriver.Chrome()
master_df = pd.DataFrame()

for year in range(1902, 2024):
    url = f'https://aviation-safety.net/wikibase/dblist.php?Year={year}'
    driver.get(url)
    time.sleep(2)

    page_element = driver.find_element(By.CSS_SELECTOR, 'div.pagenumbers')
    page_a_elements = page_element.find_elements(By.TAG_NAME, 'a')

    if not page_a_elements:

        current_page_element = page_element.find_element(By.CSS_SELECTOR, 'span.current')
        page_num = int(current_page_element.text)
    else:

        last_page_element = page_a_elements[-1]
        page_num = int(last_page_element.text)

    for page in range(1, page_num + 1):
        page_url = f'{url}&page={page}'
        driver.get(page_url)
        time.sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'hp'})

        df = pd.read_html(StringIO(str(table)))[0]

        master_df = pd.concat([master_df, df], ignore_index=True)

driver.quit()

master_df.to_excel('aviation_safety.xlsx', index=False)

# Alternative

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd
from io import StringIO
from concurrent.futures import ThreadPoolExecutor
import threading

def scrape_year(year):
    url = f'https://aviation-safety.net/wikibase/dblist.php?Year={year}'
    driver.get(url)
    time.sleep(2)

    page_element = driver.find_element(By.CSS_SELECTOR, 'div.pagenumbers')
    page_a_elements = page_element.find_elements(By.TAG_NAME, 'a')

    if not page_a_elements:
        current_page_element = page_element.find_element(By.CSS_SELECTOR, 'span.current')
        page_num = int(current_page_element.text)
    else:
        last_page_element = page_a_elements[-1]
        page_num = int(last_page_element.text)

    for page in range(1, page_num + 1):
        page_url = f'{url}&page={page}'
        driver.get(page_url)
        time.sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'hp'})

        df = pd.read_html(StringIO(str(table)))[0]

        with lock:
            master_df_list.append(df)

lock = threading.Lock()

driver = webdriver.Chrome()
master_df_list = []

years_to_scrape = list(range(1902, 2024))

num_threads = 4

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(scrape_year, years_to_scrape)

driver.quit()

master_df = pd.concat(master_df_list, ignore_index=True)
master_df.to_excel('asn_data_multithreaded.xlsx', index=False)