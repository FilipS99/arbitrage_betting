from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import time

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