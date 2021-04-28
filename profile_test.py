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
opt.add_argument("start-maximized")
opt.add_argument("--user-data-dir=C:\\Users\\mars2\\AppData\\Local\\Google\\Chrome\\User Data")

# Chrome permission Configuration
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", { \
    "profile.default_content_setting_values.media_stream_mic": 2, 
    "profile.default_content_setting_values.media_stream_camera": 2,
    "profile.default_content_setting_values.geolocation": 2, 
    "profile.default_content_setting_values.notifications": 2 
  })
#Launch chrome
driver = webdriver.Chrome(chrome_options=opt, executable_path=driver_location)
driver.implicitly_wait(10)

