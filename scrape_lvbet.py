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


def scrape_lvbet() -> pd.DataFrame():
    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    # lvbet liga 1
    url = 'https://lvbet.pl/pl/zaklady-bukmacherskie/multiple--?leagues=37424'

    # load page
    driver.get(url)

    # handle pop-ups
    # allow_cookies_btn = driver.find_element(
    #     By.XPATH, '//*[@id="cookiescript_accept"]')
    # allow_cookies_btn.send_keys(Keys.ENTER)

    # popup_age_btn = driver.find_element(
    #     By.XPATH, '//*[@id="ByModalContentConfirmButton"]')
    # popup_age_btn.send_keys(Keys.ENTER)

    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
               "stake_draw", "stake_2_wins", "url"]

    # scrape rows
    divs = ['2', '3', '4', '5']
    for d in divs:
        i = 1
        try:
            while (1):
                table_row = driver.find_element(
                    By.XPATH, f'/html/body/app-root/main-site-container/div[2]/div/div/pre-matches/section/selected-sports-view/selected-sports-view-container/div/div/div[{d}]/div[2]/match-row[{i}]/div')
                #               /html/body/app-root/main-site-container/div[2]/div/div/pre-matches/section/selected-sports-view/selected-sports-view-container/div/div/div[2]/div[2]/match-row[1]/div
                #               /html/body/app-root/main-site-container/div[2]/div/div/pre-matches/section/selected-sports-view/selected-sports-view-container/div/div/div[3]/div[2]/match-row/div
                # print(table_row.text.split("\n"))

                # append to DataFrame
                lst = table_row.text.split("\n")
                # ['12:40', '28.05', 'Wisła Kraków', 'Zagłębie Sosnowiec', '1.2', '6.75', '14', '+210']
                dct = {"team_1": lst[2],
                       "team_2": lst[3],
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

    # close chrome
    driver.quit()

    print(f"{'Lvbet:':<10} {len(df)}")

    return df


# # test
# df = pd.DataFrame()
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

# # chrome driver setup
# options = Options()
# # options.add_argument("--headless")  # opens in background
# options.add_argument('--ignore-certificate-errors')
# driver = webdriver.Chrome(options=options)
# driver.implicitly_wait(5)

# url = 'https://lvbet.pl/pl/zaklady-bukmacherskie/multiple--?leagues=37424'
# df = df._append(scrape_lvbet(driver, url), ignore_index=True)
# print(df.head())

# # close chrome
# driver.quit()
