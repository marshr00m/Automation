from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time, datetime, sys, config

# Import arguments from config.py file
email = config.EMAIL_ADDRESS
passwd = config.PASSWORD
url = config.URL
#subject = config.SUBJECT_NAME

#Import arguments from argv
subject = sys.argv[1]

########################################################################
########################################################################
####                        Configuration                           ####
########################################################################
########################################################################

# Class session length (minute)
length = 92

# Define locations
driver_location = ".\chromedriver.exe"
profile_path = "C:\\ChromeProfiles\\Automation"
profile_dir = "Default"

# Google login page URL
login_url = "https://accounts.google.com/signin/v2/identifier?hl=ja&passive=true&continue=https%3A%2F%2Fwww.google.com%2F%3Fhl%3Dja&ec=GAZAmgQ&flowName=GlifWebSignIn&flowEntry=ServiceLogin"

# Chrome configurations
# 1 - Profile
opt = Options()
opt.add_argument("start-maximized")
opt.add_argument("--user-data-dir=" + profile_path)
opt.add_argument("--profile-directory=" + profile_dir)

# 2 - Permission
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", { \
    "profile.default_content_setting_values.media_stream_mic": 2,
    "profile.default_content_setting_values.media_stream_camera": 2,
    "profile.default_content_setting_values.geolocation": 2,
    "profile.default_content_setting_values.notifications": 2
})
########################################################################
########################################################################

# Launch chrome
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(30)


# Move to objective website
def classroom(sub):
    sysmessage("Opening Google Classroom...")
    driver.get(url)
    sysmessage("Searching the classrooms for [ " + sub + " ]...")
    driver.find_element_by_partial_link_text(sub).click()
    sysmessage("Found a classroom named [ " + driver.find_element_by_partial_link_text(sub).text.replace("\n", " ") + " ].")

    meet_url = driver.find_element_by_partial_link_text("meet.google.com").text
    sysmessage()
    print("Target Google Meet URL: " + meet_url)
    return meet_url


# Join Google Meet session
def meetJoin(target_url):
    driver.execute_script("window.open('about:blank','second_tab');")
    driver.switch_to.window("second_tab")
    driver.get(target_url)
    # print(driver.find_element_by_xpath("/html/body").text)
    time.sleep(3)
    driver.find_element_by_xpath(
        '//*[@id="yDmH0d"]/div[3]/div/div[2]/div[3]/div/span/span').click()
    time.sleep(1)
    driver.find_element_by_xpath(
        '//*[@id="yDmH0d"]/c-wiz/div/div/div[9]/div[3]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]/span/span'
    ).click()
    end_date = datetime.datetime.now() + datetime.timedelta(minutes=length)
    sysmessage()
    print("Joined the class. End time will be " + end_date.strftime("%Y/%m/%d %H:%M:%S"))


# If you have to login to the Google Account
def login():
    driver.get(login_url)
    driver.find_element_by_xpath(
        '//*[@id="identifierId"]'
    ).send_keys(email + "\n")
    driver.find_element_by_xpath(
        '//*[@id="password"]/div[1]/div/div[1]/input'
    ).send_keys(passwd + "\n")


# Send a message with timestamp
def sysmessage(text_message=""):
    print("[" + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "] ", end="")
    if text_message != "":
        print(text_message)


# Execute
# login()
session_url = classroom(subject)
meetJoin(session_url)


# Timer
joined_time = time.time()
sec_time = time.time() - joined_time

while True:
    time.sleep(1)
    ela_time = time.time() - joined_time
    if ela_time > sec_time + 10:
        min = ela_time / 60
        people = driver.find_element_by_xpath(
            '//*[@id="ow3"]/div[1]/div/div[9]/div[3]/div[1]/div[3]/div/div[2]/div[1]/span/span/div/div/span[2]'
            ).text
        sysmessage()
        print('{:.0f}'.format(min) + "/" + str(length) + " min passed, " + str(round(length - min)) + " min to quit. " + str(people) + " people in the meet session.")
        sec_time = ela_time
        if people is not "1":
            pass
        else:
            sysmessage("Quitting process...")
            driver.quit()
            break
    if ela_time > length * 60:
        sysmessage()
        print(str(length) + " min timer reached")
        sysmessage("Quitting process...")
        driver.find_element_by_xpath(
            '//*[@id="ow3"]/div[1]/div/div[9]/div[3]/div[9]/div[2]/div[2]/div'
        ).click()
        time.sleep(3)
        driver.quit()
        break
