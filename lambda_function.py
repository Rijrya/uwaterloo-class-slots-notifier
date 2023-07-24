from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


URL = "https://classes.uwaterloo.ca/under.html"
COURSE_CODE = "CS"
COURSE_NUM = "246"


def get_course_info(url=URL, code=COURSE_CODE, num=COURSE_NUM):

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(executable_path="/opt/chromedriver", chrome_options=options)
    driver.get(url)

    course_code_select = Select(driver.find_element(By.ID, "ssubject"))

    course_code_select.select_by_value(code)

    course_code_num = driver.find_element(By.ID, "icournum")
    course_code_num.send_keys(num)
    course_code_num.send_keys(Keys.ENTER)

    time.sleep(1)

    course_info = driver.find_elements(By.TAG_NAME, 'td')

    class_slots = []

    for element in course_info:
        if element.text.isnumeric() and element.text != '0':
            class_slots.append(int(element.text))

    driver.quit()
    return class_slots


def get_free_slots(class_slots):
    free_slots = []

    for i in range(len(class_slots)-7):
        if class_slots[i] == 90:
            num_free = class_slots[i] - class_slots[i+1]
            if class_slots[i+2] + class_slots[i+4] <= class_slots[i]:
                diff = class_slots[i+2] - class_slots[i+3] + class_slots[i+4] - class_slots[i+5]
                if num_free != diff:
                    free_slots.append(str(class_slots[i-2]) + " - 246")
            else:
                diff = class_slots[i+2] - class_slots[i+3]
                if num_free != diff:
                    if class_slots[i-2] == 101:
                        free_slots.append(str(class_slots[i-3]) + " - 246E")
                    else:
                        free_slots.append(str(class_slots[i - 2]) + " - 246")
    return free_slots


def lambda_handler(event, context):
    print(get_free_slots(get_course_info()))


import time

t = time.localtime()
current_hr = time.strftime("%H", t)
current_min = time.strftime("%M", t)
current_time = time.strftime("%H:%M:%S", t)
print(current_hr, current_min, type(current_hr))
message = ""
message += "bob"
message += "bob"
print(message)