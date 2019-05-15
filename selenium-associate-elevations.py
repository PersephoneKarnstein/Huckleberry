from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time

driver = webdriver.Firefox()
actions = ActionChains(driver)
wait = WebDriverWait(driver, 40)


url = "https://viewer.nationalmap.gov/advanced-viewer/"

driver.get(url)

driver.maximize_window()


iframe = driver.find_element_by_xpath('/html/body/div[2]/iframe')
driver.switch_to.frame(iframe)

# time.sleep(10)

def get_elevation(lat, lon):
    start = time.time()

    lon_lat = f"{lon}, {lat}"

    await_search = wait.until(ec.visibility_of_element_located((By.ID, "esri_dijit_Search_0_input")))
    ActionChains(driver).move_to_element(await_search).perform()


    driver.find_element_by_id("esri_dijit_Search_0_input").send_keys(lon_lat)

    while True:
        try:
            driver.find_element_by_class_name('searchSubmit').click()    
            await_dot = wait.until(ec.visibility_of_element_located((By.ID, "map_graphics_layer")))
            ActionChains(driver).move_to_element(await_dot).perform()
        except TimeoutException:
            continue

    targeting_circle = driver.find_element_by_id("map_graphics_layer")
    location = targeting_circle.location

    top_buttons = driver.find_element_by_class_name("container-section")
    top_buttons.find_element_by_xpath(".//div[5]").click()

    # driver.find_element_by_xpath('/html/body/div[2]/div/div[4]/div[2]/div[5]').click()
    
    await_activate = wait.until(ec.visibility_of_element_located((By.ID, "activateButton")))
    ActionChains(driver).move_to_element(await_activate).click().perform()

    # driver.find_element_by_id("activateButton").click()
    heard_click = False

    while not heard_click:
        actions.move_to_element_with_offset(driver.find_element_by_tag_name('body'), location['x'],location['y']).click().perform()
        try :
            await_elev_popup = WebDriverWait(driver, 5).until(ec.visibility_of_element_located((By.CLASS_NAME, 'esriPopupWrapper')))
            ActionChains(driver).move_to_element(await_elev_popup).perform()
            heard_click = True

            while True:
                try:
                    elev_popup = driver.find_element_by_class_name('esriPopupWrapper')
                    elev = elev_popup.find_element_by_xpath(".//div[2]/div").text
                    break
                except NoSuchElementException:
                    time.sleep(1)

            break
        except TimeoutException:
            continue

    elev = float(elev.split()[1])
    #elev is in feet

    driver.find_element_by_id("activateButton").click()

    driver.find_element_by_id("esri_dijit_Search_0_input").clear()

    end = time.time()

    print(f"Elevation: {elev} ft.\nTime Elapsed: {end-start} seconds\n\n")
    return elev





get_elevation(41.95892, -123.06559)
get_elevation(41.95215, -123.09822)
get_elevation(41.93846, -123.11554)
get_elevation(41.69175, -123.17024)
get_elevation(41.5699, -123.1179)
get_elevation(41.56131, -123.20909)
get_elevation(41.4207, -123.2231)