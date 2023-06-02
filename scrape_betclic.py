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


def scrape_betclic() -> pd.DataFrame():

    # ligii polskie
    urls = ['https://www.betclic.pl/pilka-nozna-s1/polska-1-liga-c1749',
            'https://www.betclic.pl/pilka-nozna-s1/polska-2-liga-c2836',
            'https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-2-c22093',
            'https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-1-c22012',
            'https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-podkarpacka-c25999',
            'https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-zachodniopomorska-c26010',
            'https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-3-c22107',
            'https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-4-c21798',
            'https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-kujawsko-pomorska-c25994',
            'https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-swietokrzyska-c26007']
    
    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url"]
    
    #   chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    for url in urls:
        # load page
        driver.get(url)     

        # get table elements of every polish football league (on the same page)
        table_elements = driver.find_elements(By.XPATH, '/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/div[3]/sports-events-list/bcdk-vertical-scroller/div/div[2]/div/div/div[*]/div[2]/sports-events-event[*]')
                                                         
        for table_element in table_elements:
            item = table_element.text.split("\n")
            stakes = list(filter(lambda x: x.replace(",", "").isnumeric(), item))
            
            # if invalid data - skip 
            if len(item) < 11 or len(stakes) != 3:
                print("BetClic: Error appending - " + " | ".join(item))
                continue

            # append item
            dct = {"team_1": item[3],
                   "team_2": item[5],
                   "stake_1_wins": stakes[0].replace(",", "."),
                   "stake_draw": stakes[1].replace(",", "."),
                   "stake_2_wins": stakes[2].replace(",", "."),
                   "url": url}
            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()
    return df


# # test
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]



# df = pd.DataFrame()
# df = df._append(scrape_betclic(), ignore_index=True)
# print(df.head())
