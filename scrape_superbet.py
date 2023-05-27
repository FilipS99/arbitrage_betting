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
            #               /html/body/div[1]/div/div/div[1]/div/div[2]/div/div[3]/div/div/div/div/div[1]/div/div[2]/div[3]
            #               /html/body/div[1]/div/div/div[1]/div/div[2]/div/div[3]/div/div/div/div/div[1]/div/div[2]/div[3]/div/div[1]/div[2]/div[2]/div
            # print(table_row.text.split("\n"))

            # append to DataFrame
            lst = table_row.text.split("\n")
            # ['3.06', '17:30', 'Podbeskidzie', 'Resovia', '16889', '1', '1.67', '1.67', 'X', '4.00', '4.00', '2', '5.00', '5.00', '+119']
            dct = {"team_1": lst[2],
                   "team_2": lst[3],
                   "stake_1_wins": lst[6],
                   "stake_draw": lst[9],
                   "stake_2_wins": lst[12],
                   "url": url}
            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

            i += 1
    except Exception as e:
        # print(e)
        pass

    return df


# # test
# df = pd.DataFrame()
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

# # chrome driver setup
# options = Options()
# # options.add_argument("--headless")  # opens in background
# driver = webdriver.Chrome(options=options)


# url = 'https://superbet.pl/zaklady-bukmacherskie/pilka-nozna/polska/'
# df = df._append(scrape_superbet(driver, url), ignore_index=True)
# print("SUPERBET SUPERBET SUPERBET SUPERBET", df.head())

# # close chrome
# driver.quit()
