from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
from datetime import date
import re
from typing import Tuple

from additional_functions import scroll_into_view


def scrape_forbet() -> Tuple[pd.DataFrame, list]:
    # links
    links = [
        ('https://www.iforbet.pl/zaklady-bukmacherskie/5', 'tennis', 'two-way'),
        ('https://www.iforbet.pl/zaklady-bukmacherskie/30290', 'ufc', 'two-way'),
        ('https://www.iforbet.pl/zaklady-bukmacherskie/320',
         'polish football', 'three-way'),
        ('https://www.iforbet.pl/zaklady-bukmacherskie/139',
         'finnish football', 'three-way'),
        ('https://www.iforbet.pl/zaklady-bukmacherskie/12', 'rugby', 'three-way'),
        ('https://www.iforbet.pl/zaklady-bukmacherskie/436',
         'brazilian football', 'three-way')
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
    driver.implicitly_wait(1)

    for link in links:
        # unpack tuple
        url, category, bet_outcomes = link

        # load page
        driver.get(url)

        # in case of 'stale' elements
        time.sleep(3)

        # Get the current URL, skip if redirectred
        if url != driver.current_url:
            errors.append("ForBet: URL Redirected to: " + driver.current_url)
            continue

        # scrape sections
        sections = driver.find_elements(
            By.XPATH, '/html/body/div[*]/div/div/main/div[*]/div/div/div/div[1]/section/div/section[*]/div/section')

        for section in sections:
            scroll_into_view(driver, section, sleep=0)

            # set event date
            events_date = section.text.split('\n')[0].split(', ')[
                1].replace('.', '-')

            # get elements
            elements = section.find_elements(By.XPATH, './div[*]')

            for element in elements:
                scroll_into_view(driver, element, sleep=0)

                item = element.text.split('\n')
                teams = item[1].split(' - ')

                # remove random value
                while 'BETARCHITEKT' in item:
                    item.remove('BETARCHITEKT')

                # set game datetime
                if len(item) > 0:
                    game_datetime = events_date + ' ' + item[0]

                    # continue if gametime doesnt match regex
                    date_pattern = r"\d{2}-\d{2} \d{2}:\d{2}"
                    if not re.match(date_pattern, game_datetime):
                        errors.append(
                            "ForBet: Datetime error: " + game_datetime)
                        continue

                if bet_outcomes == 'two-way':
                    # if invalid data - skip
                    if len(item) < 5 or len(teams) != 2 or not item[2].replace(".", "").isnumeric() or not item[3].replace(".", "").isnumeric():
                        errors.append(
                            "ForBet: Error appending - " + " | ".join(item))
                        continue

                    # append item
                    dct = {"game_datetime": game_datetime,
                           "team_1": teams[0],
                           "team_2": teams[1],
                           "stake_1_wins": item[2],
                           "stake_draw": np.inf,
                           "stake_2_wins": item[3],
                           "url": url,
                           "category": category
                           }

                elif bet_outcomes == 'three-way':
                    # if invalid data - skip
                    if len(item) < 6 or len(teams) != 2 or not item[2].replace(".", "").isnumeric() or not item[3].replace(".", "").isnumeric() or not item[4].replace(".", "").isnumeric():
                        errors.append(
                            "ForBet: Error appending - " + " | ".join(item))
                        continue

                    # append item
                    dct = {"game_datetime": game_datetime,
                           "team_1": teams[0],
                           "team_2": teams[1],
                           "stake_1_wins": item[2],
                           "stake_draw": item[3],
                           "stake_2_wins": item[4],
                           "url": url,
                           "category": category
                           }

                df = df._append(pd.DataFrame(
                    [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    return df, errors


# # # test

# df = pd.DataFrame()
# df, errors = scrape_forbet()
# print(errors)
# print(len(df))