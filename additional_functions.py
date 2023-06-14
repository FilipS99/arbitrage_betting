import time
from datetime import datetime, timedelta

def scroll_into_view(driver, element, sleep=0):
    # Get initial element position
    initial_position = element.location["y"]

    # Scroll loop - until element is visible
    while True:
        # Scroll to the element's bottom position
        driver.execute_script("arguments[0].scrollIntoView(false);", element)
        
        # Wait for a short interval to allow content to load
        time.sleep(sleep)
        
        # Calculate the new element position after scrolling
        new_position = element.location["y"]
        
        # Break the loop if the element's position remains the same (reached the bottom)
        if new_position == initial_position:
            break
        
        # Update the last recorded position
        initial_position = new_position


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


# days_of_week1 = ['PON.', 'WT.', 'ŚR.', 'CZW.', 'PT.', 'SOB.', 'NIEDZ.', '01.10']
# for day in days_of_week1:
#     print(find_closest_week_day(day))

# print(format_date_with_zeros('4-10'))