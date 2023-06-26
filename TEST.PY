from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time
from datetime import datetime, date, timedelta
from selenium.webdriver.common.action_chains import ActionChains
import re
from typing import Tuple

from additional_functions import scroll_into_view, get_closest_week_day, find_elements_without_stale, scroll_to_end_of_page


def scrape_betclic() -> Tuple[pd.DataFrame, list]:
    # static links
    static_links = [
                ('https://www.betclic.pl/tenis-s2', 'tennis', 'two-way'),
                ('https://www.betclic.pl/rugby-xiii-s52', 'rugby', 'three-way'),
                ('https://www.betclic.pl/rugby-xv-s5', 'rugby', 'three-way'),
                ('https://www.betclic.pl/sztuki-walki-s23/ufc-c15946', 'ufc', 'two-way')
    ]

    # dynamic subclasses
    dynamic_links = [
                ('Piłka nożna', 'Polska', 'polish football', 'three-way'),
                ('Piłka nożna', 'Finlandia', 'finnish football', 'three-way'),
                ('Piłka nożna', 'Brazylia', 'brazilian football', 'three-way')
    ]

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
    # driver.implicitly_wait(1)

    driver.get('https://www.etoto.pl/')
    time.sleep(3)

    # scrape dynamic pages
    for discipline_name, discipline_subtype, category, bet_outcomes in dynamic_links:
        df_new, errors_new = scrape_discipline_subclass(driver, discipline_name, discipline_subtype, category, bet_outcomes)
        df = df._append(df_new, ignore_index=True)
        errors.extend(errors_new)
    
    # scrape static pages
    for url, category, bet_outcomes in static_links:
        # load page
        driver.get(url)
        
        scroll_to_end_of_page(driver)

        # Get the current URL, skip if redirectred
        if url != driver.current_url:
            errors.append("BetClic: URL Redirected to: " + driver.current_url)
            continue
        
        df_new, errors_new = scrape_page_items(driver, category, bet_outcomes)
        df = df._append(df_new, ignore_index=True)
        errors.extend(errors_new)

    # Close the WebDriver
    driver.quit()
    
    return df, errors


def scrape_discipline_subclass(driver, discipline_name, discipline_subtype, category, bet_outcomes):
    errors = []
    df = pd.DataFrame()
    action_chains = ActionChains(driver)

    scroll_to_end_of_page(driver)

    # try to find disciplines (retry if stale)
    disciplines = driver.find_elements(By.XPATH, "/html/body/app-desktop/div[1]/div/sports-left-menu/sports-list-menu/sports-list/div/div[2]/sports-tile[*]")

    if len(disciplines) == 0:
        errors.append(f"Betclic: no disciplines found [{discipline_name}/{discipline_subtype}]")
        return df, errors
    
    # find and filter discipline
    for index, d in enumerate(disciplines):
        scroll_into_view(driver, d, sleep=0) 
        if discipline_name == d.text.split('\n')[0]:
            discipline = d
            break
        elif index == len(disciplines)-1:
            errors.append(f"Betclic: discipline not found [{discipline_name}/{discipline_subtype}]")
            return df, errors

    # activate discipline dropdown list
    success = activate_dropdown_list(driver, action_chains, discipline)
    if success == False: 
        # refresh page on error
        driver.get('https://www.betclic.pl/')
        time.sleep(3)
        errors.append(f"Betclic: Unable to activate dropdown list [{discipline_name}/{discipline_subtype}]")
        return df, errors

    # try to find discipline subtypes 
    subtypes = discipline.find_elements(By.XPATH, ".//sports-details/div/ul/li[*]")
    
    if len(subtypes) == 0:
        errors.append(f"Betclic: '{discipline_name}/{discipline_subtype}' not found")
        return df, errors
 
    # find and filter discipline
    for index, s in enumerate(subtypes):
        scroll_into_view(driver, s, sleep=0) 
        if discipline_subtype == s.text.split('\n')[0]:
            subtype = s
            break
        elif index == len(subtypes)-1:
            errors.append(f"Betclic: Unable to find subtype ['{discipline_name}/{discipline_subtype}']")
            return df, errors

    # activate subtype dropdown list
    success = activate_dropdown_list(driver, action_chains, subtype)
    if success == False:
        errors.append(f"Betclic: Unable to open subtype dropdown list '{subtype.text}' ['{discipline_name}/{discipline_subtype}']")
        return df, errors
    
    leagues = subtype.find_elements(By.XPATH, "./ul/sports-tile[*]")
    
    if len(leagues) == 0:
        errors.append(f"Betclic: leagues '{discipline_name}/{discipline_subtype}' not found")
        return df, errors
    
    for league in leagues:
       # activate subtype dropdown list
        success = activate_dropdown_list(driver, action_chains, league)
        if success == False:
            errors.append(f"Betclic: Unable to read subtype URL ['{discipline_name}/{discipline_subtype}']")
            continue

        time.sleep(1)
        
        # new_urls.append(driver.current_url)
        df_new, errors_new = scrape_page_items(driver, category, bet_outcomes)
        df = df._append(df_new, ignore_index=True)
        errors.extend(errors_new)

    # deactivate discipline dropdown list
    success = deactivate_dropdown_list(driver, action_chains, discipline)
    if success == False: 
        # refresh page on error
        driver.get('https://www.betclic.pl/')
        time.sleep(3)
        errors.append(f"Betclic: Unable to deactivate dropdown list [{discipline_name}/{discipline_subtype}]")
        return df, errors

    return df, errors


def scrape_page_items(driver, category, bet_outcomes):
    errors = []
    df = pd.DataFrame()
    # try to find group events (retry if stale)
    group_events, success = find_elements_without_stale(driver, 'groupEvents', By.CLASS_NAME)

    if success == False:
        errors.append(f"Betclic: '{category}' elements timeout")
        return df, errors

    # loop from last to 1st event                
    for group_event in reversed(group_events):
        scroll_into_view(driver, group_event, sleep=0)

        # scrape events date (common for section)
        events_date, success = find_elements_without_stale(group_event, 'groupEvents_headTitle', By.CLASS_NAME)

        if success == False or len(events_date) == 0:
            errors.append(f"Betclic: '{category}' event element timeout")
            continue

        # manage unexpected values
        if events_date[0].text == 'Teraz':
            return df, errors           
        elif events_date[0].text == 'Dzisiaj':
            events_date = date.today().strftime("%d.%m.%Y")
        elif events_date[0].text == 'Jutro':
            events_date = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")
        elif events_date[0].text == 'Pojutrze':
            events_date = (date.today() + timedelta(days=2)).strftime("%d.%m.%Y")
        else:
            events_date = events_date[0].text

        events, success = find_elements_without_stale(group_event, 'cardEvent', By.CLASS_NAME)
        for event in reversed(events):
            scroll_into_view(driver, event, sleep=0)

            # event data
            team_1 = event.find_elements(By.XPATH, ".//*[contains(@class, 'scoreboard_contestant-1')]")
            team_2 = event.find_elements(By.XPATH, ".//*[contains(@class, 'scoreboard_contestant-2')]")
            bet_odds = event.find_elements(By.XPATH, ".//*[contains(@class, 'oddValue')]")
            event_time = event.find_elements(By.XPATH, ".//*[contains(@class, 'scoreboard_hour')]")

            # validate data
            numeric_pattern = re.compile(r'^[-+]?[0-9]+(\.[0-9]+)?$')
            if len(team_1) != 1 or len(team_2) != 1 or len(bet_odds) < 2 or len(event_time) != 1 or any(not numeric_pattern.match(element.text.replace(",", ".")) for element in bet_odds):
                errors.append("BetClic: Values not found: " + " | ".join(event.text.split('\n')))
                continue   

            # check if event datetime matches regex
            game_datetime = datetime.strptime(str(events_date) + " " + event_time[0].text, "%d.%m.%Y %H:%M").strftime("%d-%m %H:%M")
            date_pattern = r"\d{2}-\d{2} \d{2}:\d{2}"
            if not re.match(date_pattern, game_datetime):
                errors.append("BetClic: Datetime error: " + game_datetime)
                continue    
            
            if bet_outcomes == 'two-way':
                # create df row
                df_row = {"game_datetime": game_datetime,
                    "team_1": team_1[0].text,
                    "team_2": team_2[0].text,
                    "stake_1_wins": bet_odds[0].text.replace(",", "."),
                    "stake_draw": np.inf,
                    "stake_2_wins": bet_odds[1].text.replace(",", "."),
                    "url": driver.current_url,
                    "category": category
                    }
            
            elif bet_outcomes == 'three-way':
                # create df row
                df_row = {"game_datetime": game_datetime, 
                    "team_1": team_1[0].text,
                    "team_2": team_2[0].text,
                    "stake_1_wins": bet_odds[0].text.replace(",", "."),
                    "stake_draw": bet_odds[1].text.replace(",", "."),
                    "stake_2_wins": bet_odds[2].text.replace(",", "."),
                    "url": driver.current_url,
                    "category": category
                    }
            # append row
            df = df._append(pd.DataFrame([df_row]), ignore_index=True)

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


# # test

df = pd.DataFrame()
df, errors = scrape_etoto()
print(df.groupby(['category']).size())
