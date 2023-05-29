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
import threading

from scrape_sts import scrape_sts
from scrape_superbet import scrape_superbet
from scrape_etoto import scrape_etoto
from scrape_totolotek import scrape_totolotek
from scrape_lvbet import scrape_lvbet
from rename_synonyms import rename_synonyms
from calculate_bets_outcomes import calculate_bets_outcomes


# overriding Thread so I can access outputs
class ScrapeThread(threading.Thread):
    def __init__(self, target_func):
        super().__init__()
        self.target_func = target_func
        self.result = None

    def run(self):
        self.result = self.target_func()


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
    # options = Options()
    # # options.add_argument("--headless")  # opens in background
    # options.add_argument('--ignore-certificate-errors')
    # driver = webdriver.Chrome(options=options)
    # driver.implicitly_wait(3)

    # Create thread objects for each function
    thread1 = ScrapeThread(target_func=scrape_totolotek)
    thread2 = ScrapeThread(target_func=scrape_etoto)
    thread3 = ScrapeThread(target_func=scrape_superbet)
    thread4 = ScrapeThread(target_func=scrape_sts)
    thread5 = ScrapeThread(target_func=scrape_lvbet)

    # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    # Wait for the threads to complete
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()

    print("All threads have finished executing")
    
    # Merge threds outputs
    df = pd.concat([thread1.result, thread2.result, thread3.result, thread4.result, thread5.result], ignore_index=True)


    # scrape websites & append to DF
    # df = df._append(scrape_lvbet(driver, url), ignore_index=True)
    

    # replace synonyms (if needed)
    df = rename_synonyms(df)

    # generate all possible bets combinations
    calculate_bets_outcomes(df, bet_amount, output_path, filename_datetime)

    # save scraped data
    df.to_excel(output_path+filename_datetime+"_scraped.xlsx",
                header=True, index=False)

