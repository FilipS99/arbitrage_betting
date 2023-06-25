import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By

def scroll_into_view(driver, element, sleep=0):
    # Get initial element position
    initial_position = element.location["y"]
    try:
        # Scroll loop - until element is visible
        while True:
            # Scroll to the element's bottom position
            # driver.execute_script("arguments[0].scrollIntoView(false);", element)   
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", element)                 
            
            # Wait for a short interval to allow content to load
            time.sleep(sleep)
            
            # Calculate the new element position after scrolling
            new_position = element.location["y"]
            
            # Break the loop if the element's position remains the same (reached the bottom)
            if new_position == initial_position:
                break
            
            # Update the last recorded position
            initial_position = new_position
    
    except Exception:
        pass


def get_closest_week_day(weekday):
    days_of_week = ['PON.', 'WT.', 'ŚR.', 'CZW.', 'PT.', 'SOB.', 'NIEDZ.']

    today = datetime.now().date()  # Get the current date

    closest_days = {}
    
    if weekday in days_of_week:
        target_day = days_of_week.index(weekday)
        
        if today.weekday() == target_day:
            return today.strftime("%d.%m")
        else:
            days_ahead = (target_day - today.weekday()) % 7
            return (today + timedelta(days=days_ahead)).strftime("%d.%m")
        
    elif weekday.upper() == 'Dzisiaj'.upper():
        return datetime.now().strftime("%d.%m")
    
    elif weekday.upper() == 'Jutro'.upper():
        return (datetime.now() + timedelta(days=1)).strftime("%d.%m")
    
    else: 
        return weekday


def format_date_with_zeros(date_string): 
    parts = date_string.split("-")
    day = parts[0].zfill(2)
    month = parts[1]

    return day + "-" + month


def find_elements_without_stale(source, xpath, by=By.XPATH, max_retries=5, retry_count=0):
    success = True
    # get discipline elements
    while retry_count < max_retries:
        try:
            elements = source.find_elements(by, xpath) 
            for element in elements:
                element.get_attribute('class')
            break
        except Exception:
            time.sleep(1)
            # Increment the retry count
            retry_count += 1
            if retry_count < max_retries:
                # get discipline elements
                elements = source.find_elements(by, xpath) 
            else:
                success = True
                break

    return elements, success


def scroll_to_end_of_page(driver):
    # Scroll to the end of the page
    while True:
        # Get the current scroll height
        prev_scroll_height = driver.execute_script("return document.body.scrollHeight")

        # Scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the page to load new content
        # You may need to adjust the sleep duration based on your page
        time.sleep(0.25)

        # Get the new scroll height after scrolling
        new_scroll_height = driver.execute_script("return document.body.scrollHeight")

        # Check if the scroll height remains the same, indicating that we have reached the end
        if new_scroll_height == prev_scroll_height:
            break


# days_of_week1 = ['PON.', 'WT.', 'ŚR.', 'CZW.', 'PT.', 'SOB.', 'NIEDZ.', '01.10']
# for day in days_of_week1:
#     print(find_closest_week_day(day))

# print(format_date_with_zeros('4-10'))