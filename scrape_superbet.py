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


def scrape_superbet() -> pd.DataFrame():
    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    # SUPERBET
    url = 'https://superbet.pl/zaklady-bukmacherskie/pilka-nozna/polska/'

    # load page
    driver.get(url)

    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
               "stake_draw", "stake_2_wins", "url"]
    
    # get table elements of every polish football league (on the same page)
    table_elements = driver.find_elements(
                    By.CLASS_NAME, 'event-row__layout')
    
    for table_element in table_elements:
        # split row into seperate items  
        item = table_element.text.split("\n")
        
        # if invalid data - skip 
        if len(item) < 13 or not item[6].replace(".", "").isnumeric() or not item[9].replace(".", "").isnumeric() or not item[12].replace(".", "").isnumeric():
            print("SuperBet: Error appending - " + " | ".join(item))
            continue

        # append item
        dct = {"team_1": item[2],
                "team_2": item[3],
                "stake_1_wins": item[6],
                "stake_draw": item[9],
                "stake_2_wins": item[12],
                "url": url}
        df = df._append(pd.DataFrame(
            [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    print(f"{'Superbet:':<10} {len(df)}")

    return df


# # # test
# df = pd.DataFrame()
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

# df = df._append(scrape_superbet(), ignore_index=True)
# print(df.head())
