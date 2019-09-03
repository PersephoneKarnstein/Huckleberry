from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from browsermobproxy import Server

import urllib, lxml, time, psutil, functools, pdb
from bs4 import BeautifulSoup

# server = Server("/usr/local/lib/python3.7/site-packages/browsermob-proxy-2.1.4/bin/browsermob-proxy") #! needs to be changed for virtualenv
# server.start()
# proxy = server.create_proxy()


# firefox_profile = webdriver.FirefoxProfile()
# firefox_profile.set_preference('permissions.default.image', 2)
# firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
# firefox_profile.set_proxy(proxy.selenium_proxy())

# driver = webdriver.Firefox(firefox_profile=firefox_profile, proxy=proxy.selenium_proxy())

#####################################################################
def clean_url(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('permissions.default.image', 2)
        firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        driver = webdriver.Firefox(firefox_profile=firefox_profile)

        func(driver, *args, **kwargs)

        # server.stop()
        driver.quit()

        return
    return wrapped

def clean_scraper(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        for proc in psutil.process_iter():
            # check whether the process name matches
            try:
                if proc.name() == "browsermob-proxy" or\
                     proc.name() == "firefox":
                    proc.kill()
            except psutil.NoSuchProcess:
                pass

        server = Server("/usr/local/lib/python3.7/site-packages/browsermob-proxy-2.1.4/bin/browsermob-proxy") #! needs to be changed for virtualenv

        server.start()
        time.sleep(1)
        proxy = server.create_proxy()
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_proxy(proxy.selenium_proxy()) #! this raises a deprecation warning but the alternative does not work.
        driver = webdriver.Firefox(firefox_profile=firefox_profile)#, proxy=proxy.selenium_proxy())
        func(proxy, driver, *args, **kwargs)

        # server.stop()
        # driver.quit()

        return
    return wrapped

#####################################################################

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


def get_hike_ids(soup, driver, total=0):
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


@clean_url
def write_state_hikes_to_file(driver, url="https://www.hikingproject.com/directory/8007121/california"):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, features="lxml")
    last_height = driver.execute_script("return document.body.scrollHeight")

    total = get_total_hikes(soup)
    get_hike_ids(soup, driver, total=total)


@clean_scraper
def get_hike_data_from_url(proxy, driver, url):#, proxy=proxy, driver=driver):
    proxy.new_har("hike")
    driver.get(url)
    element = driver.find_element_by_xpath('//*[@id="map-and-ride-finder-container"]')
    # actions = ActionChains(driver)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME , 'mapboxgl-marker')))

    print("doot")
    time.sleep(15)

    ##########
    #   ...
    ##########
    # print(proxy.har)
    entries = proxy.har['log']["entries"]
    print("-"*20)
    for entry in entries:
        if 'vector.pbf?' in entry['request']['url']:
            print(entry, "\n\n")
    

    pdb.set_trace()

url = "https://www.hikingproject.com/trail/7005207/half-dome"

get_hike_data_from_url(url)
