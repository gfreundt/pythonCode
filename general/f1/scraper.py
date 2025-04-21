import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import time
from gft_utils import ChromeUtils
import time
from pprint import pprint
import requests
from bs4 import BeautifulSoup
import json


def get_list_of_circuits():
    webdriver = ChromeUtils().init_driver(headless=False, verbose=False, maximized=True)
    webdriver.get("https://www.f1-fansite.com/f1-circuits/")
    error = False
    while not error:
        error = False
        all_urls = []
        for row in range(1, 27):
            for col in range(1, 4):

                try:
                    f = webdriver.find_element(
                        By.XPATH,
                        f"/html/body/div[1]/div/div[4]/div/div[1]/div[2]/table/tbody/tr[{row}]/td[{col}]/a",
                    )

                    all_urls.append(f.get_attribute("href"))

                except StaleElementReferenceException:
                    error = True
                    print("error!")

                except:
                    print("other error")

    return all_urls


def scrape_circuit(url):

    html_page = requests.get(url)
    soup = BeautifulSoup(html_page.content, "html.parser")

    x = soup.find_all("img")

    layout_urls = []
    for u in x:
        start = str(u).find("data-src")
        end = str(u).find(".png", start + 10)
        if end == -1:
            end = str(u).find(".jpg", start + 10)
        if end > -1:
            img_url = str(u)[start + 10 : end + 4]
            if "layout" in img_url:
                layout_urls.append(img_url)

    return layout_urls


def main():

    for url in get_list_of_circuits():
        # x = "https://www.f1-fansite.com/f1-circuits/circuit-of-the-americas/"

        print(scrape_circuit(url))


def fix(text):
    t = text.lower()
    t = t.replace("-", "")
    t = t.replace(" ", "-")
    return t


def main2():
    webdriver = ChromeUtils().init_driver(
        headless=False, verbose=False, maximized=False
    )

    output = {}

    for year in range(2018, 2025):

        webdriver.get(f"https://www.formula1.com/en/racing/{year}")

        races = []
        a = 1
        while True:
            f = webdriver.find_elements(
                By.XPATH,
                f"/html/body/main/div/div[1]/div[3]/div/a[{a}]/fieldset/div/div[2]/div[1]/p",
            )
            g = webdriver.find_elements(
                By.XPATH,
                f"/html/body/main/div/div[1]/div[3]/div/a[{a}]/fieldset/legend/p",
            )
            if f and g:
                a += 1
                if "ROUND" in g[0].text:
                    races.append(fix(f[0].text))

            else:
                break

        output.update({year: races})

    with open("races_list.json", "w") as outfile:
        outfile.write(json.dumps(output))

    for year in output:
        for v in output[year]:
            try:
                webdriver.get(f"https://www.formula1.com/en/racing/{year}/{v}/circuit")
                f = webdriver.find_element(
                    By.XPATH,
                    f"/html/body/main/div[2]/div/div[2]/div/div[2]/div[1]/img",
                )
                with open(
                    os.path.join("CircuitLayouts", f"layout-{year}-{v}.png"), "wb"
                ) as out_file:
                    out_file.write(f.screenshot_as_png)
            except:
                pass


main2()
