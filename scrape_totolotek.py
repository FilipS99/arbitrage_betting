import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
import pandas as pd
import time


def scrape_totolotek() -> pd.DataFrame():    
    # totolotek 1 liga
    links = [('https://www.totolotek.pl/pl/pilka-nozna-polska-i-liga', 'polish football'),
             ('https://www.totolotek.pl/pl/pilka-nozna/polska-iii-liga-gr-2', 'polish football'),    
             ('https://www.totolotek.pl/pl/pilka-nozna/polska-iii-liga-gr-1', 'polish football')]

    # initialize output DataFrame
    columns = ["team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url", "category"]
    df = pd.DataFrame({}, columns=columns)

    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    for link in links:
        # unpack tuple
        url, category = link

        # load page
        driver.get(url)
        
        time.sleep(3)

        # get table elements of every polish football league (on the same page)
        table_elements = driver.find_elements(
                        By.XPATH, '/html/body/app-root/div/web-layout/div[1]/div/section/div/home-page/section/div/games-list/div/gamelist/div/div/div[*]/game/div')
        
        for table_element in table_elements:
            # split row into seperate items  
            item = table_element.text.split("\n")
            
            # if invalid data - skip 
            if len(item) < 10 or not item[5].replace(".", "").isnumeric() or not item[7].replace(".", "").isnumeric() or not item[9].replace(".", "").isnumeric():
                print("Totolotek: Error appending - " + " | ".join(item))
                continue

            # append item
            dct = {"team_1": item[0],
                   "team_2": item[1],
                   "stake_1_wins": item[5],
                   "stake_draw": item[7],
                   "stake_2_wins": item[9],
                   "url": url,
                   "category": category}
            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    # print(f"{'Totolotek:':<10} {len(df)}")

    return df


# test
# expected columns
# ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

# df = pd.DataFrame()
# df = df._append(scrape_totolotek(), ignore_index=True)
# print(df.head())

