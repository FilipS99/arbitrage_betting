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


def scrape_etoto(driver: webdriver.Chrome, url: str) -> pd.DataFrame():
    # load page
    driver.get(url)

    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
               "stake_draw", "stake_2_wins", "url"]

    # scrape rows
    i = 1
    try:
        while (1):
            table_row = driver.find_element(
                By.XPATH, f'/html/body/div[3]/div[3]/div[1]/div[2]/div[3]/div/div/div[3]/partial[4]/div/div/div/div[2]/div[2]/div[2]/ul/li[{i}]/ul/li')
            #               /html/body/div[3]/div[3]/div[1]/div[2]/div[3]/div/div/div[3]/partial[4]/div/div/div/div[2]/div[2]/div[2]/ul/li[1]/ul/li
            #               /html/body/div[3]/div[3]/div[1]/div[2]/div[3]/div/div/div[3]/partial[4]/div/div/div/div[2]/div[2]/div[2]/ul/li[2]/ul/li
            print(table_row.text.split("\n"))

            # append to DataFrame
            lst = table_row.text.split("\n")
            # ['Wisła Kraków', 'Zagłębie Sosnowiec', 'Dzisiaj', '12:40', '1.20', '6.50', '13.00', '+201']
            dct = {"team_1": lst[0],
                   "team_2": lst[1],
                   "stake_1_wins": lst[4],
                   "stake_draw": lst[5],
                   "stake_2_wins": lst[6],
                   "url": url}
            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

            i += 1
    except Exception as e:
        # print(e)
        pass

    return df


# # # test
# df = pd.DataFrame()
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

# # chrome driver setup
# options = Options()
# # options.add_argument("--headless")  # opens in background
# driver = webdriver.Chrome(options=options)


# url = 'https://www.etoto.pl/zaklady-bukmacherskie/pilka-nozna/polska/polska-1-liga/305'
# df = df._append(scrape_etoto(driver, url), ignore_index=True)
# print("ETOTO ETOTO ETOTO", df.head())

# # close chrome
# driver.quit()
