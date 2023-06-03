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


def scrape_totalbet() -> pd.DataFrame():
    # ligii polskie
    links = [('https://totalbet.pl/sports/events/Pilka-nozna/7486,7489,12232,13951,13952,14272,39304,39305,39308,39309,39310,39311,39312,39313,39314,39315,39316,39317,39318,39319,39320,39321,41738,41739/1', 'polish football'),
             ('https://totalbet.pl/sports/events/Pilka-nozna/7269,7270,7272,7273,7274/1', 'finland football')]
    
    # initialize output DataFrame
    columns = ["team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url", "category"]
    df = pd.DataFrame({}, columns=columns)
    
    #   chrome driver setup
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
        table_elements = driver.find_elements(By.XPATH, '/html/body/div[*]/div[2]/div[3]/div/div/div[3]/partial[3]/div/div/div/div[2]/div[2]/div[*]/ul/li[*]/ul/li')
                                                         
        for table_element in table_elements:
            # Get initial element position
            initial_position = table_element.location["y"]
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

            item = table_element.text.split("\n")
            if item[0] == '':
                continue
            teams = item[2].split(" - ")
        
            # if invalid data - skip 
            if len(item) < 5 or len(teams) != 2 or not item[3].replace(".", "").isnumeric() or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                print("TotalBet: Error appending - " + " | ".join(item))
                continue

            # append item
            dct = {"team_1": teams[0],
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

