from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import pandas as pd
import time
from datetime import datetime
import re
from typing import Tuple

from additional_functions import scroll_into_view, scroll_to_end_of_page, scroll_to_start_of_page


def scrape_fuksiarz() -> Tuple[pd.DataFrame, list]:
    # page link
    url = 'https://fuksiarz.pl/zaklady-bukmacherskie'

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

    # Click Cookies button
    button_element = driver.find_elements(By.ID, "onetrust-accept-btn-handler")  
    if len(button_element) > 0: 
        button_element[0].click()

    # (discipline_name, subtype, bet_outcomes, category
    disciplines_data = [
                        ('Piłka nożna', 'Finlandia', 'three-way', 'finnish football'),
                        ('Tenis', '*', 'two-way', 'tennis'), 
                        ('Rugby', '*', 'three-way', 'rugby'),
                        ('Piłka nożna', 'Polska', 'three-way', 'polish football'), 
                        ('Piłka nożna', 'Brazylia', 'three-way', 'brazilian football'), 
                        ('MMA', '*', 'two-way', 'ufc')]

    for discipline_name, discipline_subtype, bet_outcomes, category in disciplines_data:
        try:
            scroll_to_end_of_page(driver)

            # try to find disciplines (retry if stale)
            disciplines = driver.find_elements(By.XPATH, "/html/body/div[3]/div[*]/div[1]/div[*]/div[1]/div/div/ul/li[*]")
            
            if len(disciplines) == 0:
                errors.append(f"Fuksiarz: disciplines not found")
                return df, errors
        
            # filter disciplines
            discipline = [d for d in disciplines if discipline_name == d.text.split('\n')[0]]
            if len(discipline) != 1:
                errors.append(f"Fuksiarz: '{discipline_name}' not found [{len(discipline)} matches]")
                continue

            # activate discipline dropdown list
            success = activate_dropdown_list(driver, action_chains, discipline[0])
            if success == False: 
                errors.append(f"Fuksiarz: Unable to activate dropdown list [{discipline_name}]")
                continue

            # try to find discipline subtypes (retry if stale)
            time.sleep(1)
            subtypes = discipline[0].find_elements(By.XPATH, "./ul/li[*]")
            if len(subtypes) == 0:
                errors.append(f"Fuksiarz: '{discipline_name}/{discipline_subtype}' elements timeout")
                continue

            # filter discipline subtypes if only one desired
            if discipline_subtype != '*':
                subtypes = [s for s in subtypes if discipline_subtype in s.text]
                
                if len(subtypes) != 1:
                    errors.append(f"Fuksiarz: '{discipline_name}/{discipline_subtype}' not found [{len(discipline)}]")
                    continue
            
            # for subtypes for discipline
            for subtype in reversed(subtypes):
                try:
                    scroll_into_view(driver, subtype)

                    # activate subtype dropdown list
                    success = activate_dropdown_list(driver, action_chains, subtype)
                    if success == False:
                        errors.append(f"Fuksiarz: Unable to open subtype dropdown list [{subtype}]")
                        continue

                    # try to find elements (retry if stale)
                    leagues = subtype.find_elements(By.XPATH, "./ul/li[*]/div/div/span")
                                                                
                    if len(leagues) == 0:
                        errors.append(f"Fuksiarz: '{discipline_name}/{discipline_subtype}' elements timeout")
                        continue

                    for league in reversed(leagues):
                        try:
                            scroll_into_view(driver, league)

                            time.sleep(0.25)
                            action_chains.click(league).perform()
                            time.sleep(0.1)

                            scroll_to_start_of_page(driver)

                            # try to find elements (retry if stale)
                            elements = driver.find_elements(By.XPATH, '/html/body/div[3]/div[*]/div[1]/div/div[3]/div/div/div[3]/partial[*]/div/div/div/div[2]/div[2]/div[3]/ul/li[*]/ul/li')
                            if len(elements) == 0:
                                errors.append(f"Fuksiarz: Unable to get league elements [{league.text}]")
                                continue

                            for element in reversed(elements):
                                try:
                                    scroll_into_view(driver, element, sleep=0)

                                    item = element.text.split('\n')
                                    teams = item[2].split(' - ')

                                    # set game datetime
                                    if len(item) > 2:
                                        game_datetime = (item[1] + ' ' + item[0]).replace('.', '-')

                                        # continue if gametime doesnt match regex
                                        date_pattern = r"\d{2}-\d{2} \d{2}:\d{2}"
                                        if not re.match(date_pattern, game_datetime):
                                            errors.append("Fuksiarz: Datetime error: " + game_datetime)
                                            continue

                                    if bet_outcomes == 'two-way':
                                        # if invalid data - skip
                                        if len(item) < 6 or len(teams) != 2 or not item[3].replace(".", "").isnumeric() or not item[4].replace(".", "").isnumeric():
                                            errors.append(
                                                "Fuksiarz: Error appending - " + " | ".join(item))
                                            continue

                                        # append item
                                        dct = {"game_datetime": game_datetime,
                                               "team_1": teams[0],
                                               "team_2": teams[1],
                                               "stake_1_wins": item[3],
                                               "stake_draw": np.inf,
                                               "stake_2_wins": item[4],
                                               "url": driver.current_url,
                                               "category": category
                                               }

                                    elif bet_outcomes == 'three-way':
                                        # if invalid data - skip
                                        if len(item) < 6 or len(teams) != 2 or not item[3].replace(".", "").isnumeric() or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                                            errors.append(
                                                "Fuksiarz: Error appending - " + " | ".join(item))
                                            continue

                                        # append item
                                        dct = {"game_datetime": game_datetime,
                                               "team_1": teams[0],
                                               "team_2": teams[1],
                                               "stake_1_wins": item[3],
                                               "stake_draw": item[4],
                                               "stake_2_wins": item[5],
                                               "url": driver.current_url,
                                               "category": category
                                               }

                                    df = df._append(pd.DataFrame(
                                        [dct], columns=columns), ignore_index=True)

                                    
                                except Exception:
                                    errors.append("Fuksiarz: Element skipped (probably stale)")
                                    continue

                        except Exception:
                            errors.append("Fuksiarz: League skipped (probably stale)")
                            continue
                    
                    # close subtype dropdown list
                    deactivate_dropdown_list(driver, action_chains, subtype)
                    if not success:
                        errors.append(f"Fuksiarz: Unable to close subtype dropdown list [{subtype.text}]")

                except Exception:
                    errors.append("Fuksiarz: Subtype skipped (probably stale)")
                    continue

        except Exception:
            errors.append("Fuksiarz: Discipline skipped (probably stale)")
            continue
                    
                
                    
        # close discipline dropdown list
        deactivate_dropdown_list(driver, action_chains, discipline[0])

        if not success:
            errors.append(f"Fuksiarz: Unable to close discipline dropdown list [{discipline_name}]")
        
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
                action_chains.click(element.find_element(By.XPATH, "./*[contains(@class, 'dropdown-menu-item-inner')]")).perform()
                retries += 1
    except Exception:
        success = False
        pass

    return success

# # # test

# df = pd.DataFrame()
# df = df._append(scrape_fuksiarz(), ignore_index=True)
# print(df.head())
