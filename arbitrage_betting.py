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
from scrape_fuksiarz import scrape_fuksiarz
from scrape_forbet import scrape_forbet
from scrape_fortuna import scrape_fortuna
from scrape_betfan import scrape_betfan
from scrape_betclic import scrape_betclic
from scrape_totalbet import scrape_totalbet
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
    start_time = time.time()
    # save CSV file
    filename_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = 'D:\\moje\python_projects\\arbitrage_betting\\output\\'
    bet_amount = 1000

    # setup
    df = pd.DataFrame()
    # expected columns
    # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url", "category"]

    # Create thread objects for each function
    thread_sts = ScrapeThread(target_func=scrape_sts)
    thread_lvbet = ScrapeThread(target_func=scrape_lvbet)
    thread_superbet = ScrapeThread(target_func=scrape_superbet)
    thread_fuksiarz = ScrapeThread(target_func=scrape_fuksiarz)
    thread_etoto = ScrapeThread(target_func=scrape_etoto)
    thread_totolotek = ScrapeThread(target_func=scrape_totolotek)
    thread_forbet = ScrapeThread(target_func=scrape_forbet)
    thread_fortuna = ScrapeThread(target_func=scrape_fortuna)
    thread_betfan = ScrapeThread(target_func=scrape_betfan)
    thread_betclic = ScrapeThread(target_func=scrape_betclic)
    thread_totalbet = ScrapeThread(target_func=scrape_totalbet)

    # lvbet taking longest
    thread_lvbet.start()

    thread_superbet.start()
    thread_fuksiarz.start()
    thread_etoto.start()

    thread_superbet.join()
    thread_fuksiarz.join()
    thread_etoto.join()

    thread_totolotek.start()
    thread_forbet.start()
    thread_fortuna.start()

    thread_totolotek.join()
    thread_forbet.join()
    thread_fortuna.join()
    
    thread_betfan.start()
    thread_betclic.start()
    thread_totalbet.start()
    thread_sts.start()

    thread_betfan.join()
    thread_betclic.join()
    thread_totalbet.join()
    thread_sts.join()

    # lvbet taking longest
    thread_lvbet.join()

    print("\n-----------------------------------\n")
    print("All threads have finished executing")
    print(f"\nSTS:\n{thread_sts.result.groupby(['category']).size()}")
    print(f"\nLvbet:\n{thread_lvbet.result.groupby(['category']).size()}")
    print(f"\nSuperbet:\n{thread_superbet.result.groupby(['category']).size()}")
    print(f"\nFuksiarz:\n{thread_fuksiarz.result.groupby(['category']).size()}")
    print(f"\nEtoto:\n{thread_etoto.result.groupby(['category']).size()}")
    print(f"\nTotolotek:\n{thread_totolotek.result.groupby(['category']).size()}")
    print(f"\nForBet:\n{thread_forbet.result.groupby(['category']).size()}")
    print(f"\nFortuna:\n{thread_fortuna.result.groupby(['category']).size()}")
    print(f"\nBetFan:\n{thread_betfan.result.groupby(['category']).size()}")
    print(f"\nBetClic:\n{thread_betclic.result.groupby(['category']).size()}")
    print(f"\nTotalBet:\n{thread_totalbet.result.groupby(['category']).size()}")

    # Merge threds outputs
    df = pd.concat([thread_sts.result, thread_lvbet.result, thread_superbet.result, 
                    thread_fuksiarz.result, thread_etoto.result, thread_totolotek.result, 
                    thread_forbet.result, thread_fortuna.result, thread_betfan.result,
                    thread_betclic.result, thread_totalbet.result], ignore_index=True)

    # replace synonyms 
    df = rename_synonyms(df)

    # generate all possible bets combinations
    calculate_bets_outcomes(df, bet_amount, output_path, filename_datetime)


    # save scraped data
    df.to_excel(output_path+filename_datetime+"_scraped.xlsx",
                header=True, index=False)
    
    end_time = time.time()
    execution_time = end_time - start_time

    print("\nExecution time:", round(execution_time, 2), "seconds")