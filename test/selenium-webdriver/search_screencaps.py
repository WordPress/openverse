import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


SCREEN_DIR = './screenshots'


test_queries = [
    "dog",
    "DNA",
    "F14",
    "cat",
    "WW2",
    "Monet",
    "Edvard Munch"
]


class DriverOps:
    @staticmethod
    def _new_tab(driver):
        driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')

    @staticmethod
    def _screenshot(driver, name):
        search_item_rendered = EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, 'search-grid_image-ctr')
        )
        WebDriverWait(driver, 10).until(search_item_rendered)
        driver.save_screenshot(name)

    @staticmethod
    def test_query(driver, query):
        driver.get(
            "https://ccsearch.creativecommons.org/search?q={}".format(query)
        )
        DriverOps._screenshot(
            driver, os.path.join(SCREEN_DIR, '{}.png'.format(query))
        )


if not os.path.exists(SCREEN_DIR):
    os.makedirs(SCREEN_DIR)
driver = webdriver.Firefox()
driver.set_window_size(1920, 1080)
for q in test_queries:
    DriverOps.test_query(driver, q)
driver.close()
