from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time

# import CalFlora_post_request

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
    # print(1)
    # input("Press enter.")
    #wait until the search bar is visible and then search for the latitude and longitude in question
    await_search = wait.until(ec.visibility_of_element_located((By.ID, "esri_dijit_Search_0_input")))
    ActionChains(driver).move_to_element(await_search).perform()

    # print(2)
    # input("Press enter.")
    driver.find_element_by_id("esri_dijit_Search_0_input").send_keys(lon_lat)
    # print(3)
    # input("Press enter.")
    while True:
        try:
            driver.find_element_by_class_name('searchSubmit').click()
            # Sometimes it doesn't seem to capture the submit click on the first try. If it doesn't
            # -- which Selenium will know because it doesn't place a dot on the map -- try clicking agian.
            # print(4)
            # input("Press enter.")
            await_dot = wait.until(ec.visibility_of_element_located((By.ID, "map_graphics_layer")))
            ActionChains(driver).move_to_element(await_dot).perform()
            break
        except TimeoutException:
            continue
    # print(5)
    # input("Press enter.")

    #figure out where the dot it just put on the map is.
    targeting_circle = driver.find_element_by_id("map_graphics_layer")
    location = targeting_circle.location

    # print(6)
    # input("Press enter.")
    #find the "Spot Elevation" button on the top bar and click on it
    top_buttons = driver.find_element_by_class_name("container-section")
    top_buttons.find_element_by_xpath(".//div[5]").click()

    # print(7)
    # input("Press enter.")
    #wait until the "Activate" button for Spot Elev shows up, and click on it.
    while True:
        try:
            await_activate = wait.until(ec.visibility_of_element_located((By.ID, "activateButton")))
            ActionChains(driver).move_to_element(await_activate).click().perform()
            break
        except TimeoutException:
            top_buttons.find_element_by_xpath(".//div[5]").click()
            continue

    # print(8)
    # input("Press enter.")

    heard_click = False

    while not heard_click:
        # **should** just click on the same point as we had previously, but seems to be moving the map again? 
        actions.move_to_element_with_offset(driver.find_element_by_tag_name('body'), location['x'],location['y']).click().perform()
        try :
            # print(9)
            # input("Press enter.")
            await_elev_popup = WebDriverWait(driver, 2).until(ec.visibility_of_element_located((By.CLASS_NAME, 'esriPopupWrapper')))
            ActionChains(driver).move_to_element(await_elev_popup).perform()
            heard_click = True
            # print(10)
            # input("Press enter.")
            while True:
                try:
                    # print(11)
                    # input("Press enter.")
                    elev_popup = driver.find_element_by_class_name('esriPopupWrapper')
                    elev = elev_popup.find_element_by_xpath(".//div[2]/div").text
                    break
                except NoSuchElementException:
                    time.sleep(1)

            break
        except TimeoutException:
            continue

    got_lat, got_lon = elev.split()[9:11]
    elev = float(elev.split()[1])
    #elev is in feet

    driver.find_element_by_id("activateButton").click()
    # driver.find_element_by_xpath("/html/body/div[2]/div/div[3]/div[1]/div[2]").click()
    elev_panel = driver.find_element_by_id("widgets_SpotElevation_Widget_20_panel")
    elev_panel.find_element_by_xpath(".//div[1]/div[2]").click()

    # //*[@id="widgets_SpotElevation_Widget_20_panel"]
    # /html/body/div[2]/div/div[3]/div[1]/div[2]
    # /html/body/div[2]/div/div[1]/div[10]
    # /html/body/div[2]/div/div[1]/div[10]/div[1]/div[2]

    driver.find_element_by_id("esri_dijit_Search_0_input").clear()

    end = time.time()

    if __name__ == "__main__":
        print(f"Elevation: {elev} ft.\nLooking for {lat}, {lon};\nFound {got_lat}, {got_lon}\nTime Elapsed: {end-start} seconds\n\n")
   
    return elev





# get_elevation(41.95892, -123.06559)
# get_elevation(41.95215, -123.09822)
# get_elevation(41.93846, -123.11554)
# get_elevation(41.69175, -123.17024)
# get_elevation(41.5699, -123.1179)
# get_elevation(41.56131, -123.20909)
# get_elevation(41.4207, -123.2231)