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
    # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

    # Create thread objects for each function
    thread1 = ScrapeThread(target_func=scrape_sts)
    thread2 = ScrapeThread(target_func=scrape_lvbet)
    thread3 = ScrapeThread(target_func=scrape_superbet)
    thread4 = ScrapeThread(target_func=scrape_fuksiarz)
    thread5 = ScrapeThread(target_func=scrape_etoto)
    thread6 = ScrapeThread(target_func=scrape_totolotek)
    thread7 = ScrapeThread(target_func=scrape_forbet)
    thread8 = ScrapeThread(target_func=scrape_fortuna)
    thread9 = ScrapeThread(target_func=scrape_betfan)

    # sts/lvbet taking longest
    thread1.start()
    thread2.start()

    thread3.start()
    thread4.start()
    thread5.start()

    thread3.join()
    thread4.join()
    thread5.join()

    thread6.start()
    thread7.start()
    thread8.start()

    thread6.join()
    thread7.join()
    thread8.join()
    
    thread9.start()

    thread9.join()

    # sts/lvbet taking longest
    thread1.join()
    thread2.join()

    print("\n-----------------------------------\n")
    print("All threads have finished executing")
    print(f"{'STS:':<10} {len(thread1.result)}")
    print(f"{'Lvbet:':<10} {len(thread2.result)}")
    print(f"{'Superbet:':<10} {len(thread3.result)}")
    print(f"{'Fuksiarz:':<10} {len(thread4.result)}")
    print(f"{'Etoto:':<10} {len(thread5.result)}")
    print(f"{'Totolotek:':<10} {len(thread6.result)}")
    print(f"{'ForBet:':<10} {len(thread7.result)}")
    print(f"{'Fortuna:':<10} {len(thread8.result)}")
    print(f"{'BetFan:':<10} {len(thread9.result)}")

    # Merge threds outputs
    df = pd.concat([thread1.result, thread2.result, thread3.result, 
                    thread4.result, thread5.result, thread6.result, 
                    thread7.result, thread8.result, thread9.result], ignore_index=True)

    # replace synonyms 
    df = rename_synonyms(df)

    # generate all possible bets combinations
    calculate_bets_outcomes(df, bet_amount, output_path, filename_datetime)

    # save scraped data
    df.to_excel(output_path+filename_datetime+"_scraped.xlsx",
                header=True, index=False)
    
    end_time = time.time()
    execution_time = end_time - start_time

    print("Execution time:", round(execution_time, 2), "seconds")