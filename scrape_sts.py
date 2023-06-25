from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
import re
from typing import Tuple

from additional_functions import scroll_into_view


def scrape_sts() -> Tuple[pd.DataFrame, list]:
    links = [
                ('https://www.sts.pl/pl/zaklady-bukmacherskie/sporty-walki/mma/ufc/211/6594/84954/', 'ufc', 'two-way'),
                ('https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/184/30860/', 'polish football', 'three-way'),
                ('https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/finlandia/184/30891/', 'finnish football', 'three-way'),
                ('https://www.sts.pl/pl/zaklady-bukmacherskie/rugby/rugby-league/195/31059/', 'rugby', 'three-way'),
                ('https://www.sts.pl/pl/zaklady-bukmacherskie/rugby/rugby-union/195/31057/', 'rugby', 'three-way'),
                ('https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/brazylia/184/30863/', 'brazilian football', 'three-way'),
                ('https://www.sts.pl/pl/zaklady-bukmacherskie/tenis/185/', 'tennis', 'two-way')
            ]
    
    # initialize output DataFrame
    columns = ["game_datetime", "team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url", "category"]
    df = pd.DataFrame({}, columns=columns)
    errors = []
    
    # Chrome instance in nested, since STS blocks quick page changes with Captcha
    for link in links:
        # unpack tuple
        url, category, bet_outcomes = link

        # chrome driver setup
        options = Options()
        # options.add_argument("--headless")  # opens in background
        options.add_argument("--start-maximized")
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(options=options)
        # driver.implicitly_wait(3)

        # load page
        driver.get(url)     
        
        # in case of 'stale' elements
        time.sleep(3)

        # Get the current URL, skip if redirectred
        if url != driver.current_url:
            errors.append("STS: URL Redirected to: " + driver.current_url)
            continue

        # get table elements of every polish football league (on the same page)
        elements = driver.find_elements(By.XPATH, '/html/body/div[5]/div[2]/div[6]/div[5]/div[2]/div/div/table[*]')

        for index, element in enumerate(elements):
            scroll_into_view(driver, elements[min(index+5, len(elements)-1)], sleep=0)

            # set current section date (inherit previous date if doesnt exist)
            event_date_element = element.find_elements(By.XPATH, './thead')
            event_date = event_date_element[0].text[-10:-5] if len(event_date_element) else event_date

            # get elements time class text
            event_time = element.find_element(By.XPATH, ".//*[contains(@class, 'date_time')]").text
            
            item = element.find_element(By.XPATH, "./tbody/tr/td[2]/table/tbody").text.split("\n")

            # set game datetime
            game_datetime = (event_date + ' ' + event_time).replace('.','-')

            # continue if gametime doesnt match regex
            date_pattern = r"\d{2}-\d{2} \d{2}:\d{2}"
            if not re.match(date_pattern, game_datetime):
                errors.append("STS: Datetime error: " + game_datetime)
                continue


            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 4 or not item[1].replace(".", "").isnumeric() or not item[3].replace(".", "").isnumeric():
                    if item[0] != '':
                        errors.append("STS: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": game_datetime, 
                       "team_1": item[0],
                       "team_2": item[2],
                       "stake_1_wins": item[1],
                       "stake_draw": np.inf,
                       "stake_2_wins": item[3],
                       "url": url,
                       "category": category
                       }
            
            elif bet_outcomes == 'three-way': 
                # if invalid data - skip 
                if len(item) < 6 or not item[1].replace(".", "").isnumeric() or not item[3].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                    if item[0] != '':
                        errors.append("STS: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": game_datetime,
                       "team_1": item[0],
                       "team_2": item[4],
                       "stake_1_wins": item[1],
                       "stake_draw": item[3],
                       "stake_2_wins": item[5],
                       "url": url,
                       "category": category
                       }

            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

        # close chrome
        driver.quit()

    return df, errors


# # test

# df = pd.DataFrame()
# df = df._append(scrape_sts(), ignore_index=True)
# print(df.head())

