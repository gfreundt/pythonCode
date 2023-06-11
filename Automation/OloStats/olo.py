import time, sys
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


def set_options():
    options = WebDriverOptions()
    options.add_argument("--window-size=1440,810")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--silent")
    options.add_argument("--disable-notifications")
    # options.add_argument("--incognito")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return options


def extract(url):
    driver = webdriver.Chrome(
        service=Service("C:\pythonCode\chromedriver.exe"), options=set_options()
    )
    driver.get(url)
    time.sleep(2)

    if "GABRIEL" not in driver.page_source:
        driver.find_element(By.ID, "mobile_number").send_keys("881012400")
        driver.find_element(By.ID, "passwd").send_keys("MFZx5kTm.yaXhk*")
        driver.find_element(
            By.XPATH, "/html/body/div/div[2]/div/div/div/div[2]/form/div[3]/button"
        ).click()
        time.sleep(5)

    data_left = driver.find_element(
        By.XPATH,
        "/html/body/div/div[2]/div/div[3]/div/div[2]/div[3]/div/div[2]/p/span[1]",
    ).text

    end_date = driver.find_element(
        By.XPATH,
        "/html/body/div/div[2]/div/div[3]/div/div[2]/div[3]/div/div[1]/p",
    ).text
    return data_left, end_date[end_date.find("expira") + 12 :]


def include_in_table(output_raw):
    with open("oloStatsHistoric.txt", mode="a") as output_file:
        output_file.write(f"{dt.now()},{output_raw[0]},{output_raw[1]}\n")


def main():
    output_raw = extract("https://miolo.olo.com.pe/")
    output = (
        f"Stats from: {dt.now()}.\nData Left: {output_raw[0]}.\nUntil: {output_raw[1]}."
    )

    if "EMAIL" in sys.argv:
        import ezgmail  # Import close to sending to avoid 'Broken Pipe' error

        ezgmail.send("gfreundt@gmail.com", "OLO Stats", output)
    else:
        include_in_table(output_raw)


main()
