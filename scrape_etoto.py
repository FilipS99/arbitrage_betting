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


def scrape_etoto() -> pd.DataFrame():
    # links
    links = [
                ('https://www.etoto.pl/zaklady-bukmacherskie/sporty-walki/ufc/ufc-289:-nunes-vs-aldana,ufc-fn:-vettori-vs-cannonier,ufc-fn:-emmett-vs-topuria,ufc-290:-volkanovski-vs-rodriguez,ufc-fn:-aspinall-vs-tybura,ufc-291:-poirier-vs-gaethje-2,ufc-292:-sterling-vs-o-malley/23444,23558,23453,23536,23537,23590,23591',
                  'ufc', 'two-way'),
                ('https://www.etoto.pl/zaklady-bukmacherskie/pilka-nozna/polska/polska-1-liga,4-liga-dolnoslaska-(baraz-o-iii-lige),4-liga-opolska,4-liga-podkarpacka/305,15462,15332,15473',
                  'polish football', 'three-way'),
                ('https://www.etoto.pl/zaklady-bukmacherskie/pilka-nozna/finlandia/veikkausliiga,ykkonen,kakkonen-itainen,kakkonen-lantinen,kakkonen-pohjoinen/240,289,349,390,366', 
                  'finnish football', 'three-way'),
                ('https://www.etoto.pl/zaklady-bukmacherskie/rugby/rugby-union,rugby-league/top-14,major-league-rugby,super-rugby,puchar-swiata,super-league,rfl-championship,state-of-origin/2593,5519,15034,22951,2591,6227,7679', 
                  'rugby', 'three-way'),
                ('https://www.etoto.pl/zaklady-bukmacherskie/pilka-nozna/brazylia/serie-a,serie-d,serie-b,serie-c,campeonato-brasileiro-[k]/566,1144,734,773,1041', 
                  'brazilian football', 'three-way') 
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
        url, category, bet_outcomes  = link

        # load page
        driver.get(url)
        
        # in case of 'stale' elements
        time.sleep(3)

        # scrape rows
        elements = driver.find_elements(By.XPATH,'/html/body/div[3]/div[3]/div[1]/div[2]/div[3]/div/div/div[3]/partial[4]/div/div/div/div[2]/div[2]/div[*]/ul/li[*]/ul/li') 

        for element in elements:
            # Get initial element position
            initial_position = element.location["y"]

            # Scroll loop - until element is visible
            while True:
                # Scroll to the element's bottom position
                driver.execute_script("arguments[0].scrollIntoView(false);", element)
                
                # Wait for a short interval to allow content to load
                # time.sleep(0.1)
                
                # Calculate the new element position after scrolling
                new_position = element.location["y"]
                
                # Break the loop if the element's position remains the same (reached the bottom)
                if new_position == initial_position:
                    break
                
                # Update the last recorded position
                initial_position = new_position

            item = element.text.split('\n')
            
            if bet_outcomes == 'two-way':
                # if invalid data - skip 
                if len(item) < 7 or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                    print("Etoto: Error appending - " + " | ".join(item))
                    continue
                
                # append item
                dct = {"team_1": item[0],
                    "team_2": item[1],
                    "stake_1_wins": item[4],
                    "stake_draw": np.inf,
                    "stake_2_wins": item[5],
                    "url": url,
                    "category": category}
                
            elif bet_outcomes == 'three-way':
                # if invalid data - skip 
                if len(item) < 7 or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric() or not item[6].replace(".", "").isnumeric():
                    print("Etoto: Error appending - " + " | ".join(item))
                    continue
                
                # append item
                dct = {"team_1": item[0],
                    "team_2": item[1],
                    "stake_1_wins": item[4],
                    "stake_draw": item[5],
                    "stake_2_wins": item[6],
                    "url": url,
                    "category": category}
                

            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    # print(f"{'Etoto:':<10} {len(df)}")

    return df


# # # test

# df = pd.DataFrame()
# df = df._append(scrape_etoto(), ignore_index=True)
# print(df.head())
