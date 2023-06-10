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

    # Define the list of threads
    threads = [ 
                'thread_sts', 'thread_betclic', 'thread_lvbet', 'thread_fortuna',  
                'thread_superbet', 'thread_fuksiarz', 'thread_etoto', 'thread_totolotek', 
                'thread_forbet', 'thread_betfan', 'thread_totalbet' 
              ]
    
    
    # start threads with delay
    for thread in threads:
        globals()[thread].start()
        time.sleep(3)

    # join threads 
    for thread in threads:
        globals()[thread].join()

    print("\n-----------------------------------\n")
    print("All threads have finished executing")

    category_size_per_page = pd.DataFrame({})

    # Iterate over the threads, print and append the results
    for thread in threads:
        result = globals()[thread].result
        if not isinstance(result, pd.DataFrame):
            print(f"\n{thread.capitalize()}: CRITICAL ERROR")
        else:
            # append category_size_per_page
            category_size_per_page[thread] = result.groupby(['category']).size()

            # append main data DataFrame
            df = pd.concat([df, result])

    # print category_size_per_page
    print(category_size_per_page)

    # replace synonyms 
    df = rename_synonyms(df)

    # sorting
    df = df.sort_values(by=['category', 'team_1', 'team_2'], ascending=[True, True, True])
 
    # generate all possible bets combinations
    calculate_bets_outcomes(df, bet_amount, output_path, filename_datetime)


    # save scraped data
    df.to_excel(output_path+filename_datetime+"_scraped.xlsx",
                header=True, index=False)
    
    end_time = time.time()
    execution_time = end_time - start_time

    print("\nExecution time:", round(execution_time, 2), "seconds")