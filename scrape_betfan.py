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
    columns = ["team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url", "category"]
    df = pd.DataFrame({}, columns=columns)
    
    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    for link in links:
        # unpack tuple
        url, category, bet_outcomes = link

        # load page
        driver.get(url)
        
        # in case of 'stale' elements
        time.sleep(3)

        # scrape rows
        elements = driver.find_elements(By.XPATH,'/html/body/div[1]/div[2]/main/div[3]/div/div[*]/div[2]/div[*]/div/div[2]') 

        for element in elements:
            # Get initial element position
            initial_position = element.location["y"]

            # Scroll loop - until element is visible
            while True:
                # Scroll to the element's bottom position
                driver.execute_script("arguments[0].scrollIntoView(false);", element)
                
                # Wait for a short interval to allow content to load
                # time.sleep(0.1)
                
                # Calculate the new element position after scrolling
                new_position = element.location["y"]
                
                # Break the loop if the element's position remains the same (reached the bottom)
                if new_position == initial_position:
                    break
                
                # Update the last recorded position
                initial_position = new_position

            item = element.text.split('\n')
            # ['Stal Rzeszów', 'Skra Częstochowa', 'Stal Rzeszów', '1.50', 'Remis', '4.50', 'Skra Częstochowa', '6.20', '+140']
            
            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 7 or not item[3].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                    if item[0] == '':
                        continue
                    print("BetFan: Error appending - " + " | ".join(item))
                    continue
                
                # append item
                dct = {"team_1": item[0],
                    "team_2": item[1],
                    "stake_1_wins": item[3],
                    "stake_draw": np.inf,
                    "stake_2_wins": item[5],
                    "url": url,
                    "category": category}
                
            elif bet_outcomes == 'three-way':
                # if invalid data - skip 
                if len(item) < 7 or not item[3].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric() or not item[7].replace(".", "").isnumeric():
                    if item[0] == '':
                        continue
                    print("BetFan: Error appending - " + " | ".join(item))
                    continue
                
                # append item
                dct = {"team_1": item[0],
                    "team_2": item[1],
                    "stake_1_wins": item[3],
                    "stake_draw": item[5],
                    "stake_2_wins": item[7],
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
