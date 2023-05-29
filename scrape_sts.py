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


def scrape_sts() -> pd.DataFrame():
    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    # STS liga 1
    url = 'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/1-liga/184/30860/86440/'

    # load page
    driver.get(url)

    # handle pop-ups
    # allow_cookies_btn = driver.find_element(
    #     By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]')
    # allow_cookies_btn.send_keys(Keys.ENTER)

    # popup_cancel_btn = driver.find_element(
    #     By.XPATH, '/html/body/div[5]/div[2]/div[1]/div/div[2]/div[3]/button[1]')
    # popup_cancel_btn.send_keys(Keys.ENTER)

    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
               "stake_draw", "stake_2_wins", "url"]

    # scrape rows
    divs = ['3', '5']
    for d in divs:
        i = 1
        try:
            while (1):
                table_row = driver.find_element(
                    By.XPATH, f'/html/body/div[{d}]/div[2]/div[6]/div[5]/div[2]/div[2]/div/table[{i}]/tbody/tr/td[2]/table/tbody/tr')
                #               /html/body/div[3]/div[2]/div[6]/div[5]/div[2]/div[2]/div/table[1]/tbody/tr/td[2]/table
                #               /html/body/div[3]/div[2]/div[6]/div[5]/div[2]/div[2]/div/table[2]/tbody/tr/td[2]/table
                # print(table_row.text.split("\n"))

                # append to DataFrame
                lst = table_row.text.split("\n")
                # ['Cracovia', '2.44', 'X', '3.35', 'W. Płock', '2.80']
                dct = {"team_1": lst[0],
                       "team_2": lst[4],
                       "stake_1_wins": lst[1],
                       "stake_draw": lst[3],
                       "stake_2_wins": lst[5],
                       "url": url}
                df = df._append(pd.DataFrame(
                    [dct], columns=columns), ignore_index=True)

                i += 1
        except Exception as e:
            # print(e)
            pass

    # close chrome
    driver.quit()

    print(f"{'STS:':<10} {len(df)}")

    return df


# # test
# df = pd.DataFrame()
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

# # chrome driver setup
# options = Options()
# # options.add_argument("--headless")  # opens in background
# driver = webdriver.Chrome(options=options)

# url = 'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/1-liga/184/30860/86440/'
# df = df._append(scrape_sts(driver, url), ignore_index=True)
# print("STS STS STS", df.head())


# url = 'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/ekstraklasa/184/30860/86441/'
# df = df._append(scrape_sts(driver, url), ignore_index=True)
# print("STS STS STS", df.head())

# close chrome
# driver.quit()
