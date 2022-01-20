import datetime
import logging
import sys
import time
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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

# Number of attempts
attempt_num = 5

# Class session length (minute)
length = 95

# If Meet people number is below [ exit_threshold ],
# [ count_to_exit ] will decrement by 1 in every [ message_interval ] seconds.
exit_threshold = 14
count_to_exit = 2

# People number detection and system message interval (seconds)
message_interval = 30

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
driver.implicitly_wait(10)


# Open the objective Classroom page
def open_class(sub):
    logger.info("Opening Google Classroom...")
    driver.get(url)
    logger.info("Current page: " + driver.current_url)
    logger.info("Searching the classrooms for [ " + sub + " ]...")
    driver.find_element(By.PARTIAL_LINK_TEXT, sub).click()
    logger.info(
        "Found a classroom named [ " + driver.find_element(By.PARTIAL_LINK_TEXT, sub).text.replace("\n", " ") + " ].")
    logger.info("Current page: " + driver.current_url)


# Join the Google Meet session
def meet_join():
    logger.info("Joining Google Meet...")
    try:
        driver.find_element(By.XPATH, '//a[@aria-label="参加"]').click()
        logger.info("Opened a meet page by 'Join' button.")
    except:
        driver.find_element(By.PARTIAL_LINK_TEXT, "meet.google.com").click()
        logger.warning("Couldn't find the 'Join' button. Opened the page from another URL. The URL may be wrong.")
    # Move to the rightmost tab
    driver.switch_to.window(driver.window_handles[-1])
    logger.info("Current page: " + driver.current_url)
    time.sleep(2)
    try:
        # 右が使用不可のため生のXPATHで取得 driver.find_element(By.XPATH, "//span[contains(text(), '閉じる')]").click()
        driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/div[3]/div/div[2]/div[3]/div/span/span').click()
    finally:
        time.sleep(2)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        driver.find_element(By.XPATH, "//span[contains(text(), '参加')]").click()
    time.sleep(1)
    end_date = datetime.datetime.now() + datetime.timedelta(minutes=length)
    logger.info("Joined the class. End time will be " + end_date.strftime("%Y/%m/%d %H:%M:%S"))


# Quit meet session
def quit_meet():
    logger.info("Quitting process...")
    try:
        # Push exit button
        driver.find_element(
            By.XPATH,
            '//*[@id="ow3"]/div[1]/div/div[9]/div[3]/div[10]/div[2]/div/div[7]/span/button'
        ).click()
        time.sleep(2)
    finally:
        driver.quit()


def restart_script():
    logger.info("Some error has occurred. Automatically restarting script.")
    driver.quit()
    time.sleep(5)
    os.system("python open.py " + sys.argv[1])
    sys.exit()


# If you have to log in to the Google Account
def login():
    driver.get(login_url)
    driver.find_element(
        By.XPATH,
        '//*[@id="identifierId"]'
    ).send_keys(email + "\n")
    driver.find_element(
        By.XPATH,
        '//*[@id="password"]/div[1]/div/div[1]/input'
    ).send_keys(passwd + "\n")


# Execute
for i in range(attempt_num):
    try:
        open_class(subject)
        break
    except:
        logger.warning("Exception occurred while opening classroom page. Retrying... (attempt {})".format(i + 1))
        if i == attempt_num - 1:
            logger.warning("Classroom search failed. Closing Chrome App.")
            driver.quit()
            sys.exit()

for i in range(attempt_num):
    try:
        meet_join()
        break
    except:
        logger.warning("Exception occurred while Joining meet session. Retrying... (attempt {})".format(i + 1))
        driver.switch_to.window(driver.window_handles[0])
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        if i == attempt_num - 1:
            logger.warning("Meet join failed. Closing Chrome App.")
            driver.quit()
            sys.exit()


# Timer
joined_time = time.time()
sec_time = time.time() - joined_time
count_flag = count_to_exit

while True:
    time.sleep(1)
    ela_time = time.time() - joined_time

    try:
        if ela_time > sec_time + message_interval:
            mins = ela_time / 60
            person_count = driver.find_element(
                By.XPATH,
                '//*[@id="ow3"]/div[1]/div/div[9]/div[3]/div[10]/div[3]/div[3]/div/div/div[2]/div/div'
            ).text
        if person_count.isdecimal() is False:
            person_count = driver.find_element(
                By.XPATH,
                '//*[@id="ow3"]/div[1]/div/div[9]/div[3]/div[10]/div[3]/div[3]/div/div/div[2]/div/div'
            ).text
    except:
        restart_script()

    person_count = re.sub(r"\D", "", person_count)

    logger.info('{:.0f}'.format(mins) + "/" + str(length) + " min passed. People count: " + person_count + ".")
    sec_time = ela_time
    if person_count.isdecimal() is True:
        if int(person_count) > exit_threshold:
            if count_flag != count_to_exit:
                count_flag = count_to_exit
            pass
        else:
            count_to_exit -= 1
            logger.warning("No Meet activities. Exit in " + str(count_to_exit + 1) + ".")

    if count_to_exit == 0:
        quit_meet()
        break

    if ela_time > length * 60:
        logger.info(str(length) + " min timer reached")
        quit_meet()
        break

sys.exit()
