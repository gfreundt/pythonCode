import os
from copy import deepcopy as copy
from datetime import datetime as dt
from PIL import Image, ImageDraw, ImageFont
from gft_utils import PDFUtils


def friendly_date(date):
    return dt.strftime(dt.strptime(date, "%Y-%m-%d"), "%d/%m/%Y")


class SoatImage:

    def __init__(self, LOG, cursor):
        self.LOG = LOG
        self.cursor = cursor
        self.pdf = PDFUtils()

    def generate(self, id):
        _resources = os.path.join("D:\pythonCode", "Resources", "Fonts")
        _path = os.path.join(os.curdir, "images")
        base_img = Image.open(os.path.join(_path, "SOAT_base.png"))
        cias = [i.split(".")[0] for i in os.listdir(_path)]
        editable_img = ImageDraw.Draw(base_img)
        myFont1 = ImageFont.truetype(os.path.join(_resources, "seguisym.ttf"), 30)
        myFont2 = ImageFont.truetype(os.path.join(_resources, "seguisym.ttf"), 45)

        # get SOAT data from database
        cmd = f"SELECT Aseguradora, Certificado, FechaInicio, FechaHasta, PlacaValidate, Clase, Uso FROM soats WHERE IdPlaca_FK={id}"
        self.cursor.execute(cmd)
        info = self.cursor.fetchone()

        # turn date into friendly format
        info[2], info[3] = friendly_date(info[2]), friendly_date(info[3])

        # if logo in database add it to image, else add word
        if info[0] in cias:
            logo = Image.open(os.path.join(_path, f"{info[0]}.png"))
            logo_width, logo_height = logo.size
            logo_pos = (10 + (340 - logo_width) // 2, 250 + (120 - logo_height) // 2)
            base_img.paste(logo, logo_pos)
            # get INSURANCE COMPANY phone number from database
            cmd = f"SELECT Telefono1 FROM '@aseguradoras' WHERE Aseguradora='{info[0]}'"
            self.cursor.execute(cmd)
            _phone = self.cursor.fetchone()[0]
            editable_img.text((400, 275), _phone, font=myFont2, fill=(59, 22, 128))
        else:
            editable_img.text(
                (40, 275), info[0].upper(), font=myFont2, fill=(59, 22, 128)
            )

        # positions for each text in image
        coordinates = [
            (40, 516, 1),
            (40, 588, 2),
            (40, 665, 3),
            (337, 588, 2),
            (337, 665, 3),
            (40, 819, 4),
            (40, 897, 5),
            (40, 970, 6),
            (406, 971, 3),
        ]

        for c in coordinates:
            editable_img.text(
                (c[0], c[1]), info[c[2]].upper(), font=myFont1, fill=(59, 22, 128)
            )

        file_name = f"SOAT_{info[4].upper()}.pdf"

        to_path = os.path.join(
            r"D:\pythonCode",
            "Automation",
            "ServicioAlertas",
            "data",
            "images",
            file_name,
        )

        temp_path = os.path.join(
            r"D:\pythonCode",
            "Automation",
            "ServicioAlertas",
            "images",
            "temp_img.png",
        )

        base_img.save(temp_path)

        # delete image with same name (previous version) from destination folder if it exists
        if os.path.exists(to_path):
            os.remove(to_path)
        img = Image.open(temp_path)
        self.pdf.image_to_pdf(img, to_path)
        base_img.show()
        return file_name
