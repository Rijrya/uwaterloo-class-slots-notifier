from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import base64
from urllib import request, parse

courses = [{"URL": "https://classes.uwaterloo.ca/under.html",
            "COURSE_CODE": "CS",
            "COURSE_NUM": "246",
            "COURSE": "CS246"},
           {"URL": "https://classes.uwaterloo.ca/under.html",
            "COURSE_CODE": "ENGL",
            "COURSE_NUM": "108D",
            "COURSE": "ENGL108D"}]


TWILIO_SMS_URL = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")


def get_course_info(url, code, num):

    # for the AWS Lambda function
    # options = Options()
    # options.binary_location = '/opt/headless-chromium'
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--single-process')
    # options.add_argument('--disable-dev-shm-usage')
    #
    # driver = webdriver.Chrome('/opt/chromedriver', chrome_options=options)

    # for testing
    driver = webdriver.Chrome()

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

    driver.close()
    driver.quit()
    return class_slots


def get_free_slots(class_slots, course):
    free_slots = []

    ################################################################################################################

    # For CS246
    if course == "CS246":
        for i in range(len(class_slots)):
            if class_slots[i] == 201:
                num_free = class_slots[i + 1] - class_slots[i + 2]
                if class_slots[i + 3] + class_slots[i + 5] <= class_slots[i]:
                    diff = class_slots[i + 3] - class_slots[i + 4] + class_slots[i + 5] - class_slots[i + 6]
                    if num_free > diff:
                        num_slots_free = str(num_free - diff)
                        free_slots.append(str(class_slots[i - 1]) + "-246: " + num_slots_free + " slots")
                else:
                    diff = class_slots[i + 3] - class_slots[i + 4]
                    if num_free > diff:
                        if class_slots[i - 1] == 101:
                            pass
                            # No more 246E needed
                            # num_slots_free = str(num_free - diff)
                            # free_slots.append(str(class_slots[i - 2]) + "-246E: " + num_slots_free + " slots")
                        else:
                            num_slots_free = str(num_free - diff)
                            free_slots.append(str(class_slots[i - 1]) + "-246: " + num_slots_free + " slots")

    ################################################################################################################

    # For ENGL108D
    elif course == "ENGL108D":
        for i in range(len(class_slots)):
            if class_slots[i] < 6 and class_slots[i-1] > 2000:
                num_free = class_slots[i+1] - class_slots[i+2]
                if i+3 < len(class_slots) and class_slots[i+3] < 9:
                    num_free = num_free - (class_slots[i+3] - class_slots[i+4])
                if num_free > 0:
                    free_slots.append(str(class_slots[i]) + "-108D: " + str(num_free) + " slots")

    return free_slots


def twilio_handler(message):
    to_numbers = os.environ.get("to_numbers").split(",")
    from_number = os.environ.get("from_number")
    body = message

    # insert Twilio Account SID into the REST API URL
    populated_url = TWILIO_SMS_URL.format(TWILIO_ACCOUNT_SID)

    for to_number in to_numbers:
        post_params = {"To": to_number, "From": from_number, "Body": body}

        # encode the parameters for Python's urllib
        data = parse.urlencode(post_params).encode()
        req = request.Request(populated_url)

        # add authentication header to request based on Account SID + Auth Token
        authentication = "{}:{}".format(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        base64string = base64.b64encode(authentication.encode('utf-8'))
        req.add_header("Authorization", "Basic %s" % base64string.decode('ascii'))

        try:
            # perform HTTP POST request
            with request.urlopen(req, data) as f:
                print("Twilio returned {}".format(str(f.read().decode('utf-8'))))
        except Exception as e:
            # something went wrong!
            return e

    return "SMS sent successfully!"


def lambda_handler(event, context):

    results = []

    for i, course_params in enumerate(courses):
        results.extend(get_free_slots(
            get_course_info(url=courses[i]["URL"],
                            code=courses[i]["COURSE_CODE"],
                            num=courses[i]["COURSE_NUM"]),
            course=courses[i]["COURSE"]))

    # CURRENTLY SET FOR EDT TIME
    t = time.localtime()
    current_hr = time.strftime("%H", t)
    current_min = time.strftime("%M", t)
    start_day = False
    end_day = False
    send_message = False

    message = ""
    if current_hr == "14":
        if current_min == "32" or current_min == "33":
            message = "Start of day report \n\n"
            start_day = True
    elif current_hr == "02":
        if current_min == "32" or current_min == "33":
            message = "End of day report \n\n"
            end_day = True


    if start_day or end_day and results[0]:
        message += "Sections with available slots: \n\n"
        for section in results:
            message += section + "\n\n"
    elif results[0]:
        message += "NEW FREE SLOTS FOUND IN: \n\n"
        for section in results:
            if "E" not in section and "2-108D" not in section:
                message += section + "\n\n"
                send_message = True

    if send_message or start_day or end_day:
        twilio_handler(message)
    else:
        return



