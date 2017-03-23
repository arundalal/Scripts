#!/usr/bin/env python
##Youtube link https://www.youtube.com/watch?v=7Qp5vcuMIlk&list=PLaq655wqcKDnUvTOizhqwNCiiF_grL1vh
##Downloader link https://www.onlinevideoconverter.com/video-converter

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.PhantomJS()
driver.get("https://www.onlinevideoconverter.com/video-converter")
elem = driver.find_element_by_name("texturl")
elem.clear()
elem.send_keys("https://www.youtube.com/watch?v=7Qp5vcuMIlk&list=PLaq655wqcKDnUvTOizhqwNCiiF_grL1vh")
elem.send_keys(Keys.RETURN)
element = WebDriverWait(driver, 10).until(
        EC.title_is("Your conversion is completed - OnlineVideoConverter.com")
    )
print element.get_attribute("title")
eleme = driver.find_element_by_id("downloadq")
print downelem.get_attribute("href")
