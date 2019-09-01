from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import urllib, lxml, time
from bs4 import BeautifulSoup

firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

driver = webdriver.Firefox(firefox_profile=firefox_profile)


url = "https://www.hikingproject.com/directory/8007121/california"

driver.get(url)
soup = BeautifulSoup(driver.page_source, features="lxml")
last_height = driver.execute_script("return document.body.scrollHeight")

def get_total_hikes(soup):
    """Once on the page, read how many hikes it thinks there are 
        in the state and return that number"""
        
    headers = soup.select(".dont-shrink")

    for i in range(len(headers)):
        text = headers[i].get_text()
        if "Trails in California -" in text:
            return int(text.split("-")[1].strip())
        else: pass
    return 0


def get_hike_ids(soup=soup, total=0, driver=driver):
    """Because it doesn't seem like there's a consistent numbering scheme
        for how to identify the IDs of trails within a given state; 
        physically reads through the list of hikes in the state, and outputs
        a list of the url of each hike's page to file for later use."""

    found_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    try:
        while len(found_urls)<=total:
            
            all_trails = soup.select(".trail-table")[0]
            trails = all_trails.select("tr")

            for trail in trails[-50:-1]: 
                found_urls.add(trail["data-href"])
                #it only loads 20 at a time but even with the wait condition 
                # (below) it sometimes reads the list of hikes before the page has
                # finished loading new ones so for safety, we read the last two loads.

            with open("trail_urls.txt", "w+") as f:
                f.writelines(a+"\n" for a in found_urls)

            print("{0: >4g}/{1: <4g}: [{2: <20s}]".format(len(found_urls), total, \
                int(20*len(found_urls)/total)*"|"), end='\r') #progress bar

            driver.find_element_by_id("load-more-trails").click()
            
            #Wait on Scroll Increase
            #I initially wrote this for reading through Twitter without an API:
            #   essentially, it checks how far it's possible to scroll down the
            #   page (because Selenium can wait on the appearance of an object
            #   if you know what it will be called ahead of time, but in this 
            #   case we don't) and if that length increases, you know that more
            #   entries in an infinite scroll have been loaded.
            while True:
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height: 
                    time.sleep(1)
                    continue
                elif new_height > last_height: 
                    last_height = new_height
                    break
                else: raise UserWarning("It shrunk halp.")


            soup = BeautifulSoup(driver.page_source, features="lxml")
    except NoSuchElementException:
        with open("trail_urls-complete.txt", "w+") as f:
                f.writelines(a+"\n" for a in found_urls)
        print("Done.")

total = get_total_hikes(soup)
get_hike_ids(total=total)