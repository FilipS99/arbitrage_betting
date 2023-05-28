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


def scrape_totolotek(driver: webdriver.Chrome, url: str) -> pd.DataFrame():
    # load page
    driver.get(url)

    # handle pop-ups
    allow_cookies_btn = driver.find_element(
        By.XPATH, '//*[@id="cookiescript_accept"]')
    allow_cookies_btn.send_keys(Keys.ENTER)

    popup_age_btn = driver.find_element(
        By.XPATH, '//*[@id="ByModalContentConfirmButton"]')
    popup_age_btn.send_keys(Keys.ENTER)

    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
               "stake_draw", "stake_2_wins", "url"]

    # scrape rows
    i = 1
    try:
        while (1):
            table_row = driver.find_element(
                By.XPATH, f'/html/body/app-root/div/web-layout/div[1]/div/section/div/home-page/section/div/games-list/div/gamelist/div/div/div[{i}]/game/div')
            #               /html/body/app-root/div/web-layout/div[1]/div/section/div/home-page/section/div/games-list/div/gamelist/div/div/div[1]/game/div
            #               /html/body/app-root/div/web-layout/div[1]/div/section/div/home-page/section/div/games-list/div/gamelist/div/div/div[2]/game/div
            print(table_row.text.split("\n"))

            # append to DataFrame
            lst = table_row.text.split("\n")
            # ['Wisła Kraków', 'Zagłębie Sosnowi.', 'Niedz. 28.05', '12:40', '1', '1.25', 'X', '5.20', '2', '8.87', '1X', '1.01', '12', '1.09', 'X2', '3.25', '0:1', '1', '1.78', 'X', '3.70', '2', '3.25', '+29']
            dct = {"team_1": lst[0],
                   "team_2": lst[1],
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


# # test
# df = pd.DataFrame()
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

# # chrome driver setup
# options = Options()
# # options.add_argument("--headless")  # opens in background
# driver = webdriver.Chrome(options=options)
# driver.implicitly_wait(5)

# url = 'https://www.totolotek.pl/pl/pilka-nozna-polska-i-liga'
# df = df._append(scrape_totolotek(driver, url), ignore_index=True)
# print(df.head())

# # close chrome
# driver.quit()
