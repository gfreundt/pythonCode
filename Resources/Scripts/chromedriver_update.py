import subprocess
import os, time
from gft_utils import ChromePreLoad


def check_chrome_version():
    result = subprocess.check_output(
        'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
    ).decode("utf-8")
    return result.split(" ")[-1].split(".")[0]


def check_chromedriver_version(path):
    result = subprocess.check_output(f"{path} -v").decode("utf-8")
    return result.split(" ")[1].split(".")[0]


def download_correct_chromedriver(target_version, temp_path, final_path):
    webdriver = ChromePreLoad.init_driver(incognito=True, headless=True)
    webdriver.get("https://chromedriver.chromium.org/downloads")

    # wait until page loaded
    ps = ""
    while "ChromeDriver 2.41" not in ps:
        time.sleep(3)
        ps = webdriver.page_source

    versions = [i.split(" ")[-1] for i in ps.split("\n")[1:4]]
    full_url = f"https://chromedriver.storage.googleapis.com/{[i for i in versions if i.split('.')[0] == str(target_version)][0]}/chromedriver_win32.zip"
    webdriver.get(full_url)

    # wait until download has finished to quit browser
    while not os.path.exists(temp_path):
        time.sleep(3)
    webdriver.quit()

    # delete current chromedriver.exe
    if os.path.exists(final_path):
        os.remove(final_path)

    # unzip downloaded file contents into Resources folder
    cmd = (
        rf'Expand-Archive -Path {temp_path} -DestinationPath "D:\pythonCode\Resources"'
    )
    subprocess.run(["powershell", "-Command", cmd])

    # delete unnecesary files after unzipping
    os.remove(temp_path)
    os.remove(r"D:\pythonCode\Resources\LICENSE.chromedriver")


def main():
    TEMP = os.path.join(r"C:\Users", "gfreu", "Downloads", "chromedriver_win32.zip")
    FINAL = os.path.join(r"D:\pythonCode", "Resources", "chromedriver.exe")

    # get current browser and chromedriver versions
    driver = check_chromedriver_version(path=FINAL)
    browser = check_chrome_version()
    print(f"Driver is {driver} and Browser is {browser}.")

    # if versions don't match, get the correct chromedriver from repository
    if driver != browser:
        print("Updating chromedriver.exe...")
        download_correct_chromedriver(
            target_version=browser, temp_path=TEMP, final_path=FINAL
        )

    print("Process Finished Succesfully.")


main()
