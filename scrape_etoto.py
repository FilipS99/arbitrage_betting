from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
from selenium.webdriver.common.action_chains import ActionChains
import re
from typing import Tuple

from additional_functions import scroll_into_view, get_closest_week_day, find_elements_without_stale


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
    time.sleep(3)

    # Get the current URL, skip if redirectred
    # if url != driver.current_aurl:
    #     errors.append("Etoto: URL Redirected to: " + driver.current_url)
    #     return

    # (discipline_name, subtype, bet_outcomes, category
    disciplines_data = [
                        ('Piłka nożna', 'Finlandia', 'three-way', 'finnish football'),
                        ('Tenis', '*', 'two-way', 'tennis'), 
                        ('Rugby', '*', 'three-way', 'rugby'),
                        ('Piłka nożna', 'Polska', 'three-way', 'polish football'), 
                        ('Piłka nożna', 'Brazylia', 'three-way', 'brazilian football'), 
                        ('Sporty walki', '*', 'two-way', 'ufc')]

    for discipline_name, discipline_subtype, bet_outcomes, category in disciplines_data:
        # try to find disciplines (retry if stale)
        disciplines, success = find_elements_without_stale(driver, "/html/body/div[3]/div[*]/div[1]/div[2]/div[1]/div/div/ul/li[*]")
        
        if success == False:
            errors.append(f"Etoto: finding disciplines elements timeout")
            return df, errors
    
        # filter disciplines
        discipline = [d for d in disciplines if discipline_name == d.text.split('\n')[0]]
        if len(discipline) != 1:
            errors.append(f"Etoto: '{discipline_name}' not found [{len(discipline)} matches]")
            continue

        # activate discipline dropdown list
        success = activate_dropdown_list(action_chains, discipline[0])
        if success == False: 
            errors.append(f"Etoto: Unable to activate dropdown list [{discipline_name}]")
            continue

        # try to find discipline subtypes (retry if stale)
        subtypes, success = find_elements_without_stale(discipline[0], "./ul/li[*]")
        if success == False:
            errors.append(f"Etoto: '{discipline_name}/{discipline_subtype}' elements timeout")
            continue

        # filter discipline subtypes if only one desired
        if discipline_subtype != '*':
            subtypes = [s for s in subtypes if discipline_subtype in s.text]
            
            if len(subtypes) != 1:
                errors.append(f"Etoto: '{discipline_name}/{discipline_subtype}' not found [{len(discipline)}]")
                continue
        
        # for subtypes for discipline
        for subtype in subtypes:
            # activate subtype dropdown list
            success = activate_dropdown_list(action_chains, subtype)
            if success == False:
                errors.append(f"Etoto: Unable to open subtype dropdown list [{subtype}]")
                continue

            # # open dropdown list
            # retries = 0
            # error = False
            # while not 'is-active' in subtype.get_attribute('class'):
            #     if retries >= 3:
            #         errors.append(f"Etoto: Unable to open dropdown list [{subtype}]")
            #         error = True
            #         break
            #     else:
            #         action_chains.click(subtype).perform()
            #         retries += 1
            
            # if error == True:
            #     continue

            # try to find elements (retry if stale)
            leagues, success = find_elements_without_stale(subtype, "./ul/li[*]/a/span")
            
            if success == False:
                errors.append(f"Etoto: '{discipline_name}/{discipline_subtype}' elements timeout")
                continue

            for league in leagues:
                # try to find discipline subtypes (retry if stale)
                subtypes, success = find_elements_without_stale(discipline[0], "./ul/li[*]")
                if success == False:
                    errors.append(f"Etoto: '{discipline_name}/{discipline_subtype}' elements timeout")
                    continue

                # activate subtype dropdown list
                success = activate_dropdown_list(action_chains, subtype)
                if success == False:
                    errors.append(f"Etoto: Unable to open subtype dropdown list [{subtype}]")
                    continue

                action_chains.click(league).perform()

                # try to find elements (retry if stale)
                elements, success = find_elements_without_stale(driver, '/html/body/div[3]/div[*]/div[1]/div[2]/div[3]/div/div/div[3]/partial[4]/div/div/div/div[2]/div[2]/div[*]/ul/li[*]/ul')
                if success == False:
                    errors.append(f"Etoto: Unable to get league elements [{league.text}]")
                    continue

                for index, element in enumerate(elements):
                    scroll_into_view(driver, elements[min(index+5, len(elements)-1)], sleep=0)

                    item = element.text.split('\n')

                    # set game datetime
                    if len(item) > 4:
                        game_datetime = get_closest_week_day(item[2]).replace('.', '-') + ' ' + item[3]   

                    # continue if gametime doesnt match regex
                    date_pattern = r"\d{2}-\d{2} \d{2}:\d{2}"
                    if not re.match(date_pattern, game_datetime):
                        errors.append("Etoto: Datetime error: " + game_datetime)
                        continue    
                    
                    if bet_outcomes == 'two-way':
                        # if invalid data - skip 
                        if len(item) < 7 or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                            errors.append("Etoto: Error appending - " + " | ".join(item))
                            continue
                        
                        # append item
                        dct = {"game_datetime": game_datetime,
                            "team_1": item[0],
                            "team_2": item[1],
                            "stake_1_wins": item[4],
                            "stake_draw": np.inf,
                            "stake_2_wins": item[5],
                            "url": url,
                            "category": category}
                        
                    elif bet_outcomes == 'three-way':
                        # if invalid data - skip 
                        if len(item) < 7 or not item[4].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric() or not item[6].replace(".", "").isnumeric():
                            errors.append("Etoto: Error appending - " + " | ".join(item))
                            continue
                        
                        # append item
                        dct = {"game_datetime": game_datetime,
                            "team_1": item[0],
                            "team_2": item[1],
                            "stake_1_wins": item[4],
                            "stake_draw": item[5],
                            "stake_2_wins": item[6],
                            "url": url,
                            "category": category}
                        

                    df = df._append(pd.DataFrame(
                        [dct], columns=columns), ignore_index=True)
                    
            # close subtype dropdown list
            retries = 0
            error = False
            try:
                while 'is-active' in subtype.get_attribute('class'):
                    if retries >= 3:
                        errors.append(f"Etoto: Unable to close subtype dropdown list [{subtype}]")
                        error = True
                        break
                    else:
                        action_chains.click(subtype).perform()
                        retries += 1
            except:
                pass
                    
        # close discipline dropdown list
        retries = 0
        error = False
        while 'is-active' in discipline[0].get_attribute('class'):
            if retries >= 3:
                errors.append(f"Etoto: Unable to close discipline dropdown list [{discipline_name}]")
                error = True
                break
            else:
                time.sleep(1)
                action_chains.click(discipline[0]).perform()
                retries += 1
        
        if error == True:
            continue
        
    # Close the WebDriver
    driver.quit()
    
    return df, errors



def activate_dropdown_list(action_chains, element):
    retries = 0
    success = True
    while not 'is-active' in element.get_attribute('class'):
        if retries >= 3:
            success = False
            break
        else:
            action_chains.click(element).perform()
            retries += 1
    
    return success


# # # test

# df = pd.DataFrame()
# df = df._append(scrape_etoto(), ignore_index=True)
# print(df.head())
