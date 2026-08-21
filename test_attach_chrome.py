import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=options)
    print("Selenium Connected to active Chrome window!")
    print("Current URL:", driver.current_url)
    print("Page Title:", driver.title)
    driver.quit()
except Exception as e:
    print("Selenium Error:", e)
