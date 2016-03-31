import os
import sys
import time
import dotenv
import urllib2
from dotenv import load_dotenv
from multiprocessing import Pool
from os.path import join, dirname
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

if len(sys.argv) < 2:
    print 'Usage: python tutsplus_downloader.py url_to_course'
    sys.exit()

load_dotenv(join(dirname(__file__), '.env'))

username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
storage_path = os.environ.get('STORAGE_PATH')
course_url = sys.argv[1]
count = 0

browser = webdriver.Chrome()

# Login to the application
print('=> Login in to the website...')
browser.get('https://tutsplus.com/sign_in')
browser.find_element_by_id('session_login').send_keys(username)
browser.find_element_by_id('session_password').send_keys(password)
browser.find_element_by_class_name('sign-in__button').send_keys(Keys.RETURN)

# Get the data for each individual lesson
print('=> Fetching the lesson data...')
browser.get(course_url)

lesson_links = browser.find_elements_by_class_name('lesson-index__lesson-link')
lesson_links = [link.get_attribute('href') for link in lesson_links]

lesson_titles = browser.find_elements_by_class_name('lesson-index__lesson-title')
lesson_titles = [title.get_attribute('innerHTML') for title in lesson_titles]

lesson_numbers = browser.find_elements_by_class_name('lesson-index__lesson-number')
lesson_numbers = [number.get_attribute('innerHTML') for number in lesson_numbers]


# Create the course directory save to storage path variable
course_title = browser.find_element_by_class_name('content-header__title')
course_title = course_title.get_attribute('innerHTML') + '/'

storage_path = storage_path if storage_path[-1] == '/' else storage_path + '/'
storage_path += course_title + '/'

# Loop over each lesson and save each video
print('=> Retrieving the individual lesson urls...')

lessons = []

for url in lesson_links:
    video_title = lesson_numbers[count] + ' ' + lesson_titles[count]
    video_title = video_title.replace('/', '-')
    count += 1

    browser.get(url)
    time.sleep(1)

    video_url = browser.find_element_by_tag_name('source').get_attribute('src')
    file_name = storage_path + video_title + '.mp4'

    lessons.append({'url': video_url, 'file_name': file_name})

browser.close()

print('=> Creating the storage directory...')
if not os.path.exists(storage_path):
    os.makedirs(storage_path)

print "=> Downloading videos..."
def download_lesson(lesson):
    response = urllib2.urlopen(lesson['url'])
    with open(lesson['file_name'], 'wb') as file:
        file.write(response.read())

pool = Pool(processes=4)
pool.map(download_lesson, lessons)

print "=> Succesfully downloaded %d videos." % count




