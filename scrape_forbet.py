from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
from datetime import datetime, date

from additional_functions import scroll_into_view

def scrape_forbet() -> pd.DataFrame():
    # links
    links = [
                ('https://www.iforbet.pl/zaklady-bukmacherskie/30290', 'ufc', 'two-way'),
                ('https://www.iforbet.pl/zaklady-bukmacherskie/320', 'polish football', 'three-way'),
                ('https://www.iforbet.pl/zaklady-bukmacherskie/139', 'finnish football', 'three-way'),
                ('https://www.iforbet.pl/zaklady-bukmacherskie/12', 'rugby', 'three-way'),
                ('https://www.iforbet.pl/zaklady-bukmacherskie/436', 'brazilian football', 'three-way')
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
        
        # scrape sections 
        sections = driver.find_elements(By.XPATH,'/html/body/div[1]/div/div/main/div[2]/div/div/div/div[1]/section/div/section[*]/div/section') 

        for section in sections:
            scroll_into_view(driver, section, sleep=0)

            # set event date 
            events_date = section.text.split('\n')[0].split(', ')[1].replace('.', '-') + '-' + str(date.today().year)

            # get elements
            elements = section.find_elements(By.XPATH, './div[*]') 
                                                                    
            for element in elements:
                scroll_into_view(driver, element, sleep=0.1)
                
                item = element.text.split('\n')[1:]
                teams = item[0].split(' - ')

                # remove random value
                while 'BETARCHITEKT' in item:
                    item.remove('BETARCHITEKT')
                
                if bet_outcomes == 'two-way':
                    # if invalid data - skip 
                    if len(item) < 4 or len(teams) != 2 or not item[1].replace(".", "").isnumeric() or not item[2].replace(".", "").isnumeric():
                        print("ForBet: Error appending - " + " | ".join(item))
                        continue

                    # append item
                    dct = {"game_datetime": events_date + ' ' + item[0],
                           "team_1": teams[0],
                           "team_2": teams[1],
                           "stake_1_wins": item[1],
                           "stake_draw": np.inf,
                           "stake_2_wins": item[2],
                           "url": url,
                           "category": category
                        }
                
                elif bet_outcomes == 'three-way':
                    # if invalid data - skip 
                    if len(item) < 5 or len(teams) != 2 or not item[1].replace(".", "").isnumeric() or not item[2].replace(".", "").isnumeric() or not item[3].replace(".", "").isnumeric():
                        print("ForBet: Error appending - " + " | ".join(item))
                        continue

                    # append item
                    dct = {"game_datetime": events_date + ' ' + item[0],
                           "team_1": teams[0],
                           "team_2": teams[1],
                           "stake_1_wins": item[1],
                           "stake_draw": item[2],
                           "stake_2_wins": item[3],
                           "url": url,
                           "category": category
                        }
                        
                df = df._append(pd.DataFrame(
                    [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    # print(f"{'ForBet:':<10} {len(df)}")

    return df


# # # test

# df = pd.DataFrame()
# df = df._append(scrape_forbet(), ignore_index=True)
print(df.head())

