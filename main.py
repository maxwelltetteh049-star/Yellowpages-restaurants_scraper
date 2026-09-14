import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import html

options = uc.ChromeOptions()
options.binary_location = r"C:\chrome-win64\chrome.exe"              #insert location of chrome tester
options.add_argument(r"--user-data-dir=C:\maxxy_scraper")
options.add_argument("--start-maximized")

driver = uc.Chrome(options=options, version_main=150)
wait = WebDriverWait(driver, 40)


driver.get("https://www.yellowpages.com")

search_bt = wait.until(
    EC.presence_of_element_located((By.XPATH,"//input[@id='query']"))
)

endpoint = "https://www.yellowpages.com/los-angeles-ca/restaurants?page=1"

response = driver.execute_async_script(
'''
const callback = arguments[arguments.length - 1];
fetch( arguments[0], {
        method : "GET",
        credentials : "include"
    }
)
.then(response => response.text())
.then(html => callback(html))
.catch(error => error.toString(callback(error)));

''', endpoint
)

print(response)