import sys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils

wd = ChromeUtils().init_driver(headless=True)
url = r"http:\\192.168.100.1"

wd.get(url)
time.sleep(5)

f = wd.find_element(By.ID, "txt_Username")
f.send_keys("technician")
time.sleep(2)

f = wd.find_element(By.ID, "txt_Password")
f.send_keys("fttht3chn1c1@n")
time.sleep(2)
f.send_keys(Keys.RETURN)

time.sleep(5)

# click Advanced
f = wd.find_element(By.ID, "name_addconfig")
f.click()
time.sleep(2)

# click Security
f = wd.find_element(By.ID, "name_securityconfig")
f.click()
time.sleep(2)

# click MAC Filtering
f = wd.find_element(By.ID, "macfilter")
f.click()
time.sleep(2)

wd.switch_to.frame("menuIframe")

# click Enable MAC filter button
f = wd.find_element(By.ID, "EnableMacFilter")
f.click()
time.sleep(2)

wd.switch_to.default_content()

# click WiFi MAC Filtering
f = wd.find_element(By.ID, "wlanmacfilter")
f.click()
time.sleep(2)

wd.switch_to.frame("menuIframe")

# click Enable MAC filter button
f = wd.find_element(By.ID, "EnableMacFilter")
f.click()
time.sleep(2)

# clean exit
print("Script ran successfully")
