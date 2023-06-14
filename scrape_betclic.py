from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
from datetime import datetime, date, timedelta

from additional_functions import scroll_into_view


def scrape_betclic() -> pd.DataFrame():
    # links (url, category, 2/3 way bet)
    links = [
                ('https://www.betclic.pl/rugby-xiii-s52', 'rugby', 'three-way'),
                ('https://www.betclic.pl/rugby-xv-s5', 'rugby', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-1-liga-c146', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-kolmonen-c21892', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-2-liga-c494', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-kakkonen-a-c7467', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-kakkonen-b-c7468', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/finlandia-kakkonen-c-c7469', 'finnish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazylia-campeonato-k-c21767', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazylia-serie-a-c187', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazylia-serie-c-c19658', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazilia-carioca-3-c26087', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazilia-carioca-b2-u20-c24650', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazylia-serie-b-c3454', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/brazylia-serie-d-c22011', 'brazilian football', 'three-way'),
                ('https://www.betclic.pl/sztuki-walki-s23/ufc-c15946', 'ufc', 'two-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-1-liga-c1749', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-2-liga-c2836', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-2-c22093', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-1-c22012', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-podkarpacka-c25999', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-zachodniopomorska-c26010', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-3-c22107', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-3-liga-gr-4-c21798', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-kujawsko-pomorska-c25994', 'polish football', 'three-way'),
                ('https://www.betclic.pl/pilka-nozna-s1/polska-4-liga-swietokrzyska-c26007', 'polish football', 'three-way')
            ]
    
    # initialize output DataFrame
    columns = ["game_datetime", "team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url", "category"]
    df = pd.DataFrame({}, columns=columns)
    
    #   chrome driver setup
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
        time.sleep(1)

        # get table elements of every polish football league (on the same page)
        group_events = driver.find_elements(By.CLASS_NAME, 'groupEvents')
                                                         
        for index, group_event in enumerate(group_events):
            scroll_into_view(driver, group_events[min(index+5, len(group_events)-1)], sleep=0)

            # scrape events date (common for section)
            events_date = group_event.find_element(By.CLASS_NAME, "groupEvents_headTitle").text

            # manage unexpected values
            if events_date == 'Teraz':
                continue            
            elif events_date == 'Dzisiaj':
                events_date = date.today().strftime("%d.%m.%Y")
            elif events_date == 'Jutro':
                events_date = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")
            elif events_date == 'Pojutrze':
                events_date = (date.today() + timedelta(days=2)).strftime("%d.%m.%Y")

            # scrape events wtithin section & find elements until each is loaded
            last_elements_count = 0
            current_elements_count = -1       
            while last_elements_count != current_elements_count:
                last_elements_count = current_elements_count
                # get table elements of every league (on the same page)
                events = group_event.find_elements(By.CLASS_NAME, "cardEvent")
                current_elements_count = len(events)
                
                if current_elements_count > 0:
                    # scroll to last loaded element
                    driver.execute_script("arguments[0].scrollIntoView(false);", events[-1])

            for event in events:
                scroll_into_view(driver, event, sleep=0)

                item = event.text.split("\n")
                stakes = list(filter(lambda x: x.replace(",", "").isnumeric(), item))

                # get events time
                event_time = event.find_element(By.CLASS_NAME, "scoreboard_hour").text

                # merge to datetime
                event_datetime = datetime.strptime(str(events_date) + " " + event_time, "%d.%m.%Y %H:%M").strftime("%d-%m %H:%M")
                
                if bet_outcomes == 'two-way':
                    # if invalid data - skip 
                    if len(item) < 8 or len(stakes) != 2:
                        print("BetClic: Error appending - " + " | ".join(item))
                        continue

                    # append item
                    dct = {"game_datetime": event_datetime,
                           "team_1": item[3],
                           "team_2": item[5],
                           "stake_1_wins": stakes[0].replace(",", "."),
                           "stake_draw": np.inf,
                           "stake_2_wins": stakes[1].replace(",", "."),
                           "url": url,
                           "category": category
                        }
                
                elif bet_outcomes == 'three-way':
                    # if invalid data - skip 
                    if len(item) < 11 or len(stakes) != 3:
                        print("BetClic: Error appending - " + " | ".join(item))
                        continue

                    # append item
                    dct = {"game_datetime": event_datetime, 
                           "team_1": item[3],
                           "team_2": item[5],
                           "stake_1_wins": stakes[0].replace(",", "."),
                           "stake_draw": stakes[1].replace(",", "."),
                           "stake_2_wins": stakes[2].replace(",", "."),
                           "url": url,
                           "category": category
                        }
                df = df._append(pd.DataFrame([dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()
    return df


# # test
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]



# df = pd.DataFrame()
# df = df._append(scrape_betclic(), ignore_index=True)
# print(df.head())

