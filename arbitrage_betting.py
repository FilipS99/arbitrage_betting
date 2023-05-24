import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# chrome driver setup
options = Options()
options.add_argument("start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# load page
driver.get('https://www.sts.pl/pl/zaklady-bukmacherskie/pilka-nozna/polska/ekstraklasa/184/30860/86441/')

# handle pop-ups
allow_cookies_btn = driver.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]')
allow_cookies_btn.send_keys(Keys.ENTER)

popup_cancel_btn = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[1]/div/div[2]/div[3]/button[1]')
popup_cancel_btn.send_keys(Keys.ENTER)

# scrape
table_row = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[6]/div[5]/div[2]/div[2]/div/table[1]/tbody/tr/td[2]/table/tbody/tr')
print(table_row.text.split("\n"))  
i = 1
try:
    while(1):
        table_row = driver.find_element(By.XPATH, f'/html/body/div[5]/div[2]/div[6]/div[5]/div[2]/div[2]/div/table[{i}]/tbody/tr/td[2]/table/tbody/tr')
        print(table_row.text.split("\n"))          
        i += 1
except Exception:
    print("Kuniec")



time.sleep(100)
driver.quit()