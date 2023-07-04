from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
from datetime import datetime
import re
from typing import Tuple

from additional_functions import scroll_into_view


def scrape_fuksiarz() -> Tuple[pd.DataFrame, list]:
    # links
    links = [
        ('https://fuksiarz.pl/zaklady-bukmacherskie/tenis/atp/atp-wimbledon,atp-wimbledon-debel/153514,153835/5', 'tennis', 'two-way'),
        ('https://fuksiarz.pl/zaklady-bukmacherskie/tenis/wta/wta-wimbledon,wta-wimbledon-debel/153591,153836/5', 'tennis', 'two-way'),
        ('https://fuksiarz.pl/zaklady-bukmacherskie/tenis/challenger/mediolan,troyes,mediolan-debel,troyes-debel,atp-challenger-karlsruhe-germany-men-double,atp-challenger-karlsruhe-germany-men-singles,atp-challenger-santa-fe-argentina-men-singles,atp-challenger-bloomfield-hills-usa-men-singles/153463,180261,153431,180249,204591,204607,204625,204634/5', 'tennis', 'two-way'),
        ('https://fuksiarz.pl/zaklady-bukmacherskie/tenis/itf-mezczyzni/ajaccio,klosters,casablanca,irvine,alkmaar,wroclaw,santo-domingo,rosario-santa-fe/204631,58045,204256,164434,153981,154018,167048,165926/5', 'tennis', 'two-way'),
        ('https://fuksiarz.pl/zaklady-bukmacherskie/tenis/itf-kobiety/palma-del-rio,perigueux,santo-domingo,klosters,haga,hong-kong,liepaja,montpellier,irvine,rosario-santa-fe/158603,153930,190887,160216,153982,204597,151370,155886,204282,186537/5', 'tennis', 'two-way'),
        ('https://fuksiarz.pl/zaklady-bukmacherskie/mma/ufc/ufc/6657/41',
         'ufc', 'two-way'),
        ('https://fuksiarz.pl/zaklady-bukmacherskie/pilka-nozna/polska/2-liga-polska,1-liga-polska,superpuchar-polski,ekstraklasa/537,517,1319,265/1',
         'polish football', 'three-way'),
        ('https://fuksiarz.pl/zaklady-bukmacherskie/pilka-nozna/finlandia/1-liga,2-liga,3-liga/693,912,144998/1',
         'finnish football', 'three-way'),
        ('https://fuksiarz.pl/zaklady-bukmacherskie/rugby/rugby-league,rugby-union/anglia-super-league,australia-nrl,rfl-championship,puchar-swiata,super-rugby,francja-top-14/1261,585,95327,198619,2375,1785/12', 'rugby', 'three-way'),
        ('https://fuksiarz.pl/zaklady-bukmacherskie/pilka-nozna/brazylia/1-liga,2-liga,3-liga,4-liga,1-liga-(k)/710,749,1324,1816,1640/1',
         'brazilian football', 'three-way')
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
    errors = []

    for link in links:
        # unpack tuple
        url, category, bet_outcomes = link

        # load page
        driver.get(url)

        # in case of 'stale' elements
        time.sleep(3)

        # Get the current URL, skip if redirectred
        if url != driver.current_url:
            errors.append("Fuksiarz: URL Redirected to: " + driver.current_url)
            continue

        elements = driver.find_elements(
            By.XPATH, f'/html/body/div[3]/div[2]/div[1]/div[2]/div[3]/div/div/div[3]/partial[*]/div/div/div/div[2]/div[2]/div[*]/ul/li[*]/ul/li')

        for index, element in enumerate(elements):
            scroll_into_view(driver, elements[min(
                index+5, len(elements)-1)], sleep=0)

            item = element.text.split('\n')
            teams = item[2].split(' - ')

            # set game datetime
            if len(item) > 2:
                game_datetime = (item[1] + ' ' + item[0]).replace('.', '-')

                # continue if gametime doesnt match regex
                date_pattern = r"\d{2}-\d{2} \d{2}:\d{2}"
                if not re.match(date_pattern, game_datetime):
                    errors.append("Fuksiarz: Datetime error: " + game_datetime)
                    continue

            if bet_outcomes == 'two-way':
                # if invalid data - skip
                if len(item) < 6 or len(teams) != 2 or not item[3].replace(".", "").isnumeric() or not item[4].replace(".", "").isnumeric():
                    errors.append(
                        "Fuksiarz: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": game_datetime,
                       "team_1": teams[0],
                       "team_2": teams[1],
                       "stake_1_wins": item[3],
                       "stake_draw": np.inf,
                       "stake_2_wins": item[4],
                       "url": url,
                       "category": category
                       }

            elif bet_outcomes == 'three-way':
                # if invalid data - skip
                if len(item) < 6 or len(teams) != 2 or not item[3].replace(".", "").isnumeric() or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                    errors.append(
                        "Fuksiarz: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"game_datetime": game_datetime,
                       "team_1": teams[0],
                       "team_2": teams[1],
                       "stake_1_wins": item[3],
                       "stake_draw": item[4],
                       "stake_2_wins": item[5],
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
# df = df._append(scrape_fuksiarz(), ignore_index=True)
# print(df.head())
