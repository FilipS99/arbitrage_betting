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


def scrape_fortuna() -> pd.DataFrame():
    # links
    links = [
                ('https://www.efortuna.pl/zaklady-bukmacherskie/mma', 'ufc', 'two-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/fortuna-1-liga-polska', 'polish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/2-polska', 'polish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-polska-grupa-i', 'polish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-polska-grupa-ii', 'polish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-polska-grupa-iii', 'polish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-polska-grupa-iv', 'polish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/1-finlandia', 'finnish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/2-finlandia', 'finnish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-finlandia-a', 'finnish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-finlandia-b', 'finnish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-finlandia-c', 'finnish football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/rugby', 'rugby', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/1-brazylia', 'brazilian football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/1-brazylia-k-', 'brazilian football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/2-brazylia', 'brazilian football', 'three-way'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-brazylia', 'brazilian football', 'three-way')
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
        time.sleep(1)   

        # get table elements (on the same page)
        if bet_outcomes == 'three-way':
            table_elements = driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[2]/div[2]/div/div[3]/div[5]/section/div[2]/div/div/table/tbody/tr[*]')

        elif bet_outcomes == 'two-way':
            table_elements = driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[2]/div[2]/div/div[*]/section[*]/div[2]/div/div/table/tbody/tr[*]')
                                                         

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

            item = table_element.text.split("\n")

            # remove redundant elements
            patterns = ['BetBuilder']
            item = [x for x in item if all(pattern not in x for pattern in patterns)]
            
            try:
                if item[0] != '':
                    teams = table_element.find_element(By.CLASS_NAME, 'market-name').text.split(' - ')
            except Exception as e:
                teams = []                

            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 4 or len(teams) != 2 or not item[1].replace(".", "").isnumeric() or not item[2].replace(".", "").isnumeric():
                    if item[0] != '':
                        print("Fortuna: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"team_1": teams[0],
                    "team_2": teams[1],
                    "stake_1_wins": item[1],
                    "stake_draw": np.inf,
                    "stake_2_wins": item[2],
                    "url": url,
                    "category": category}
            
            elif bet_outcomes == 'three-way':    
                # if invalid data - skip 
                if len(item) < 4 or len(teams) != 2 or not item[1].replace(".", "").isnumeric() or not item[2].replace(".", "").isnumeric() or not item[3].replace(".", "").isnumeric():
                    if item[0] != '':
                        print("Fortuna: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"team_1": teams[0],
                    "team_2": teams[1],
                    "stake_1_wins": item[1],
                    "stake_draw": item[2],
                    "stake_2_wins": item[3],
                    "url": url,
                    "category": category}
            
            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    return df


# # test

# df = pd.DataFrame()
# df = df._append(scrape_fortuna(), ignore_index=True)
# print(df.head())

