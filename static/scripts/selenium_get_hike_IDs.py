from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import requests, urllib, lxml, time #, ast, re #json
from bs4 import BeautifulSoup

driver = webdriver.Firefox()
actions = ActionChains(driver)
wait = WebDriverWait(driver, 40)


url = "https://www.hikingproject.com/directory/8007121/california"

driver.get(url)
soup = BeautifulSoup(driver.page_source, features="lxml")
last_height = driver.execute_script("return document.body.scrollHeight")

def get_total_hikes(soup):
    headers = soup.select(".dont-shrink")
    for i in range(len(headers)):
        text = headers[i].get_text()
        if "Trails in California -" in text:
            return int(text.split("-")[1].strip())
        else: pass
    return 0

def get_hike_ids(soup=soup, total=0, driver=driver):
    found_urls = set()
    while len(found_urls)<=total:
        all_trails = soup.select(".trail-table")[0]
        trails = all_trails.select("tr")
        for trail in trails[-5s0:-1]:
            found_urls.add(trail["data-href"])
        with open("trail_urls.txt", "w+") as f:
            f.writelines(a+"\n" for a in found_urls)
        print(f"{len(found_urls)}/{total}\r")
        driver.find_element_by_id("load-more-trails").click()
        
        #! scrollability timer
        while True:
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: 
                time.sleep(1)
                continue
            elif new_height > last_height: break
            else: raise UserWarning("It shrunk halp.")

        soup = BeautifulSoup(driver.page_source, features="lxml")


total = get_total_hikes(soup)
get_hike_ids(total=total)