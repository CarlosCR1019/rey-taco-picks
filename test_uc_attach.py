import undetected_chromedriver as uc

try:
    options = uc.ChromeOptions()
    # attach to debugger
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = uc.Chrome(options=options)
    print("UC Connected!")
    print("Title:", driver.title)
    print("URL:", driver.current_url)
    driver.quit()
except Exception as e:
    print("UC Error:", e)
