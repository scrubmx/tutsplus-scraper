import os
import time
import dotenv
import urllib2
from dotenv import load_dotenv
from os.path import join, dirname
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

browser = webdriver.Chrome()

# Login to the application
browser.get('https://tutsplus.com/sign_in')
browser.find_element_by_id('session_login').send_keys(os.environ.get('USERNAME'))
browser.find_element_by_id('session_password').send_keys(os.environ.get('PASSWORD'))
browser.find_element_by_class_name('sign-in__button').send_keys(Keys.RETURN)

# Get the individual lessons url's
browser.get('https://code.tutsplus.com/courses/get-started-with-ruby-on-rails')
lesson_elements = browser.find_elements_by_class_name('lesson-index__lesson-link')
lesson_urls = [link.get_attribute('href') for link in lesson_elements]

for url in lesson_urls:
    browser.get(url)
    time.sleep(1)

    video_url = browser.find_element_by_tag_name('source').get_attribute('src')

    breadcrumb = browser.find_elements_by_class_name('breadcrumbs-bar__item')[-1]
    video_title = breadcrumb.get_attribute('innerHTML')

    directory = os.environ.get('DIRECTORY') or '/'
    directory = directory if directory[-1] == '/' else directory + '/'
    file_name = directory + video_title + '.mp4'

    response = urllib2.urlopen(video_url)

    with open(file_name, 'wb') as file:
        file.write(response.read())

browser.close()
