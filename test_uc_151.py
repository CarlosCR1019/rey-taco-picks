import undetected_chromedriver as uc

try:
    options = uc.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = uc.Chrome(version_main=151, options=options)
    print("UC Connected to port 9222 successfully!")
    print("Title:", driver.title)
    print("URL:", driver.current_url)
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        print(f"Tab: {driver.title} | {driver.current_url}")
    driver.quit()
except Exception as e:
    print("UC Error:", e)
