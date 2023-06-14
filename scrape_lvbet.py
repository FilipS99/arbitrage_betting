from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
from datetime import datetime

from additional_functions import scroll_into_view


def scrape_lvbet() -> pd.DataFrame():
    # lvbet polska piłka nożna
    links = [
                ('https://lvbet.pl/pl/zaklady-bukmacherskie/multiple--?leagues=20773', 'ufc', 'two-way'),
                ('https://lvbet.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/--/1/35381/', 'polish football', 'three-way'),
                ('https://lvbet.pl/pl/zaklady-bukmacherskie/multiple--?leagues=37529,37532,37533', 'finnish football', 'three-way'),
                ('https://lvbet.pl/pl/zaklady-bukmacherskie/multiple--?leagues=21996,21985,21995,22043,22058', 'rugby', 'three-way'),
                ('https://lvbet.pl/pl/zaklady-bukmacherskie/multiple--?leagues=37606,37307,37267,36685,36851,36582,35954,72296,72500', 'brazilian football', 'three-way')
            ]

    # initialize output DataFrame
    columns = ["game_datetime", "team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url", "category"]
    df = pd.DataFrame({}, columns=columns)
    
    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
           
    for link in links:
        # unpack tuple
        url, category, bet_outcomes = link

        # load page
        driver.get(url)

        # in case of 'stale' elements
        time.sleep(3)

        # get table elements of every polish football league (on the same page)
        elements = driver.find_elements(
                        By.CLASS_NAME, 'odds-table__entry')

        for index, element in enumerate(elements):
            scroll_into_view(driver, elements[min(index+5, len(elements)-1)], sleep=0)

            # split row into seperate items  
            item = element.text.split("\n") 
            
            # remove redundant elements
            patterns = ['betbuilder']
            item = [x for x in item if all(pattern not in x for pattern in patterns)]

            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 7 or not item[4].replace(".", "").isnumeric() or not item[6].replace(".", "").isnumeric():
                    print("LvBet: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": (item[1] + ' ' + item[0]).replace('.','-'),
                       "team_1": item[2],
                       "team_2": item[3],
                       "stake_1_wins": item[4],
                       "stake_draw": np.inf,
                       "stake_2_wins": item[6],
                       "url": url,
                       "category": category
                       }
                
            
            elif bet_outcomes == 'three-way': 
                # if invalid data - skip 
                if len(item) < 7 or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric() or not item[6].replace(".", "").isnumeric():
                    print("LvBet: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": (item[1] + ' ' + item[0]).replace('.','-'),
                       "team_1": item[2],
                       "team_2": item[3],
                       "stake_1_wins": item[4],
                       "stake_draw": item[5],
                       "stake_2_wins": item[6],
                       "url": url,
                       "category": category
                       }

            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    return df


# # # test

# df = pd.DataFrame()
# df = df._append(scrape_lvbet(), ignore_index=True)
# print(df.head())

