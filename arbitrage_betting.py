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

if __name__ == "__main__":
    df = pd.DataFrame()
    # expected columns
    # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

    # scrape websites
    df = df._append(scrape_sts(), ignore_index=True)
    df = df._append(scrape_superbet(), ignore_index=True)

    # TODO zbudowac slownik do zamiany synonimów nazw zespołów, np. Górnik Z./G. Zabrze -> Górnik Zabrze
    # TODO zbudować logikę na wyłapanie duplikatów spotkań i wyliczenie % zysku (uwzględnić podatek)

    # save CSV file
    filename = datetime.now().strftime("%Y%m%d_%H%M%S.xlsx")
    output_path = 'D:\\Edukacja\\Projekty\\arbitrage_betting\\output\\'
    df.to_excel(output_path+filename,
                header=True, index=False)
