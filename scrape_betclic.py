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


def scrape_betclic() -> pd.DataFrame():
    # links (url, category, 2/3 way bet)
    links = [
                ('https://www.betclic.pl/pilka-nozna-s1/polska-1-liga-c1749', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-2-liga-c2836', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-2-c22093', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-1-c22012', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-podkarpacka-c25999', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-zachodniopomorska-c26010', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-3-c22107', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-4-c21798', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-kujawsko-pomorska-c25994', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-swietokrzyska-c26007', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-1-liga-c146', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-kolmonen-c21892', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-2-liga-c494', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-kakkonen-a-c7467', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-kakkonen-b-c7468', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-kakkonen-c-c7469', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/rugby-xiii-s52', 'rugby', 'three-way'),
                ('https://www.betclic.pl/rugby-xv-s5', 'rugby', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazylia-campeonato-k-c21767', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazylia-serie-a-c187', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazylia-serie-c-c19658', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazilia-carioca-3-c26087', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazilia-carioca-b2-u20-c24650', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazylia-serie-b-c3454', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazylia-serie-d-c22011', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/sztuki-walki-s23/ufc-c15946', 'ufc', 'two-way')
            ]
    
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
        url, category, bet_outcomes = link

        # load page
        driver.get(url)     
        
        # in case of 'stale' elements
        time.sleep(1)

        # get table elements of every polish football league (on the same page)
        table_elements = driver.find_elements(By.XPATH, '/html/body/app-desktop/div[1]/div/bcdk-content-scroller/div/sports-competition/div[3]/sports-events-list/bcdk-vertical-scroller/div/div[2]/div/div/div[*]/div[2]/sports-events-event[*]')
                                                         
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
            stakes = list(filter(lambda x: x.replace(",", "").isnumeric(), item))
            
            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 10 or len(stakes) != 2:
                    print("BetClic: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"team_1": item[3],
                    "team_2": item[5],
                    "stake_1_wins": stakes[0].replace(",", "."),
                    "stake_draw": np.inf,
                    "stake_2_wins": stakes[1].replace(",", "."),
                    "url": url,
                    "category": category}
            
            elif bet_outcomes == 'three-way':
                # if invalid data - skip 
                if len(item) < 11 or len(stakes) != 3:
                    print("BetClic: Error appending - " + " | ".join(item))
                    continue

                # append item
                dct = {"team_1": item[3],
                    "team_2": item[5],
                    "stake_1_wins": stakes[0].replace(",", "."),
                    "stake_draw": stakes[1].replace(",", "."),
                    "stake_2_wins": stakes[2].replace(",", "."),
                    "url": url,
                    "category": category}
            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()
    return df


# # test
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]



# df = pd.DataFrame()
# df = df._append(scrape_betclic(), ignore_index=True)
# print(df.head())

