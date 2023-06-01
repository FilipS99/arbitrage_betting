import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import pandas as pd
import time


def scrape_fuksiarz() -> pd.DataFrame():
    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    # lvbet polska piłka nożna
    url = 'https://fuksiarz.pl/zaklady-bukmacherskie/pilka-nozna/polska/1-liga-polska,3-liga-gr-i,2-liga-polska,3-liga-gr-ii,3-liga-gr-iii,3-liga-gr-iv,4-liga,regionalny-puchar-polski/517,602,537,594,575,597,1294,179592/1'
           
    # load page
    driver.get(url)

    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
               "stake_draw", "stake_2_wins", "url"]

    # Locate the specific sections
    section_elements = driver.find_elements(By.XPATH, '//*[@class="list-unstyled single-events"]')

    section_counter = 0
    for section_element in section_elements:
        # Get initial element position
        initial_position = section_element.location["y"]

        # Scroll loop - until end of element is visible
        while True:
            # Scroll to the element's bottom position
            driver.execute_script("arguments[0].scrollIntoView(false);", section_element)
            
            # Wait for a short interval to allow content to load
            time.sleep(0.5)
            
            # Calculate the new element position after scrolling
            new_position = section_element.location["y"]
            
            # Break the loop if the element's position remains the same (reached the bottom)
            if new_position == initial_position:
                break
            
            # Update the last recorded position
            initial_position = new_position

        # get section elements 
        section_counter += 3
        elements = section_element.find_elements(By.XPATH, f'/html/body/div[3]/div[2]/div[1]/div[2]/div[3]/div/div/div[3]/partial[3]/div/div/div/div[2]/div[2]/div[{section_counter}]/ul/li[*]/ul/li') 

        for element in elements:
            item = element.text.split('\n')
            teams = item[2].split(' - ')
            
            # if invalid data - skip 
            if len(item) < 6 or len(teams) != 2 or not item[3].replace(".", "").isnumeric() or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
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

    # print(f"{'Fuksiarz:':<10} {len(df)}")

    return df


# # # test
# # # expected columns
# # # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]

# df = pd.DataFrame()
# df = df._append(scrape_fuksiarz(), ignore_index=True)
# print(df.head())
