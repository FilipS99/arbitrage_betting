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


def scrape_superbet(driver: webdriver.Chrome(), url: str) -> pd.DataFrame():
    # load page
    driver.get(url)

    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
               "stake_draw", "stake_2_wins", "url"]

    # scrape rows
    i = 3
    try:
        while (1):
            table_row = driver.find_element(
                By.XPATH, f'/html/body/div[1]/div/div/div[1]/div/div[2]/div/div[3]/div/div/div/div/div[1]/div/div[2]/div[{i}]')
            # print(table_row.text.split("\n"))

            # append to DataFrame
            lst = table_row.text.split("\n")
            # ['SOB.', '17:30', 'Raków', 'Lubin', '6305', '1.47', '1.47', '4.60', '4.60', '6.50', '6.50', '+350']
            dct = {"team_1": lst[2],
                   "team_2": lst[3],
                   "stake_1_wins": lst[5],
                   "stake_draw": lst[7],
                   "stake_2_wins": lst[9],
                   "url": url}
            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

            i += 1
    except Exception as e:
        # print(e)
        pass

    # time.sleep(100)

    # print(df.head())

    return df
