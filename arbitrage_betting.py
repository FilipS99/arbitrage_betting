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
from datetime import datetime

from scrape_sts import scrape_sts
from scrape_superbet import scrape_superbet
from rename_synonyms import rename_synonyms

if __name__ == "__main__":
    df = pd.DataFrame()
    # expected columns
    # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    driver = webdriver.Chrome(options=options)

    # scrape websites & append to DF
    # liga 1
    url = 'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/1-liga/184/30860/86440/'
    df = df._append(scrape_sts(driver, url), ignore_index=True)
    print("STS STS STS", df.tail())

    # ekstraklasa
    url = 'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/ekstraklasa/184/30860/86441/'
    df = df._append(scrape_sts(driver, url), ignore_index=True)
    print("STS STS STS STS STS STS STS STS", df.tail())

    url = 'https://superbet.pl/zaklady-bukmacherskie/pilka-nozna/polska/'
    df = df._append(scrape_superbet(driver, url), ignore_index=True)
    print("SUPERBET SUPERBET SUPERBET SUPERBET", df.tail())

    # close chrome
    driver.quit()

    # replace synonyms (if needed)
    df = rename_synonyms(df)

    # print(df.head())
    # TODO zbudować logikę na wyłapanie duplikatów spotkań i wyliczenie % zysku (uwzględnić podatek)

    # save CSV file
    filename = datetime.now().strftime("%Y%m%d_%H%M%S.xlsx")
    output_path = 'D:\\Edukacja\\Projekty\\arbitrage_betting\\output\\'
    df.to_excel(output_path+filename,
                header=True, index=False)
