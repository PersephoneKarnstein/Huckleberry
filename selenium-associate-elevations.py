from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import time

driver = webdriver.Firefox()
actions = ActionChains(driver)
wait = WebDriverWait(driver, 20)


url = "https://viewer.nationalmap.gov/advanced-viewer/"

driver.get(url)

driver.maximize_window()


iframe = driver.find_element_by_xpath('/html/body/div[2]/iframe')
driver.switch_to.frame(iframe)

# time.sleep(10)

def get_elevation(lat, lon):
    lon_lat = f"{lon}, {lat}"

    await_search = wait.until(ec.visibility_of_element_located((By.ID, "esri_dijit_Search_0_input")))
    ActionChains(driver).move_to_element(await_search).perform()


    driver.find_element_by_id("esri_dijit_Search_0_input").send_keys(lon_lat)
    driver.find_element_by_class_name('searchSubmit').click()    

    await_dot = wait.until(ec.visibility_of_element_located((By.ID, "map_graphics_layer")))
    ActionChains(driver).move_to_element(await_dot).perform()

    targeting_circle = driver.find_element_by_id("map_graphics_layer")
    location = targeting_circle.location

    top_buttons = driver.find_element_by_class_name("container-section")
    top_buttons.find_element_by_xpath(".//div[5]").click()

    # driver.find_element_by_xpath('/html/body/div[2]/div/div[4]/div[2]/div[5]').click()
    
    await_activate = wait.until(ec.visibility_of_element_located((By.ID, "activateButton")))
    ActionChains(driver).move_to_element(await_activate).click().perform()

    # driver.find_element_by_id("activateButton").click()

    time.sleep(5)
    actions.move_to_element_with_offset(driver.find_element_by_tag_name('body'), location['x'],location['y']).click().perform()

    # time.sleep(5)
    await_result = wait.until(ec.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div[6]/div[2]/div/div/div[2]/div[3]/table/tr[2]/td[4]")))
    ActionChains(driver).move_to_element(await_result).perform()

    elev = driver.find_element_by_xpath("/html/body/div[2]/div/div[3]/div[2]/div/div/div[2]/div[3]/table/tr[2]/td[4]").text
    #elev is in feet

    driver.find_element_by_id("activateButton").click()

    driver.find_element_by_xpath("""/html/body/div[2]/div/div[6]/div[1]/div[2]""").click()

    print(elev)
    return elev





get_elevation(33.0015277777752445, -114.00152777781112)