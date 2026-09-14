from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from helpers import Helper
import mysql.connector
from lxml import html
import time, random
import logging
import csv

#=============== objects ================
helper = Helper()
logging.basicConfig(level=logging.INFO)


#================ MYSQL CONNECTOR ==============
conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "passworDmax15$",
    database = "webscraping_db"
)
cursor = conn.cursor()

#=============== Extract function =================
def safe_find(con, xpathh):
    try:
        return con.xpath(xpathh)[0]
    except:
        return None

#=============== SCRAPING PROCESS START ==================

driver, wait = helper.open_browser()

driver = helper.load_site(driver, "https://www.yellowpages.com")
search_bt = wait.until(
    EC.presence_of_element_located((By.XPATH,"//input[@id='query']"))
)

page = 1
pages = 10
while page <= pages:
    logging.info(f"Starting Page {page}")
    endpoint = f"https://www.yellowpages.com/los-angeles-ca/restaurants?page={page}"

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

    tree = html.fromstring(response)
    logging.info(f"Response gotten for Page {page}")

    container = tree.xpath("//div[@class='v-card']")

    for index in range(len(container)):
        try:
            con = container[index]
        except IndexError:
            print("Index out of range, breaking loop.")
            break
        name = safe_find(con, ".//a[@class='business-name']//text()")
        phone = safe_find(con, ".//div[contains(@class,'phone')]//text()")
        location = safe_find(con, ".//div[@class='street-address']//text()")
        website = safe_find(con, ".//a[@class='track-visit-website']//@href")
        listing_url = safe_find(con, ".//a[@class='business-name']//@href")
        if location is None:
            continue
        info = (name, phone, location, website, listing_url)


        query = '''
INSERT IGNORE INTO yellow(namee, phone, location, website, listing_url)
VALUES(%s, %s, %s, %s, %s)
'''
        cursor.execute(query, info)
        conn.commit()
        print(f"business info {index + 1} added")

    if page == pages:
        logging.info("Pages to be scraped is Reached")
        break

    time.sleep(random.uniform(2.5, 5.5))
    page += 1

query1 = "SELECT * FROM yellow"
cursor.execute(query1)
data = cursor.fetchall()

with open("restuarants.csv", "w", newline="", encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Business Name", "Phone", "Location(Los angeles)", "Website", "Listing_URL"])
    writer.writerows(data)

logging.info("SCRAPING IS SUCCESSFUL")
