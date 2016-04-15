#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import dotenv
import urllib2
import argparse
from dotenv import load_dotenv
from multiprocessing import Pool
from selenium import webdriver

def login(username, password):
    browser.get('https://tutsplus.com/sign_in')
    browser.find_element_by_id('session_login').send_keys(username)
    browser.find_element_by_id('session_password').send_keys(password)
    browser.find_element_by_class_name('sign-in__button').click()

def get_course_information(course_url):
    browser.get(course_url)
    course_title = browser.find_element_by_class_name('content-header__title')
    lesson_nodes = browser.find_elements_by_class_name('lesson-index__lesson-link')

    course_title = course_title.get_attribute('innerHTML')

    lesson_urls = [
        lesson_node.get_attribute('href')
        for lesson_node in lesson_nodes
    ]
    lessons = map(get_lesson_information, lesson_urls)

    return {
        'title': course_title,
        'lessons': lessons
    }

def get_lesson_information(lesson_url):
    browser.get(lesson_url)
    title = browser.find_element_by_class_name('lesson-description__lesson-title').get_attribute('innerHTML')
    lesson_number = browser.find_element_by_class_name('lesson-index__lesson-number').get_attribute('innerHTML')
    video_url = browser.find_element_by_tag_name('source').get_attribute('src')

    return {
        'title': title,
        'lesson_number': lesson_number,
        'video_url': video_url
    }

def get_course_storage_path(base_path, course_name):
    storage_path = '{base_path}/{course_name}/'.format(base_path=base_path, course_name=course_name)

    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    return storage_path

def get_lesson_filename(course_storage_path, lesson_number, lesson_name):

    return '{course_storage_path}{lesson_number} - {lesson_name}.mp4'.format(
        lesson_number=lesson_number,
        course_storage_path=course_storage_path,
        lesson_name=lesson_name
        )

def setup_course_storage(course):
    course_storage_path = get_course_storage_path(base_path=base_path, course_name=course['title'])
    for lesson in course['lessons']:
        lesson['filename'] = get_lesson_filename(
            course_storage_path=course_storage_path,
            lesson_number=lesson['lesson_number'],
            lesson_name=lesson['title']
            )

def download_lesson(lesson):
    response = urllib2.urlopen(lesson['video_url'])
    with open(lesson['filename'], 'wb') as file:
        file.write(response.read())
        print('==> {lesson_title} downloaded successfully'.format(lesson_title=lesson['title']))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('url', help="tuts+ course url")
    args = parser.parse_args()

    course_url = args.url

    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

    username = os.environ.get('USERNAME')
    password = os.environ.get('PASSWORD')
    base_path = os.environ.get('STORAGE_PATH')

    print('=> Opening web browser...')
    browser = webdriver.Firefox()
    print('=> Logging in to the website...')
    login(username=username, password=password)
    print('=> Fetching course information...')
    course = get_course_information(course_url=course_url)
    print('=> Closing web browser...')
    browser.close()
    print('=> Setting up course storage...')
    setup_course_storage(course=course)
    print('=> Downloading lessons...')
    pool = Pool(processes=4)
    pool.map(download_lesson, course['lessons'])
    print('=> Successfully downleaded {number_of_videos} videos'.format(
        number_of_videos=len(course['lessons'])
        )
    )
