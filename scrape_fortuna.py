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
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/fortuna-1-liga-polska', 'polish football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/2-polska', 'polish football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-polska-grupa-i', 'polish football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-polska-grupa-ii', 'polish football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-polska-grupa-iii', 'polish football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-polska-grupa-iv', 'polish football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/1-finlandia', 'finland football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/2-finlandia', 'finland football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-finlandia-a', 'finland football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-finlandia-b', 'finland football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/pilka-nozna/3-finlandia-c', 'finland football'),
                ('https://www.efortuna.pl/zaklady-bukmacherskie/rugby', 'rugby')
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
        url, category = link

        # load page
        driver.get(url)     

        # get table elements of every polish football league (on the same page)
        table_elements = driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[2]/div[2]/div/div[3]/div[5]/section/div[2]/div/div/table/tbody/tr[*]')

        for table_element in table_elements:
            item = table_element.text.split("\n")
            # 00: ['P.Niepołomice - Ch.G... Multiliga', '1.48', '4.50', '6.70', '1.11', '2.69', '1.21', '+82', '03.06. 17:30']
            
            teams = item[0].replace(' Polsat Sport - Multiliga', '').split(' - ')

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

