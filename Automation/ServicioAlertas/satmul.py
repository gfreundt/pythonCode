import time
from pygame.locals import *
from statistics import mean
from datetime import datetime as dt
from pprint import pprint


from gft_utils import ChromeUtils


def main(SATMUL, placas):

    # don't run if no records to process
    if not placas:
        return []

    URL = "https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx"
    SATMUL.WEBD = ChromeUtils().init_driver(
        headless=False, verbose=False, maximized=True, incognito=False
    )
    SATMUL.WEBD.get(URL)
    _target = (
        "https://www.sat.gob.pe/VirtualSAT/modulos/papeletas.aspx?tri=T&mysession="
        + SATMUL.WEBD.current_url.split("=")[-1]
    )
    time.sleep(2)
    SATMUL.WEBD.get(_target)

    all_responses = []
    for placa in placas:
        try:
            while True:
                # attempt to scrape image
                response = SATMUL.browser(placa=placa[4])
                # scrape succesful
                if response != -1:
                    all_responses.append(
                        (
                            placa[0],
                            placa[1],
                            response,
                        )
                    )
                    break
                # if scrape unsuccesful (wrong captcha or image did not load) recycle
        except KeyboardInterrupt:
            quit()
        except:
            # if error, go to next placa to avoid getting stuck in loop
            print("error")
            time.sleep(3)

    return all_responses
