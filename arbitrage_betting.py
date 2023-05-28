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
from scrape_etoto import scrape_etoto
from scrape_totolotek import scrape_totolotek
from scrape_lvbet import scrape_lvbet
from rename_synonyms import rename_synonyms
from calculate_bets_outcomes import calculate_bets_outcomes

if __name__ == "__main__":
    # variables
    # save CSV file
    filename_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = 'D:\\moje\python_projects\\arbitrage_betting\\output\\'
    bet_amount = 1000

    # setup
    df = pd.DataFrame()
    # expected columns
    # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    # TODO OTWIERANIE STRON NA ROZNYCH TABACH I DOPIERO POTEM SCRAPING, ZEBY JS ZALADOWAL ZAWARTOSC

    # scrape websites & append to DF
    # lvbet liga 1
    url = 'https://lvbet.pl/pl/zaklady-bukmacherskie/multiple--?leagues=37424'
    df = df._append(scrape_lvbet(driver, url), ignore_index=True)
    print("LVBET LVBET LVBET LVBET\n", df.tail())
    print("")

    # totolotek 1 liga
    url = 'https://www.totolotek.pl/pl/pilka-nozna-polska-i-liga'
    df = df._append(scrape_totolotek(driver, url), ignore_index=True)
    print("TOTOLOTEK TOTOLOTEK TOTOLOTEK\n", df.tail())
    print("")

    # etoto 1 liga
    url = 'https://www.etoto.pl/zaklady-bukmacherskie/pilka-nozna/polska/polska-1-liga/305'
    df = df._append(scrape_etoto(driver, url), ignore_index=True)
    print("ETOTO ETOTO ETOTO\n", df.tail())
    print("")

    # STS liga 1
    url = 'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/1-liga/184/30860/86440/'
    df = df._append(scrape_sts(driver, url), ignore_index=True)
    print("STS STS STS\n", df.tail())
    print("")

    # # STS ekstraklasa
    # url = 'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/ekstraklasa/184/30860/86441/'
    # df = df._append(scrape_sts(driver, url), ignore_index=True)
    # print("STS STS STS STS STS STS STS STS\n", df.tail())

    url = 'https://superbet.pl/zaklady-bukmacherskie/pilka-nozna/polska/'
    df = df._append(scrape_superbet(driver, url), ignore_index=True)
    print("SUPERBET SUPERBET SUPERBET SUPERBET\n", df.tail())
    print("")

    # close chrome
    driver.quit()

    # replace synonyms (if needed)
    df = rename_synonyms(df)

    # generate all possible bets combinations
    calculate_bets_outcomes(df, bet_amount, output_path, filename_datetime)

    # save scraped data
    df.to_excel(output_path+filename_datetime+"_scraped.xlsx",
                header=True, index=False)
