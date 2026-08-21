import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By

options = uc.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = uc.Chrome(version_main=151, options=options)
print("Connected to Chrome! Available tabs:")

target_handle = None
for handle in driver.window_handles:
    driver.switch_to.window(handle)
    url = driver.current_url
    title = driver.title
    print(f" - [{handle}] {title} -> {url}")
    if "facebook.com" in url or "developers" in url:
        target_handle = handle

if target_handle:
    driver.switch_to.window(target_handle)
    print(f"\nSwitched to Facebook tab: {driver.title} ({driver.current_url})")
else:
    print("\nOpening Graph API Explorer...")
    driver.get("https://developers.facebook.com/tools/explorer/")
    time.sleep(3)

print("Current active page:", driver.title, driver.current_url)
