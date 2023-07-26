from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
from selenium.webdriver.common.action_chains import ActionChains
import re
from typing import Tuple
from datetime import date

from additional_functions import scroll_into_view, get_closest_week_day, scroll_to_end_of_page, scroll_to_start_of_page


def scrape_etoto() -> Tuple[pd.DataFrame, list]:
    # page link
    url = 'https://www.etoto.pl/'

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
    driver.implicitly_wait(3)
    action_chains = ActionChains(driver)

    # load page
    driver.get(url)
    
    # in case of 'stale' elements
    time.sleep(1)

    # (discipline_name, subtype, bet_outcomes, category
    disciplines_data = [
                        ('Piłka nożna', 'Finlandia', 'three-way', 'finnish football'),
                        ('Tenis', '*', 'two-way', 'tennis'), 
                        ('Rugby', '*', 'three-way', 'rugby'),
                        ('Piłka nożna', 'Polska', 'three-way', 'polish football'), 
                        ('Piłka nożna', 'Brazylia', 'three-way', 'brazilian football'), 
                        ('Sporty walki', '*', 'two-way', 'ufc')]

    for discipline_name, discipline_subtype, bet_outcomes, category in disciplines_data:
        try:
            scroll_to_end_of_page(driver)

            # try to find disciplines (retry if stale)
            disciplines = driver.find_elements(By.XPATH, "/html/body/div[3]/div[*]/div[1]/div[2]/div[1]/div/div/ul/li[*]")
            
            if len(disciplines) == 0:
                errors.append(f"Etoto: disciplines not found")
                return df, errors
        
            # filter disciplines
            discipline = [d for d in disciplines if discipline_name == d.text.split('\n')[0]]
            if len(discipline) != 1:
                errors.append(f"Etoto: '{discipline_name}' not found [{len(discipline)} matches]")
                continue

            # activate discipline dropdown list
            success = activate_dropdown_list(driver, action_chains, discipline[0])
            if success == False: 
                errors.append(f"Etoto: Unable to activate dropdown list [{discipline_name}]")
                continue

            # try to find discipline subtypes (retry if stale)
            subtypes = discipline[0].find_elements(By.XPATH, "./ul/li[*]")
            if len(subtypes) == 0:
                errors.append(f"Etoto: '{discipline_name}/{discipline_subtype}' elements timeout")
                continue

            # filter discipline subtypes if only one desired
            if discipline_subtype != '*':
                subtypes = [s for s in subtypes if discipline_subtype in s.text]
                
                if len(subtypes) != 1:
                    errors.append(f"Etoto: '{discipline_name}/{discipline_subtype}' not found [{len(discipline)}]")
                    continue
            
            # for subtypes for discipline
            for subtype in reversed(subtypes):
                try:
                    scroll_into_view(driver, subtype)

                    # activate subtype dropdown list
                    success = activate_dropdown_list(driver, action_chains, subtype)
                    if success == False:
                        errors.append(f"Etoto: Unable to open subtype dropdown list [{subtype}]")
                        continue

                    # try to find elements (retry if stale)
                    leagues = subtype.find_elements(By.XPATH, "./ul/li[*]/a/span")
                    
                    if len(leagues) == 0:
                        errors.append(f"Etoto: '{discipline_name}/{discipline_subtype}' elements timeout")
                        continue

                    for league in reversed(leagues):
                        try:
                            scroll_into_view(driver, league)
                            # try to find discipline subtypes (retry if stale)
                            subtypes = discipline[0].find_elements(By.XPATH, "./ul/li[*]")
                            if len(subtypes) == 0:
                                errors.append(f"Etoto: '{discipline_name}/{discipline_subtype}' elements timeout")
                                continue

                            # activate subtype dropdown list
                            success = activate_dropdown_list(driver, action_chains, subtype)
                            if success == False:
                                errors.append(f"Etoto: Unable to open subtype dropdown list [{subtype}]")
                                continue

                            action_chains.click(league).perform()

                            scroll_to_start_of_page(driver)

                            # try to find elements (retry if stale)
                            elements = driver.find_elements(By.XPATH, '/html/body/div[3]/div[*]/div[1]/div[2]/div[3]/div/div/div[3]/partial[4]/div/div/div/div[2]/div[2]/div[*]/ul/li[*]/ul')
                            if len(elements) == 0:
                                errors.append(f"Etoto: Unable to get league elements [{league.text}]")
                                continue

                            for element in reversed(elements):
                                try:
                                    scroll_into_view(driver, element, sleep=0)

                                    # item = element.text.split('\n')

                                    # event data
                                    team_1 = element.find_elements(By.XPATH, ".//*[contains(@class, 'participant1')]")
                                    team_2 = element.find_elements(By.XPATH, ".//*[contains(@class, 'participant2')]")
                                    bet_odds = element.find_elements(By.XPATH, ".//*[contains(@class, 'eventListOutcomesPartial')]")
                                    event_time = element.find_elements(By.XPATH, ".//*[contains(@class, 'date-time')]")
                                    
                                    # validate data
                                    if len(team_1) != 1 or len(team_2) != 1 or len(bet_odds) == 0 or len(event_time) != 1:
                                        errors.append("Etoto: Values not found: " + " | ".join(element.text.split('\n')))
                                        continue  

                                    numeric_pattern = re.compile(r'^[-+]?[0-9]+(\.[0-9]+)?$')
                                    if any(not numeric_pattern.match(odd.replace(",", ".")) for odd in bet_odds[0].text.split('\n')):
                                        errors.append("Etoto: Values not found: " + " | ".join(element.text.split('\n')))
                                        continue  

                                    game_datetime = event_time[0].text.replace('.', '-').replace('\n', ' ').replace('Dzisiaj', date.today().strftime("%d-%m"))  

                                    # continue if gametime doesnt match regex
                                    date_pattern = r"\d{2}-\d{2} \d{2}:\d{2}"
                                    if not re.match(date_pattern, game_datetime):
                                        errors.append("Etoto: Datetime error: " + game_datetime)
                                        continue    
                                    
                                    if bet_outcomes == 'two-way':
                                        # if invalid data - skip 
                                        if len(bet_odds[0].text.split('\n')) != 2:
                                            errors.append("Etoto: Error appending - " + " | ".join(element.text.split('\n')))
                                            continue
                                        
                                        # append item
                                        df_row = {"game_datetime": game_datetime,
                                            "team_1": team_1[0].text,
                                            "team_2": team_2[0].text,
                                            "stake_1_wins": bet_odds[0].text.split('\n')[0],
                                            "stake_draw": np.inf,
                                            "stake_2_wins": bet_odds[0].text.split('\n')[1],
                                            "url": driver.current_url,
                                            "category": category}
                                        
                                    elif bet_outcomes == 'three-way':
                                        # if invalid data - skip 
                                        if len(bet_odds[0].text.split('\n')) != 3:
                                            errors.append("Etoto: Error appending - " + " | ".join(element.text.split('\n')))
                                            continue
                                        
                                        # append item
                                        df_row = {"game_datetime": game_datetime,
                                            "team_1": team_1[0].text,
                                            "team_2": team_2[0].text,
                                            "stake_1_wins": bet_odds[0].text.split('\n')[0],
                                            "stake_draw": bet_odds[0].text.split('\n')[1],
                                            "stake_2_wins": bet_odds[0].text.split('\n')[2],
                                            "url": driver.current_url,
                                            "category": category}
                                        

                                    df = df._append(pd.DataFrame(
                                        [df_row], columns=columns), ignore_index=True)
                                    
                                except Exception:
                                    errors.append("Etoto: Element skipped (probably stale)")
                                    continue

                        except Exception:
                            errors.append("Etoto: League skipped (probably stale)")
                            continue
                    
                    # close subtype dropdown list
                    deactivate_dropdown_list(driver, action_chains, subtype)
                    if not success:
                        errors.append(f"Etoto: Unable to close subtype dropdown list [{subtype.text}]")

                except Exception:
                    errors.append("Etoto: Subtype skipped (probably stale)")
                    continue

        except Exception:
            errors.append("Etoto: Discipline skipped (probably stale)")
            continue
                    
                
                    
        # close discipline dropdown list
        deactivate_dropdown_list(driver, action_chains, discipline[0])

        if not success:
            errors.append(f"Etoto: Unable to close discipline dropdown list [{discipline_name}]")
        
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
# df, errors = scrape_etoto()
# print(df.head())
