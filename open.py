import datetime
import logging
import sys
import time
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config

# Import arguments from config.py file
email = config.EMAIL_ADDRESS
passwd = config.PASSWORD
url = config.URL
# subject = config.SUBJECT_NAME

# Import arguments from argv
subject = sys.argv[1]


########################################################################
# Configuration
########################################################################

# Class session length (minute)
length = 92

# If Meet people number is below [ exit_threshold ], count will decrease 1 by a minute.
exit_threshold = 14
count_to_exit = 3

# People number detection and system message interval (seconds)
message_interval = 10

# Logfile location
logfileDir = './logs/'

# Google login page URL
login_url = "https://accounts.google.com/signin/v2/identifier?hl=ja&passive=true&continue=https%3A%2F%2Fwww.google" \
            ".com%2F%3Fhl%3Dja&ec=GAZAmgQ&flowName=GlifWebSignIn&flowEntry=ServiceLogin "


# Chrome configurations
# 1 - Profile
driver_location = ".\\chromedriver.exe"
profile_path = "C:\\ChromeProfiles\\Automation"
profile_dir = "Default"

opt = Options()
opt.add_argument("start-maximized")
opt.add_argument("--user-data-dir=" + profile_path)
opt.add_argument("--profile-directory=" + profile_dir)

# 2 - Permission
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_mic": 2,
    "profile.default_content_setting_values.media_stream_camera": 2,
    "profile.default_content_setting_values.geolocation": 2,
    "profile.default_content_setting_values.notifications": 2
})
########################################################################
########################################################################


# Create logfile directory if not exists
if not os.path.exists(logfileDir):
    os.makedirs(logfileDir)


# Logger
logger = logging.getLogger('AutoMeetJoin')
logger.setLevel(20)

sh = logging.StreamHandler()
fh = logging.FileHandler('logs/{:%Y-%m-%d-%H-%M-%S}.log'.format(datetime.datetime.now()))
logger.addHandler(sh)
logger.addHandler(fh)

formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
fh.setFormatter(formatter)
sh.setFormatter(formatter)


# Launch chrome
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(30)


# Move to objective website
def classroom(sub):
    url_pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    logger.info("Opening Google Classroom...")
    driver.get(url)
    logger.info("Searching the classrooms for [ " + sub + " ]...")
    driver.find_element_by_partial_link_text(sub).click()
    logger.info(
        "Found a classroom named [ " + driver.find_element_by_partial_link_text(sub).text.replace("\n", " ") + " ].")
    meet_url = driver.find_element_by_partial_link_text("meet.google.com").text
    meet_url = re.findall(url_pattern, meet_url)
    meet_url = "".join(meet_url)
    logger.info("Target Google Meet URL: " + meet_url)
    return meet_url


# Join Google Meet session
def meetJoin(target_url):
    driver.execute_script("window.open('about:blank','second_tab');")
    driver.switch_to.window("second_tab")
    driver.get(target_url)
    time.sleep(3)
    driver.find_element_by_xpath(
        '//*[@id="yDmH0d"]/div[3]/div/div[2]/div[3]/div/span/span').click()
    time.sleep(1)
    driver.find_element_by_xpath(
        '//*[@id="yDmH0d"]/c-wiz/div/div/div[9]/div[3]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]/div['
        '1]/span/span'
    ).click()
    end_date = datetime.datetime.now() + datetime.timedelta(minutes = length)
    logger.info("Joined the class. End time will be " + end_date.strftime("%Y/%m/%d %H:%M:%S"))


# If you have to login to the Google Account
def login():
    driver.get(login_url)
    driver.find_element_by_xpath(
        '//*[@id="identifierId"]'
    ).send_keys(email + "\n")
    driver.find_element_by_xpath(
        '//*[@id="password"]/div[1]/div/div[1]/input'
    ).send_keys(passwd + "\n")


# Execute
# login()
session_url = classroom(subject)
meetJoin(session_url)

# Timer
joined_time = time.time()
sec_time = time.time() - joined_time
countFlag = count_to_exit

while True:
    time.sleep(1)
    ela_time = time.time() - joined_time

    if ela_time > sec_time + message_interval:
        mins = ela_time / 60
        person_count = driver.find_element_by_xpath(
            '//*[@id="ow3"]/div[1]/div/div[9]/div[3]/div[1]/div[3]/div/div[2]/div[1]/span/span/div/div/span[2]'
        ).text
        if person_count.isdecimal() is False:
            person_count = driver.find_element_by_xpath(
                '//*[@id="ow3"]/div[1]/div/div[9]/div[3]/div[4]/div/div[2]/div[2]/div[1]/div[1]/span/div/span'
            ).text
        person_count = re.sub(r"\D", "", person_count)

        logger.info('{:.0f}'.format(mins) + "/" + str(length) + " min passed. People count: " + person_count + ".")
        sec_time = ela_time
        if person_count.isdecimal() is True:
            if int(person_count) > exit_threshold:
                if countFlag != count_to_exit:
                    countFlag = count_to_exit
                pass
            else:
                count_to_exit -= 1
                logger.warning("No Meet activities. Exit in " + str(count_to_exit + 1) + ".")

    if count_to_exit == 0:
        logger.info("Quitting process...")
        driver.quit()
        break

    if ela_time > length * 60:
        logger.info(str(length) + " min timer reached")
        logger.info("Quitting process...")
        driver.find_element_by_xpath(
            '//*[@id="ow3"]/div[1]/div/div[9]/div[3]/div[9]/div[2]/div[2]/div'
        ).click()
        time.sleep(3)
        driver.quit()
        break
