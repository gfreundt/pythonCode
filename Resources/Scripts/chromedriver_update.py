import subprocess
import os
import requests
import json


def target_drive():
    for drive in ("C:", "D:"):
        if os.path.exists(os.path.join(drive, "\pythonCode")):
            return drive


def check_chrome_version():
    result = subprocess.check_output(
        'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
    ).decode("utf-8")
    return result.split(" ")[-1].split(".")[0]


def check_chromedriver_version():
    try:
        version = subprocess.check_output(f"{CURRENT_PATH} -v").decode("utf-8")
        return version.split(".")[0][-3:]
    except:
        return 0


def download_chromedriver(target_version):
    # extract latest data from Google API
    api_data = json.loads(requests.get(GOOGLE_CHROMEDRIVER_API).text)

    # find latest build for current Chrome version and download zip file
    endpoints = api_data["milestones"][str(target_version)]["downloads"]["chromedriver"]
    url = [i["url"] for i in endpoints if i["platform"] == "win64"][0]
    with open(TARGET_PATH, mode="wb") as download_file:
        download_file.write(requests.get(url).content)

    # delete current chromedriver.exe
    if os.path.exists(CURRENT_PATH):
        os.remove(CURRENT_PATH)

    # unzip downloaded file contents into Resources folder
    cmd = rf'Expand-Archive -Force -Path {TARGET_PATH} -DestinationPath "{BASE_PATH}"'
    subprocess.run(["powershell", "-Command", cmd])

    # move chromedriver.exe to correct folder
    os.rename(os.path.join(UNZIPPED_PATH, "chromedriver.exe"), CURRENT_PATH)

    # delete unnecesary files after unzipping
    os.remove(os.path.join(UNZIPPED_PATH, "LICENSE.chromedriver"))
    os.rmdir(UNZIPPED_PATH)
    os.remove(TARGET_PATH)


def main():
    # get current browser and chromedriver versions
    driver = check_chromedriver_version()
    browser = check_chrome_version()
    print(f"Driver: version {driver}\nBrowser: version {browser}.")

    # if versions don't match, get the correct chromedriver from repository
    if driver != browser:
        print("Updating chromedriver.exe...")
        download_chromedriver(browser)
    else:
        print("No need to update driver")

    print(">> Process Finished Succesfully <<")


GOOGLE_CHROMEDRIVER_API = "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json"
BASE_PATH = os.path.join(rf"{target_drive()}\pythonCode", "Resources")
CURRENT_PATH = os.path.join(BASE_PATH, "chromedriver.exe")
TARGET_PATH = os.path.join(BASE_PATH, "chromedriver.zip")
UNZIPPED_PATH = os.path.join(BASE_PATH, "chromedriver-win64")


main()
