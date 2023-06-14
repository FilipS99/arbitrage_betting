from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
import re
from typing import Tuple

from additional_functions import scroll_into_view

def scrape_totolotek() -> Tuple[pd.DataFrame, list]:    
    # totolotek 1 liga
    links = [
                ('https://www.totolotek.pl/pl/mma', 'ufc', 'two-way'),
                ('https://www.totolotek.pl/pl/pilka-nozna/polska', 'polish football', 'three-way'),
                ('https://www.totolotek.pl/pl/pilka-nozna/finlandia', 'finnish football', 'three-way'),
                ('https://www.totolotek.pl/pl/rugby', 'rugby', 'three-way'),
                ('https://www.totolotek.pl/pl/pilka-nozna/brazylia', 'brazilian football', 'three-way')
            ]

    # initialize output DataFrame
    columns = ["game_datetime", "team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url", "category"]
    df = pd.DataFrame({}, columns=columns)
    errors = []

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

        # Get the current URL, skip if redirectred
        if url != driver.current_url:
            errors.append("Totolotek: URL Redirected to: " + driver.current_url)
            continue

        # find elements until each is loaded
        last_elements_count = 0
        current_elements_count = -1       
        while last_elements_count != current_elements_count:
            last_elements_count = current_elements_count
            # get table elements of every league (on the same page)
            elements = driver.find_elements(
                        By.XPATH, '/html/body/app-root/div/web-layout/div[1]/div/section/div/home-page/section/div/games-list/div/gamelist/div/div/div[*]/game/div')
            current_elements_count = len(elements)
            
            if current_elements_count > 0:
                # scroll to last loaded element
                driver.execute_script("arguments[0].scrollIntoView(false);", elements[-1])
        
        for index, element in enumerate(elements):
            scroll_into_view(driver, elements[min(index+5, len(elements)-1)], sleep=0)

            # split row into seperate items  
            item = element.text.split("\n")

            if len(item) > 4:
                # set game datetime
                game_datetime = (item[2][-5:] + ' ' + item[3]).replace('.','-')

                # continue if gametime doesnt match regex
                date_pattern = r"\d{2}-\d{2} \d{2}:\d{2}"
                if not re.match(date_pattern, game_datetime):
                    errors.append("Totolotek: Datetime error: " + game_datetime)
                    continue
            
            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 8 or not item[5].replace(".", "").isnumeric() or not item[7].replace(".", "").isnumeric():
                    errors.append("Totolotek: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": game_datetime,
                    "team_1": item[0],
                    "team_2": item[1],
                    "stake_1_wins": item[5],
                    "stake_draw": np.inf,
                    "stake_2_wins": item[7],
                    "url": url,
                    "category": category}
            
            elif bet_outcomes == 'three-way': 
                # if invalid data - skip 
                if len(item) < 10 or not item[5].replace(".", "").isnumeric() or not item[7].replace(".", "").isnumeric() or not item[9].replace(".", "").isnumeric():
                    errors.append("Totolotek: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": game_datetime,
                    "team_1": item[0],
                    "team_2": item[1],
                    "stake_1_wins": item[5],
                    "stake_draw": item[7],
                    "stake_2_wins": item[9],
                    "url": url,
                    "category": category}

            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    # print(f"{'Totolotek:':<10} {len(df)}")

    return df, errors


# test

# df = pd.DataFrame()
# df = df._append(scrape_totolotek(), ignore_index=True)
# print(df.head())