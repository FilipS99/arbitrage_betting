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


def scrape_sts() -> pd.DataFrame():
    # chrome driver setup
    options = Options()
    # options.add_argument("--headless")  # opens in background
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    # liga 1 i 2
    urls = ['https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/1-liga/184/30860/86440/']
            # ,'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/2-liga/184/30860/86439/']
    
    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url"]
    
    for url in urls:
        # load page
        driver.get(url)     

        # get table elements of every polish football league (on the same page)
        table_elements = driver.find_elements(
                        By.CLASS_NAME, 'col3')

        first_item = True
        for table_element in table_elements:
            # split row into seperate items  
            if not first_item:
                item = table_element.text.split("\n")[1:]
            else:
                item = table_element.text.split("\n")[2:]
                first_item = False
            # ['17:30', 'Nieciecza', '2.01', 'X', '3.55', 'Arka', '3.50', '96']
            # ['17:30', 'Nieciecza', '2.01', 'X', '3.55', 'Arka', '3.50', '96']

            # if invalid data - skip 
            if len(item) < 6 or not item[1].replace(".", "").isnumeric() or not item[3].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                print("STS: Error appending - " + " | ".join(item))
                continue

            # append item
            dct = {"team_1": item[0],
                    "team_2": item[4],
                    "stake_1_wins": item[1],
                    "stake_draw": item[3],
                    "stake_2_wins": item[5],
                    "url": url}
            df = df._append(pd.DataFrame(
                [dct], columns=columns), ignore_index=True)

    # close chrome
    driver.quit()

    print(f"{'STS:':<10} {len(df)}")

    return df


# # test
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]



# df = pd.DataFrame()
# df = df._append(scrape_sts(), ignore_index=True)
# print("STS STS STS", df.head())

