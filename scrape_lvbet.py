from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
from datetime import datetime
import re
from typing import Tuple

from additional_functions import scroll_into_view, get_closest_week_day, scroll_to_end_of_page, scroll_to_start_of_page


def scrape_lvbet() -> Tuple[pd.DataFrame, list]:
    # page link
    url = 'https://lvbet.pl/pl/'

    # initialize output DataFrame
    columns = ["game_datetime", "team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url", "category"]
    df = pd.DataFrame({}, columns=columns)
    errors = []
    
    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(1)
    action_chains = ActionChains(driver)

    # load page
    driver.get(url)
    
    # in case of 'stale' elements
    time.sleep(1)

    # Click Cookies button
    button_element = driver.find_elements(By.CLASS_NAME, "lv-cookie-button")  
    if len(button_element) > 0: 
        button_element[0].click()

    # (discipline_name, subtype, bet_outcomes, category
    disciplines_data = [
                        ('Piłka nożna', 'Finlandia', 'three-way', 'finnish football'),
                        ('Tenis', '*', 'two-way', 'tennis'), 
                        ('Rugby League', '*', 'three-way', 'rugby'),
                        ('Rugby Union', '*', 'three-way', 'rugby'),
                        ('Piłka nożna', 'Polska', 'three-way', 'polish football'), 
                        ('Piłka nożna', 'Brazylia', 'three-way', 'brazilian football'), 
                        ('MMA / Kick-boxing', 'UFC', 'two-way', 'ufc')]

    for discipline_name, discipline_subtype, bet_outcomes, category in disciplines_data:
        try:
            # refresh page
            driver.get(url)
    
            # in case of 'stale' elements
            time.sleep(2)
    
            # Click Show All Disciplines
            button_element = driver.find_elements(By.CLASS_NAME, "btn-sidebar-show")  
            if len(button_element) > 0: 
                button_element[0].click()

            scroll_to_end_of_page(driver)

            # try to find disciplines (retry if stale)
            disciplines = driver.find_elements(By.CLASS_NAME, "sidebar-entry")
            
            if len(disciplines) == 0:
                errors.append(f"LvBet: disciplines not found")
                return df, errors
        
            # filter disciplines
            discipline = [d for d in disciplines if discipline_name == d.text.split('\n')[0]]
            if len(discipline) != 1:
                errors.append(f"LvBet: '{discipline_name}' not found [{len(discipline)} matches]")
                continue
            
            # activate discipline dropdown list
            success = activate_dropdown_list(driver, action_chains, discipline[0])
            if success == False: 
                errors.append(f"LvBet: Unable to activate dropdown list [{discipline_name}]")
                continue

            # try to find discipline subtypes 
            subtypes = discipline[0].find_elements(By.CLASS_NAME, 'sidebar-list-entry')  
            if len(subtypes) == 0:
                errors.append(f"LvBet: '{discipline_name}/{discipline_subtype}' elements timeout")
                continue
            
            # Click Show All Subtypes
            button_element = [b for b in subtypes if b.text.split('\n')[0] == 'Show all' ]
            if len(button_element) > 0: 
                button_element[0].click()

                # refresh subtypes
                subtypes = discipline[0].find_elements(By.CLASS_NAME, 'sidebar-list-entry')  

            # filter discipline subtypes if only one desired
            if discipline_subtype != '*':
                subtypes = [s for s in subtypes if discipline_subtype in s.text]
                
                if len(subtypes) != 1:
                    errors.append(f"LvBet: '{discipline_name}/{discipline_subtype}' not found [{len(discipline)}]")
                    continue
            
            # for subtypes for discipline
            for subtype in reversed(subtypes):
                try:
                    scroll_into_view(driver, subtype)

                    # activate subtype dropdown list
                    success = activate_dropdown_list(driver, action_chains, subtype)
                    if success == False:
                        if subtype.text != "":
                            errors.append(f"LvBet: Unable to open subtype dropdown list [{subtype.text}]")
                        continue

                    # try to find leagues
                    league = subtype.find_elements(By.CLASS_NAME, 'sidebar-list-entry')  
                    
                    # Select all leagues
                    if len(league) == 1:
                        button_element = league
                    else:
                        button_element = [b for b in league if b.text.split('\n')[0] == 'Wybierz wszystkie' ]
                        if len(button_element) != 1: 
                            errors.append(f"LvBet: '{discipline_name}/{discipline_subtype}' 'Wybierz wszystkie' not found [{len(discipline)}]")
                            continue
                    button_element[0].click()


                except Exception:
                    if subtype.text != "":
                        errors.append("LvBet: Subtype skipped (probably stale)")
                    continue
                    
            time.sleep(1)
            # try to find elements (retry if stale)
            elements = driver.find_elements(By.CLASS_NAME, 'single-game')
            if len(elements) == 0:
                errors.append(f"LvBet: Unable to get league elements [{league.text}]")
                continue

            for element in reversed(elements):
                try:
                    scroll_into_view(driver, element, sleep=0)

                    # event data
                    team_1 = element.find_elements(By.XPATH, ".//*[contains(@class, 'single-game-participants__entry single-game-participants__entry--home')]")
                    if len(team_1) == 0:
                        errors.append("LvBet: Team 1 name not found: " + " | ".join(element.text.split('\n')))
                        continue

                    team_2 = element.find_elements(By.XPATH, ".//*[contains(@class, 'single-game-participants__entry single-game-participants__entry--away')]")
                    if len(team_2) == 0:
                        errors.append("LvBet: Team 2 name not found: " + " | ".join(element.text.split('\n')))
                        continue

                    bet_odds = element.find_elements(By.XPATH, ".//*[contains(@class, 'column-data--primary')]")
                    if len(bet_odds) == 0:
                        errors.append("LvBet: bet odds not found: " + " | ".join(element.text.split('\n')))
                        continue
                    bet_odds = bet_odds[0].text.split('\n')

                    event_time = element.find_elements(By.XPATH, ".//*[contains(@class, 'single-game-date__entry has-hour')]")
                    if len(event_time) == 0:
                        errors.append("LvBet: event time not found: " + " | ".join(element.text.split('\n')))
                        continue

                    event_date = element.find_elements(By.XPATH, ".//*[contains(@class, 'single-game-date__entry has-day')]")
                    if len(event_date) == 0:
                        errors.append("LvBet: event time not found: " + " | ".join(element.text.split('\n')))
                        continue

                    # validate data
                    numeric_pattern = re.compile(r'^[-+]?[0-9]+(\.[0-9]+)?$')
                    if len(team_1) != 1 or len(team_2) != 1 or len(event_time) != 1 or len(event_date) != 1 or len(bet_odds) < 3 or any(not numeric_pattern.match(e.replace(",", ".")) and e != 'VS' for e in bet_odds):
                        errors.append("LvBet: Values not found: " + " | ".join(element.text.split('\n')))
                        continue   

                    # check if event datetime matches regex
                    game_datetime = event_date[0].text.replace(".", "-") + " " + event_time[0].text
                    date_pattern = r"\d{2}-\d{2} \d{2}:\d{2}"
                    if not re.match(date_pattern, game_datetime):
                        errors.append("LvBet: Datetime error: " + game_datetime)
                        continue    
                    
                    if bet_outcomes == 'two-way':
                        # append item
                        df_row = {"game_datetime": game_datetime,
                            "team_1": team_1[0].text,
                            "team_2": team_2[0].text,
                            "stake_1_wins": bet_odds[0],
                            "stake_draw": np.inf,
                            "stake_2_wins": bet_odds[2],
                            "url": driver.current_url,
                            "category": category}
                        
                    elif bet_outcomes == 'three-way':
                        # append item
                        df_row = {"game_datetime": game_datetime,
                            "team_1": team_1[0].text,
                            "team_2": team_2[0].text,
                            "stake_1_wins": bet_odds[0],
                            "stake_draw": bet_odds[1],
                            "stake_2_wins": bet_odds[2],
                            "url": driver.current_url,
                            "category": category}
                        

                    df = df._append(pd.DataFrame(
                        [df_row], columns=columns), ignore_index=True)
                        
                except Exception:
                    errors.append("LvBet: Element skipped (probably stale)")
                    continue

                    # # close subtype dropdown list
                    # deactivate_dropdown_list(driver, action_chains, subtype)
                    # if not success:
                    #     errors.append(f"LvBet: Unable to close subtype dropdown list [{subtype.text}]")

        except Exception:
            errors.append("LvBet: Discipline skipped (probably stale)")
            continue
          
        # # close discipline dropdown list
        # deactivate_dropdown_list(driver, action_chains, discipline[0])

        # if not success:
        #     errors.append(f"LvBet: Unable to close discipline dropdown list [{discipline_name}]")
        
    # Close the WebDriver
    driver.quit()
    
    return df, errors


def activate_dropdown_list(driver, action_chains, element):
    retries = 0
    success = True
    try:
        scroll_into_view(driver, element, sleep=0) 
        while not 'is-active' in element.get_attribute('class'):
            if retries >= 5:
                success = False
                break
            else:
                time.sleep(0.25)
                action_chains.click(element).perform()
                retries += 1
    except Exception:
        success = False
        pass
    
    return success


def deactivate_dropdown_list(driver, action_chains, element):
    retries = 0
    success = True
    try:
        scroll_into_view(driver, element, sleep=0) 
        while 'is-active' in element.get_attribute('class'):
            if retries >= 5:
                success = False
                break
            else:
                time.sleep(0.25)
                action_chains.click(element.find_element(By.XPATH, "./*[contains(@class, 'sportList_itemWrapper')]")).perform()
                retries += 1
    except Exception:
        success = False
        pass

    return success
    

# # # test

# df = pd.DataFrame()
# errors = []
# df, errors = scrape_lvbet()
# print(df.head())
