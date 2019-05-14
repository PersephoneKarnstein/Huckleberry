from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

driver = webdriver.Firefox()
actions = ActionChains(driver)

url = "https://viewer.nationalmap.gov/advanced-viewer/"

driver.get(url)
iframe = driver.find_element_by_xpath('/html/body/div[2]/iframe')
driver.switch_to.frame(iframe)

time.sleep(10)

def get_elevation(lat, lon):
    lon_lat = f"{lon}, {lat}"
    driver.find_element_by_id("esri_dijit_Search_0_input").send_keys(lon_lat)
    driver.find_element_by_class_name('searchSubmit').click()    

    time.sleep(5)
    targeting_circle = driver.find_element_by_id("map_graphics_layer")
    location = targeting_circle.location

    driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[2]/div[5]').click()
    
    time.sleep(5)
    driver.find_element_by_id("activateButton").click()

    time.sleep(5)
    actions.move_to_element_with_offset(driver.find_element_by_tag_name('body'), location['x'],location['y']).click().perform()

    time.sleep(5)
    elev = driver.find_element_by_xpath("/html/body/div[2]/div/div[6]/div[2]/div/div/div[2]/div[3]/table/tr[2]/td[4]").text
    #elev is in feet

    driver.find_element_by_id("activateButton").click()

    driver.find_element_by_xpath("""/html/body/div[2]/div/div[6]/div[1]/div[2]""").click()

    print(elev)
    return elev





get_elevation(33.0015277777752445, -114.00152777781112)