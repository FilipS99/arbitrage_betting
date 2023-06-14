from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta

from additional_functions import scroll_into_view


def scrape_betfan() -> pd.DataFrame():
    # links
    links = [
                ('https://betfan.pl/lista-zakladow/pilka-nozna/polska/245', 'polish football', 'three-way'),
                ('https://betfan.pl/lista-zakladow/pilka-nozna/finlandia/856', 'finnish football', 'three-way'),
                ('https://betfan.pl/lista-zakladow/rugby/rugby-league/991', 'rugby', 'three-way'),
                ('https://betfan.pl/lista-zakladow/rugby/rugby-union/674', 'rugby', 'three-way'),
                ('https://betfan.pl/lista-zakladow/pilka-nozna/brazylia/240', 'brazilian football', 'three-way'),
                ('https://betfan.pl/lista-zakladow/mma/ufc/1489', 'ufc', 'two-way'),
                ('https://betfan.pl/lista-zakladow/mma/ufc/1489', 'ufc', 'two-way')
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

        # scrape rows
        elements = driver.find_elements(By.XPATH,'/html/body/div[1]/div[2]/main/div[3]/div/div[*]/div[2]/div[*]') 

        for index, element in enumerate(elements):
            scroll_into_view(driver, elements[min(index+5, len(elements)-1)], sleep=0)

            item = element.text.split('\n')

            if len(item) > 1:
                # Get current date
                current_date = datetime.now().strftime("%d.%m.%Y ")

                # Get tomorrow's date
                tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y ")

                # Replace "today" and "tomorrow" with their respective dates
                item[1] = item[1].replace('Jutro', tomorrow_date).replace('Dziś', current_date)
            
            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 8 or not item[5].replace(".", "").isnumeric() or not item[7].replace(".", "").isnumeric():
                    if item[0] == '':
                        continue
                    print("BetFan: Error appending - " + " | ".join(item))
                    continue
                
                # append item
                dct = {
                    "game_datetime": datetime.strptime(item[1], "%d.%m.%Y %H:%M").strftime("%d-%m %H:%M"),
                    "team_1": item[2],
                    "team_2": item[3],
                    "stake_1_wins": item[5],
                    "stake_draw": np.inf,
                    "stake_2_wins": item[7],
                    "url": url,
                    "category": category}
                
            elif bet_outcomes == 'three-way':
                # if invalid data - skip 
                if len(item) < 9 or not item[5].replace(".", "").isnumeric() or not item[7].replace(".", "").isnumeric() or not item[9].replace(".", "").isnumeric():
                    if item[0] == '':
                        continue
                    print("BetFan: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {
                    "game_datetime": datetime.strptime(item[1], "%d.%m.%Y %H:%M").strftime("%d-%m %H:%M"),
                    "team_1": item[2],
                    "team_2": item[3],
                    "stake_1_wins": item[5],
                    "stake_draw": item[7],
                    "stake_2_wins": item[9],
                    "url": url,
                    "category": category}


            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    return df


# # # test
# df = pd.DataFrame()
# df = df._append(scrape_betfan(), ignore_index=True)
# print(df.head())
