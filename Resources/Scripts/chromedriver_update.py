import subprocess
import os, time
from gft_utils import ChromePreLoad


def check_chrome_version():
    result = subprocess.check_output(
        'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
    ).decode("utf-8")
    return result.split(" ")[-1].split(".")[0]


def check_chromedriver_version():
    result = subprocess.check_output(f"{PATH} -v").decode("utf-8")
    return result.split(" ")[1].split(".")[0]


def download_correct_chromedriver(target_version):
    webdriver = ChromePreLoad.init_driver(incognito=True, headless=True)
    webdriver.get("https://chromedriver.chromium.org/downloads")
    time.sleep(3)
    ps = webdriver.page_source

    while "ChromeDriver 2.41" not in ps:
        # wait until page loaded
        pass

    versions = [i.split(" ")[-1] for i in ps.split("\n")[1:4]]
    full_url = f"https://chromedriver.storage.googleapis.com/{[i for i in versions if i.split('.')[0] == str(target_version)][0]}/chromedriver_win32.zip"
    webdriver.get(full_url)

    # wait until download has finished to quit browser
    while not os.path.exists(TEMP):
        time.sleep(3)
    webdriver.quit()

    # delete current chromedriver.exe
    if os.path.exists(PATH):
        os.remove(PATH)

    # unzip downloaded file contents into Resources folder
    cmd = rf'Expand-Archive -Path {TEMP} -DestinationPath "D:\pythonCode\Resources"'
    subprocess.run(["powershell", "-Command", cmd])

    # delete unnecesary files after unzipping
    os.remove(r"D:\pythonCode\Resources\LICENSE.chromedriver")
    os.remove(TEMP)


TEMP = os.path.join(r"C:\Users", "gfreu", "Downloads", "chromedriver_win32.zip")
PATH = os.path.join(r"D:\pythonCode", "Resources", "chromedriver.exe")
driver = check_chromedriver_version()
browser = check_chrome_version()

print(f"Driver is {driver} and Browser is {browser}.")

if driver != browser:
    print("Updating chromedriver.exe...")
    download_correct_chromedriver(browser)
