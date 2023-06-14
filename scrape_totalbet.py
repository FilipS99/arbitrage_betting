from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time

from additional_functions import scroll_into_view, get_closest_week_day

def scrape_totalbet() -> pd.DataFrame():
    # ligii polskie
    links = [
                ('https://totalbet.pl/sports/events/MMA-i-Kickboxing/41852,41920,42019,42036,42091/41', 'ufc', 'two-way'),
                ('https://totalbet.pl/sports/events/Pilka-nozna/7488,7486,7489,12232,13951,13952,14272,39304,39305,39308,39309,39310,39311,39312,39313,39314,39315,39316,39317,39318,39319,39320,39321,41738,41739/1', 'polish football', 'three-way'),
                ('https://totalbet.pl/sports/events/Pilka-nozna/7269,7270,7272,7273,7274/1', 'finnish football', 'three-way'),
                ('https://totalbet.pl/sports/events/Rugby/6631,6632,6634,6637,6650,6651,6652,30191/12', 'rugby', 'three-way'),
                ('https://totalbet.pl/sports/events/Pilka-nozna/7331,7342,7344,7351,7353,29269/1', 'brazilian football', 'three-way')
            ]
    
    # initialize output DataFrame
    columns = ["game_datetime", "team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url", "category"]
    df = pd.DataFrame({}, columns=columns)
    
    #   chrome driver setup
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
        elements = driver.find_elements(By.XPATH, '/html/body/div[*]/div[2]/div[3]/div/div/div[3]/partial[3]/div/div/div/div[2]/div[2]/div[*]/ul/li[*]/ul/li')
                                                         
        for index, element in enumerate(elements):
            scroll_into_view(driver, elements[min(index+5, len(elements)-1)], sleep=0)
            
            item = element.text.split("\n")
            if item[0] == '':
                continue
            teams = item[2].split(" - ")

            # set game datetime
            game_datetime = (get_closest_week_day(item[0]) + ' ' + item[1]).replace('.','-')

            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 5 or len(teams) != 2 or not item[3].replace(".", "").isnumeric() or not item[4].replace(".", "").isnumeric():
                    print("TotalBet: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": game_datetime, 
                    "team_1": teams[0],
                    "team_2": teams[1],
                    "stake_1_wins": item[3],
                    "stake_draw": np.inf,
                    "stake_2_wins": item[4],
                    "url": url,
                    "category": category}
            
            elif bet_outcomes == 'three-way': 
                # if invalid data - skip 
                if len(item) < 5 or len(teams) != 2 or not item[3].replace(".", "").isnumeric() or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                    print("TotalBet: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": game_datetime, 
                    "team_1": teams[0],
                    "team_2": teams[1],
                    "stake_1_wins": item[3],
                    "stake_draw": item[4],
                    "stake_2_wins": item[5],
                    "url": url,
                    "category": category}

            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()
    return df


# # test

# df = pd.DataFrame()
# df = df._append(scrape_totalbet(), ignore_index=True)
# print(df.head())

