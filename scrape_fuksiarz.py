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


def scrape_fuksiarz() -> pd.DataFrame():
    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    # polska liga 1
    url = 'https://fuksiarz.pl/zaklady-bukmacherskie/pilka-nozna/polska/1-liga-polska,3-liga-gr-i,2-liga-polska,3-liga-gr-ii,3-liga-gr-iii,3-liga-gr-iv,4-liga,regionalny-puchar-polski/517,602,537,594,575,597,1294,179592/1'

    # load page
    driver.get(url)

    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
               "stake_draw", "stake_2_wins", "url"]

    # scrape rows
    table_elements = driver.find_elements(
                    By.CLASS_NAME, 'eventListLeagueEventsListPartial')
    
    for table_element in table_elements:
        # split row into seperate items  
        split_list = table_element.text.split("\n")
        items = [split_list[i:i+7] for i in range(0, len(split_list), 7)]

        for item in items:
            teams = item[2].split("-")
            
            # if invalid data - skip 
            if len(teams)!=2 or not item[3].replace(".", "").isnumeric() or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                print("Fuksiarz: Error appending - " + " | ".join(item))
                continue

            # append item
            dct = {"team_1": teams[0],
                    "team_2": teams[1],
                    "stake_1_wins": item[3],
                    "stake_draw": item[4],
                    "stake_2_wins": item[5],
                    "url": url}
            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    print(f"{'Fuksiarz:':<10} {len(df)}")

    return df


# # # test
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

df = pd.DataFrame()
df = df._append(scrape_fuksiarz(), ignore_index=True)
print(df.head())

