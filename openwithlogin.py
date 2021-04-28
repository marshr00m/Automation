from selenium import webdriver
from selenium.webdriver.common.keys import Keys as keys
from selenium.webdriver.chrome.options import Options
import time, config

# Import arguments from config.py file
email = config.EMAIL_ADDRESS
passwd = config.PASSWORD
url = config.URL

# Define "chromedriver.exe" location
driver_location = ".\chromedriver.exe"

#Google login page URL
login_url = "https://accounts.google.com/signin/v2/identifier?hl=ja&passive=true&continue=https%3A%2F%2Fwww.google.com%2F%3Fhl%3Dja&ec=GAZAmgQ&flowName=GlifWebSignIn&flowEntry=ServiceLogin"

opt = Options()
opt.add_argument("--disable-infobars")
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")

# Chrome permission Configuration
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", { \
    "profile.default_content_setting_values.media_stream_mic": 2, 
    "profile.default_content_setting_values.media_stream_camera": 2,
    "profile.default_content_setting_values.geolocation": 2, 
    "profile.default_content_setting_values.notifications": 2 
  })
#Launch chrome
driver = webdriver.Chrome(options=opt, executable_path=driver_location)

# Login operation
driver.get(login_url)
time.sleep(2)
driver.find_element_by_xpath(
    '//*[@id="identifierId"]'
    ).send_keys(email+"\n")
time.sleep(3)
driver.find_element_by_xpath(
    '//*[@id="password"]/div[1]/div/div[1]/input'
    ).send_keys(passwd+"n")
time.sleep(3)

#Move to objective website
driver.get(url)
time.sleep(2)
driver.find_element_by_xpath(
    '//*[@id="yDmH0d"]/div[3]/div/div[2]/div[3]/div/span/span'
    ).click()
time.sleep(2)
driver.find_element_by_xpath(
    '//*[@id="yDmH0d"]/c-wiz/div/div/div[9]/div[3]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[1]/span/span'
    ).click()
time.sleep(60)
driver.close()
