from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time

from additional_functions import scroll_into_view, get_closest_week_day, format_date_with_zeros

def scrape_superbet() -> pd.DataFrame():
    # SUPERBET
    links = [
                ('https://superbet.pl/zaklady-bukmacherskie/sporty-walki/ufc', 'ufc', 'two-way'),
                ('https://superbet.pl/zaklady-bukmacherskie/pilka-nozna/polska/', 'polish football', 'three-way'),
                ('https://superbet.pl/zaklady-bukmacherskie/pilka-nozna/finlandia', 'finnish football', 'three-way'),
                ('https://superbet.pl/zaklady-bukmacherskie/rugby', 'rugby', 'three-way'),
                ('https://superbet.pl/zaklady-bukmacherskie/pilka-nozna/brazylia', 'brazilian football', 'three-way')
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
                        By.CLASS_NAME, 'event-row__layout')
        
        
        for index, element in enumerate(elements):
            scroll_into_view(driver, elements[min(index+5, len(elements)-1)], sleep=0.1)

            # split row into seperate items  
            item = element.text.split("\n")
            # ['SOB.', '17:30', 'Niepołomice', 'Głogów', '2448', '1.47', '1.47', '4.50', '4.50', '6.50', '6.50', '+129']

            # get game datetime
            game_datetime = format_date_with_zeros((get_closest_week_day(item[0]) + ' ' + item[1]).replace('.','-'))
            
            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 8 or not item[5].replace(".", "").isnumeric() or not item[7].replace(".", "").isnumeric():
                    print("SuperBet: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": game_datetime,
                        "team_1": item[2],
                        "team_2": item[3],
                        "stake_1_wins": item[5],
                        "stake_draw": np.inf,
                        "stake_2_wins": item[7],
                        "url": url,
                        "category": category}
            
            elif bet_outcomes == 'three-way': 
                # if invalid data - skip 
                if len(item) < 12 or not item[5].replace(".", "").isnumeric() or not item[7].replace(".", "").isnumeric() or not item[9].replace(".", "").isnumeric():
                    print("SuperBet: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": game_datetime,
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

    # print(f"{'Superbet:':<10} {len(df)}")

    return df


# # # test

# df = pd.DataFrame()
# df = df._append(scrape_superbet(), ignore_index=True)
# print(df.head())
