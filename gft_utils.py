import os
import platform
import time
import random
from datetime import datetime as dt, timedelta as td
import math
import ctypes
from PIL import Image
import pypdfium2.raw as pdfium
import img2pdf
import pywhatkit
import pyautogui
import dotenv
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import speech_recognition


"""make sure that httplib2==0.15.0 or there will be conflicts with pydrive"""


class ChromeUtils:
    def init_driver(self, **kwargs):
        """Returns a ChromeDriver object with commonly used parameters allowing for some optional settings"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as WebDriverOptions
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.keys import Keys

        # set defaults that can be overridden by passed parameters
        parameters = {
            "incognito": False,
            "headless": False,
            "window_size": False,
            "load_profile": False,
            "verbose": True,
            "no_driver_update": False,
            "maximized": False,
        } | kwargs

        options = WebDriverOptions()

        # configurable options
        if parameters["incognito"]:
            options.add_argument("--incognito")
        if parameters["headless"]:
            options.add_argument("--headless=new")
        if parameters["load_profile"]:
            options.add_argument(
                r"--user-data-dir=C:\Users\gfreu\AppData\Local\Google\Chrome\User Data\Default\Profile 1"
            )
        if parameters["window_size"]:
            options.add_argument(
                f"--window-size={parameters['window_size'][0]},{parameters['window_size'][1]}"
            )
        # if parameters["window-position"]:
        #     options.add_argument(
        #         f"--window-position={parameters['window-position'][0]},{parameters['window-position'][1]}"
        #     )

        if parameters["maximized"]:
            options.add_argument("--start-maximized")

        # fixed options
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.218 Safari/537.36"
        )
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--silent")
        options.add_argument("--disable-notifications")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # disabled options
        """
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--content-shell-hide-toolbar")
        options.add_argument("--top-controls-hide-threshold")

        """

        _path = (
            os.path.join(
                f"{os.getcwd()[:2]}\pythonCode", "Resources", "chromedriver.exe"
            )
            if "Windows" in platform.uname().system
            else "/usr/bin/chromedriver"
        )

        # update driver to match browser version if necessary
        if not parameters["no_driver_update"]:
            self.driver_update(verbose=False)

        if parameters["verbose"]:
            print("gft_utils --> Chromedriver initiated")

        _w = webdriver.Chrome(service=Service(_path), options=options)
        return _w

    def driver_update(self, **kwargs):
        """Compares current Chrome browser and Chrome driver versions and updates driver if necessary"""
        import subprocess
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
            endpoints = api_data["milestones"][str(target_version)]["downloads"][
                "chromedriver"
            ]
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
            # os.rmdir(UNZIPPED_PATH)
            # os.remove(TARGET_PATH)

        # set defaults that can be overridden by passed parameters
        parameters = {
            "verbose": True,
        } | kwargs

        # define URIs
        GOOGLE_CHROMEDRIVER_API = "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json"
        if "Windows" in platform.uname().system:
            BASE_PATH = os.path.join(rf"{target_drive()}\pythonCode", "Resources")
        else:
            BASE_PATH = r"/home/gfreundt/pythonCode/Resources"
        # BASE_PATH = os.path.join(rf"{target_drive()}\pythonCode", "Resources")
        CURRENT_PATH = os.path.join(BASE_PATH, "chromedriver.exe")
        TARGET_PATH = os.path.join(BASE_PATH, "chromedriver.zip")
        UNZIPPED_PATH = os.path.join(BASE_PATH, "chromedriver-win64")

        # get current browser and chromedriver versions
        driver = check_chromedriver_version()
        browser = check_chrome_version()
        if parameters["verbose"]:
            print(f"Driver: version {driver}\nBrowser: version {browser}.")

        # if versions don't match, get the correct chromedriver from repository
        if driver != browser:
            if parameters["verbose"]:
                print("Updating chromedriver.exe...")
            download_chromedriver(browser)
        else:
            if parameters["verbose"]:
                print("No need to update driver")

        # clean exit
        if parameters["verbose"]:
            print(">> Process Finished Succesfully <<")

    def slow_key_sender(self=None, **kwargs):
        """Inserts random small pauses between keystrokes to simulate human typing"""

        # TODO: default for return_key
        for key in kwargs["text"]:
            time.sleep(random.randint(1, 10) / 10)
            kwargs["element"].send_keys(key)
        if kwargs["return_key"]:
            time.sleep(0.4)
            kwargs["element"].send_keys(Keys.RETURN)

    def button_clicker(self, webdriver, type, element, timeout=20, fatal_error=False):
        """Waits for clickable element to load before clicking on it"""
        try:
            WebDriverWait(webdriver, timeout).until(
                EC.element_to_be_clickable((type, element))
            ).click()
        except TimeoutException:
            if fatal_error:
                print("Webpage failed to load.")
                quit()


class pygameUtils:
    def __init__(self, screen_size=None) -> None:
        import pygame
        import json

        pygame.init()

        # load environment constants
        self.DISPLAY_WIDTH = pygame.display.Info().current_w
        self.DISPLAY_HEIGHT = pygame.display.Info().current_h
        if not screen_size:
            self.MAIN_SURFACE = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.MAIN_SURFACE = pygame.display.set_mode(screen_size, pygame.NOFRAME)
        # split main surface in two halves
        self.LEFT_SURFACE = pygame.Surface(
            (self.MAIN_SURFACE.get_width() // 2, self.MAIN_SURFACE.get_height())
        )
        self.RIGHT_SURFACE = self.LEFT_SURFACE.copy()

        # load custom constants
        self.RESOURCES_PATH = os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources")
        with open(
            os.path.join(self.RESOURCES_PATH, "ConfigData", "pygame_data.json"),
            mode="r",
        ) as file:
            data = json.load(file)
        self.COLORS = data["colors"]
        self.PALETTES = data["palettes"]
        _fonts = data["fonts"]
        self.FONTS = {
            i: pygame.font.Font(
                os.path.join(self.RESOURCES_PATH, "Fonts", _fonts[i]["ttf"]),
                _fonts[i]["size"],
            )
            for i in _fonts
        }


class GoogleUtils:
    def __init__(self) -> None:

        from pydrive.drive import GoogleDrive
        from pydrive.auth import GoogleAuth

        self.DRIVE_CREDENTIALS_PATH = os.path.join(
            "d:\pythonCode", "Resources", "ConfigData"
        )
        _gauth = GoogleAuth()
        _gauth.LocalWebserverAuth()
        self.gdrive = GoogleDrive(_gauth)
        self.from_address_tokens = {
            "gfreundt@gmail.com": "gfreundt_token.json",
            "gabfre@gmail.com": "gabfre_token.json",
            "servicioalertaperu@gmail.com": "servicioalertaperu_token.json",
        }

    def get_drive_files(self, gdrive_path_id):
        file_list = self.gdrive.ListFile(
            {"q": f"'{gdrive_path_id}' in parents and trashed=False"}
        ).GetList()
        return file_list

    def download_from_drive(self, gdrive_object, local_path):
        _mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        gdrive_object.GetContentFile(local_path, mimetype=_mimetype)

    def upload_to_drive(self, local_path, gdrive_filename, gdrive_path_id):
        # select file to upload
        file = self.gdrive.CreateFile(
            {"title": gdrive_filename, "parents": [{"id": gdrive_path_id}]}
        )
        file.SetContentFile(local_path)
        # execute
        file.Upload()

    def send_gmail(self, fr, messages):
        # must be imported close to sending email to avoid "broken pipe" error
        import ezgmail

        ezgmail.init(
            tokenFile=os.path.join(
                "D:\pythonCode", "Resources", "ConfigData", self.from_address_tokens[fr]
            ),
            credentialsFile=os.path.join(
                "D:\pythonCode", "Resources", "ConfigData", "gmail_credentials.json"
            ),
        )

        result = []
        for message in messages:
            try:
                ezgmail.send(
                    recipient=message.get("to"),
                    cc=message.get("cc"),
                    bcc=message.get("bcc"),
                    subject=message.get("subject"),
                    body=message.get("body"),
                    attachments=message.get("attachments"),
                    mimeSubtype="html",
                )
                result.append(True)
            except KeyboardInterrupt:
                result.append(False)

        return result

    def read_gmail(self, fr, only_unread=True, max_results=20, mark_read=False):
        # must be imported close to reading email to avoid "broken pipe" error
        import ezgmail

        ezgmail.init(
            tokenFile=os.path.join(
                "D:\pythonCode", "Resources", "ConfigData", self.from_address_tokens[fr]
            ),
            credentialsFile=os.path.join(
                "D:\pythonCode", "Resources", "ConfigData", "gmail_credentials.json"
            ),
        )

        inbox = (
            ezgmail.unread() if only_unread else ezgmail.recent(maxResults=max_results)
        )
        if mark_read:
            for i in inbox:
                i.markAsRead()

        return inbox


class PDFUtils:

    def pdf_to_png(self, from_path, to_path=None, scale=1):
        """if parameter to_path is given, result of funtion is to save image
        if parameter to_path is not given, return object as PIL image"""

        # Load document
        pdf = pdfium.FPDF_LoadDocument((from_path + "\x00").encode("utf-8"), None)

        # Check page count to make sure it was loaded correctly
        page_count = pdfium.FPDF_GetPageCount(pdf)
        assert page_count >= 1

        # Load the first page and get its dimensions
        page = pdfium.FPDF_LoadPage(pdf, 0)
        width = int(math.ceil(pdfium.FPDF_GetPageWidthF(page)) * scale)
        height = int(math.ceil(pdfium.FPDF_GetPageHeightF(page)) * scale)

        # Create a bitmap
        # (Note, pdfium is faster at rendering transparency if we use BGRA rather than BGRx)
        use_alpha = pdfium.FPDFPage_HasTransparency(page)
        bitmap = pdfium.FPDFBitmap_Create(width, height, int(use_alpha))
        # Fill the whole bitmap with a white background
        # The color is given as a 32-bit integer in ARGB format (8 bits per channel)
        pdfium.FPDFBitmap_FillRect(bitmap, 0, 0, width, height, 0xFFFFFFFF)

        # Store common rendering arguments
        render_args = (
            bitmap,  # the bitmap
            page,  # the page
            # positions and sizes are to be given in pixels and may exceed the bitmap
            0,  # left start position
            0,  # top start position
            width,  # horizontal size
            height,  # vertical size
            0,  # rotation (as constant, not in degrees!)
            pdfium.FPDF_LCD_TEXT
            | pdfium.FPDF_ANNOT,  # rendering flags, combined with binary or
        )

        # Render the page
        pdfium.FPDF_RenderPageBitmap(*render_args)

        # Get a pointer to the first item of the buffer
        buffer_ptr = pdfium.FPDFBitmap_GetBuffer(bitmap)
        # Re-interpret the pointer to encompass the whole buffer
        buffer_ptr = ctypes.cast(
            buffer_ptr, ctypes.POINTER(ctypes.c_ubyte * (width * height * 4))
        )
        # Create a PIL image from the buffer contents
        img = Image.frombuffer(
            "RGBA", (width, height), buffer_ptr.contents, "raw", "BGRA", 0, 1
        )
        # Close all
        pdfium.FPDFBitmap_Destroy(bitmap)
        pdfium.FPDF_ClosePage(page)
        pdfium.FPDF_CloseDocument(pdf)
        # Save it as file or return image object
        if to_path:
            img.save(to_path)
            return None
        else:
            return img
        
    def image_to_pdf(self, image_bytes, to_path):
 
        with open(to_path, "wb") as file:
            file.write(img2pdf.convert(image_bytes.filename))
    
class WhatsAppUtils:

    def __init__(self) -> None:
        pass

    def send_wapp(self, celnum, alert_txt):
        # ensure correct Chorme Windows is selected so correct WA is used
        # input("***** Make sure active Chrome Window is selected AND PRESS ENTER *****")

        # code assumes that correct Chrome profile is active

        # define time to use as parameter for library
        now = dt.now()
        sec = int(now.strftime("%S"))
        now += td(minutes=2 if sec > 40 else 1)
        hour, min = int(now.strftime("%H")), int(now.strftime("%M"))

        # set up text
        pywhatkit.sendwhatmsg(f"+51{celnum}", alert_txt, hour, min)

        # set focus on window and manually press ENTER
        time.sleep(1)
        _win = pyautogui.getWindowsWithTitle("Chrome")[0]
        _win.minimize()
        time.sleep(0.5)
        _win.maximize()
        pyautogui.press("ENTER")

class EmailUtils:

    def __init__(self, account):
        dotenv.load_dotenv(os.path.join("D:\pythonCode","Resources","ConfigData","environ_variables.env"))
        self.sender_email = account
        try:
            self.sender_password = os.environ[account.upper()]
        except KeyError:
            raise KeyError("Email account has no registered password.")

    def send_from_outlook(self, emails):
        ''' structure is dictionary with keys: MANDATORY: to (string), subject (string)
            OPTIONAL: bcc (string), plain_body (string), html_body (string), attachments (list of strings)'''
        success = []
        for to_send_email in emails:
            # create a multipart message and set headers
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = to_send_email["to"]
            message["Subject"] = to_send_email["subject"]
            if to_send_email.get("cc"):
                message["Cc"] = to_send_email["cc"]
            if to_send_email.get("bcc"):
                message["Bcc"] = to_send_email["bcc"]

            # add plain body and/or html body to email
            if to_send_email.get("plain_body"):
                message.attach(MIMEText(to_send_email["plain_body"], "plain"))
            if to_send_email.get("html_body"):
                message.attach(MIMEText(to_send_email["html_body"], "html"))

            # cycle through all of the attachments and add them to message
            if to_send_email.get("attachments"):
                for attach_filename in to_send_email["attachments"]:
                    # open attachment file in binary mode and encode
                    with open(attach_filename, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                    # add header as key/value pair to attachment part
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attach_filename}",
                    )
                    # add attachment to message
                    message.attach(part)

            # send email
            try:
                with smtplib.SMTP("smtp-mail.outlook.com", port=587) as smtp:
                    smtp.starttls()
                    smtp.login(self.sender_email, self.sender_password)
                    smtp.sendmail(self.sender_email, to_send_email["to"], message.as_string())
                    success.append(True)
            except:
                success.append(False)

        return success

class SpeechUtils:

    def __init__(self):
        self.speech_driver_errors = 0

    def clean_military_alphabet(self, text):
        with open(os.path.join("D:\pythonCode", "Resources", "StaticData", "military_alphabet.txt")) as file:
            ma_index = [i.strip() for i in file.readlines()]
            for word in ma_index:
                text = text.replace(word, word[0])
        return text

    def get_speech(self, use_military_alphabet=True, max_driver_errors=5):
        while True:
            try:
                with speech_recognition.Microphone() as mic:
                    self.speech.adjust_for_ambient_noise(mic, duration=0.2)
                    _audio = self.speech.listen(mic)
                    text = self.speech.recognize_google(_audio)
                    
                    
                # clean military alphabet letters
                if use_military_alphabet:
                    text = self.clean_military_alphabet(text.lower())
                
                return text

            except:
                if self.speech_driver_errors < max_driver_errors:
                    self.speech = speech_recognition.Recognizer()
                    self.speech_driver_errors += 1
                else:
                    return None
