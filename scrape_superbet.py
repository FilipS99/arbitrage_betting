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
        
        # get table elements of every polish football league (on the same page)
        table_elements = driver.find_elements(
                        By.CLASS_NAME, 'event-row__layout')
        
        
        for table_element in table_elements:
            # Get initial element position
            initial_position = table_element.location["y"]

            # Scroll loop - until element is visible
            while True:
                # Scroll to the element's bottom position
                driver.execute_script("arguments[0].scrollIntoView(false);", table_element)
                
                # Wait for a short interval to allow content to load
                # time.sleep(0.1)
                
                # Calculate the new element position after scrolling
                new_position = table_element.location["y"]
                
                # Break the loop if the element's position remains the same (reached the bottom)
                if new_position == initial_position:
                    break
                
                # Update the last recorded position
                initial_position = new_position

            # split row into seperate items  
            item = table_element.text.split("\n")
            # ['SOB.', '17:30', 'Niepołomice', 'Głogów', '2448', '1.47', '1.47', '4.50', '4.50', '6.50', '6.50', '+129']
            
            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 8 or not item[5].replace(".", "").isnumeric() or not item[7].replace(".", "").isnumeric():
                    print("SuperBet: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"team_1": item[2],
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
                dct = {"team_1": item[2],
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
