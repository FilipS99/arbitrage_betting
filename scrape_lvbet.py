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


def scrape_lvbet() -> pd.DataFrame():
    # lvbet polska piłka nożna
    links = [('https://lvbet.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/--/1/35381/', 'polish football'),
             ('https://lvbet.pl/pl/zaklady-bukmacherskie/multiple--?leagues=37529,37532,37533', 'finland football')]

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
        url, category = link

        # load page
        driver.get(url)

        # in case of 'stale' elements
        time.sleep(3)

        # get table elements of every polish football league (on the same page)
        table_elements = driver.find_elements(
                        By.CLASS_NAME, 'odds-table__entry')

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
            
            # if invalid data - skip 
            if len(item) < 7 or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric() or not item[6].replace(".", "").isnumeric():
                print("LvBet: Error appending - " + " | ".join(item))
                continue

            # append item
            dct = {"team_1": item[2],
                   "team_2": item[3],
                   "stake_1_wins": item[4],
                   "stake_draw": item[5],
                   "stake_2_wins": item[6],
                   "url": url,
                   "category": category}
            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    return df


# # # test

# df = pd.DataFrame()
# df = df._append(scrape_lvbet(), ignore_index=True)
# print(df.head())

