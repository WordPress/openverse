import os
import requests as rs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


SCREEN_DIR = './screenshots'
TARGET_URL = 'https://search.creativecommons.org'
release = rs.get('https://api.creativecommons.engineering/version').json()
VERSION = release['release']
ENVIRONMENT = release['environment']
test_queries = [
    "dog",
    "DNA",
    "F14",
    "cat",
    "WW2",
    "Monet",
    "Edvard Munch",
    "flamingo",
    "weather",
    "Andrew Jackson",
    "maps of the Atlantic",
    "wildlife",
    "reading",
    "Syrian women",
    "medicine",
    "health",
    "periodic table",
    "aardvark",
    "children playing",
    "nurse",
    "basketball team",
    "music",
    "computer",
    "technology",
    "car",
    "books",
    "video",
    "beach",
    "flower",
    "food",
    "tree",
    "people",
    "nature",
    "money",
    "house",
    "school"
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
        # Scroll down so the header isn't visible.
        driver.execute_script("window.scrollTo(0, 200)")
        driver.save_screenshot(name + '.png')
        # Take a screenshot of the second page of results.
        driver.execute_script("window.scrollTo(0, 1080)")
        driver.save_screenshot(name + '_2.png')

    @staticmethod
    def test_query(driver, query):
        results_dir = os.path.join(SCREEN_DIR, '{}-{}'.format(ENVIRONMENT, VERSION))
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        driver.get(
            "{}/search?q={}".format(TARGET_URL, query)
        )
        DriverOps._screenshot(
            driver, os.path.join(results_dir, query)
        )


if not os.path.exists(SCREEN_DIR):
    os.makedirs(SCREEN_DIR)
driver = webdriver.Firefox()
driver.set_window_size(1920, 1080)
for q in test_queries:
    DriverOps.test_query(driver, q)
driver.close()
