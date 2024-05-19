from gft_utils import ChromeUtils
import scrapers
import time

scraper = scrapers.SoatImage()
# scraper = scrapers.CallaoMulta("")

url = "kaka:"

scraper.WEBD = ChromeUtils().init_driver(headless=False, verbose=False, maximized=True)
scraper.WEBD.get(url)
time.sleep(3)


placas = [
    "AMQ073",
    "CBW475",
    "4536FC",
    "F4J162",
    "AJP209",
    "D5Y413",
    "CJM179",
    "APA503",
    "D7Z065",
    "BAW484",
    "AKE119",
    "A1L239",
    "BAV066",
    "CHO571",
    "AHJ311",
    "ATR393",
    "A7X390",
    "LIA118",
    "BKI054",
    "CBU074",
    "AVN261",
    "BLB551",
    "CDH680",
    "CBA688",
    "BSL336",
    "C1P415",
    "CDN467",
    "95817Y",
    "94491F",
]

for placa in placas[-2:]:

    x = scraper.browser(placa=placa)
    time.sleep(3)
