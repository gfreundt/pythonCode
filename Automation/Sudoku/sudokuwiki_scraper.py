import sys
import time
from tqdm import tqdm
from datetime import datetime as dt, timedelta as td
from selenium.webdriver.common.by import By


# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


def process():
    webd = ChromeUtils().init_driver(headless=True, verbose=False, maximized=True)
    for i in tqdm(range(31)):
        date = dt.now() - td(days=(30 - i))
        url = f"https://www.sudokuwiki.org/Print/Print_Daily_Sudoku.aspx?day={date.day}-{date.month}-{date.year}"
        webd.get(url)

        level = (
            webd.find_element(
                By.XPATH,
                f"/html/body/table/tbody/tr[1]/td",
            )
            .text.strip()
            .split("\n")[-1]
        )

        sudoku = ""
        for row in range(1, 10):
            for col in range(1, 10):
                digit = webd.find_element(
                    By.XPATH,
                    f"/html/body/table/tbody/tr[4]/td[2]/table/tbody/tr[{str(row)}]/td[{str(col)}]",
                ).text.strip()
                if not digit:
                    digit = "0"
                sudoku += digit
        with open("sudokuwiki.csv", "a+") as file:
            file.write(f"{sudoku},{level},{str(date)[:10]}\n")


url = f"https://www.sudokuwiki.org/Print/Print_Daily_Sudoku.aspx?day={dt.now().day}-{dt.now().month}-{dt.now().year}"

process()
