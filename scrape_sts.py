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

    # liga 1 i 2
    urls = ['https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/1-liga/184/30860/86440/',
            'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/2-liga/184/30860/86439/',
            'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/3-liga-grupa-i/184/30860/86447/',
            'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/3-liga-grupa-ii/184/30860/86604/',
            'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/3-liga-grupa-iii/184/30860/86450/',
            'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/3-liga-grupa-iv/184/30860/86449/',
            'https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/4-liga-podkarpacka/184/30860/86664/']
    
    
    # initialize output DataFrame
    df = pd.DataFrame()
    columns = ["team_1",  "team_2", "stake_1_wins",
            "stake_draw", "stake_2_wins", "url"]
    


    # Chrome instance in nested, since STS blocks quick page changes with Captcha
    for url in urls:
        # chrome driver setup
        options = Options()
        # options.add_argument("--headless")  # opens in background
        options.add_argument("--start-maximized")
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)

        # load page
        driver.get(url)     

        # get table elements of every polish football league (on the same page)
        table_elements = driver.find_elements(By.XPATH, '/html/body/div[*]/div[2]/div[6]/div[5]/div[2]/div[2]/div/table[*]/tbody/tr/td[2]/table/tbody/tr')

        for table_element in table_elements:
            item = table_element.text.split("\n")
            # ['Nieciecza', '2.01', 'X', '3.55', 'Arka', '3.50']

            # if invalid data - skip 
            if len(item) != 6 or not item[1].replace(".", "").isnumeric() or not item[3].replace(".", "").isnumeric() or not item[5].replace(".", "").isnumeric():
                if item[0] != '':
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

    # print(f"{'STS:':<10} {len(df)}")

    return df


# # test
# # expected columns
# # ["team_1",  "team_2", "stake_1_wins", "stake_draw", "stake_2_wins", "url"]



# df = pd.DataFrame()
# df = df._append(scrape_sts(), ignore_index=True)
# print("STS STS STS", df.head())

