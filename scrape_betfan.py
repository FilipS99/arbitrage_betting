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


def scrape_betfan() -> pd.DataFrame():
    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    # ligii polskie
    url = 'https://betfan.pl/lista-zakladow/pilka-nozna/polska/245'

    # load page
    driver.get(url)

    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
               "stake_draw", "stake_2_wins", "url"]

    # scrape rows
    elements = driver.find_elements(By.XPATH,'/html/body/div[1]/div[2]/main/div[3]/div/div[*]/div[2]/div[*]/div/div[2]') 

    for element in elements:
        item = element.text.split('\n')
        # ['Stal Rzeszów', 'Skra Częstochowa', 'Stal Rzeszów', '1.50', 'Remis', '4.50', 'Skra Częstochowa', '6.20', '+140']
        
        # if invalid data - skip 
        if len(item) < 7 or not item[3].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric() or not item[7].replace(".", "").isnumeric():
            print("BetFan: Error appending - " + " | ".join(item))
            continue
        
        # append item
        dct = {"team_1": item[0],
               "team_2": item[1],
               "stake_1_wins": item[3],
               "stake_draw": item[5],
               "stake_2_wins": item[7],
               "url": url}
        df = df._append(pd.DataFrame(
            [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    return df


# # # test
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

# df = pd.DataFrame()
# df = df._append(scrape_betfan(), ignore_index=True)
# print(df.head())