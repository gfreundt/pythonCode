import scrapers, sunarp
from datetime import datetime as dt


class Maintenance:

    def __init__(self, LOG, members, MONITOR) -> None:
        self.LOG = LOG
        self.MONITOR = MONITOR
        self.cursor = members.cursor
        self.conn = members.conn
        self.sql = members.sql

    def housekeeping(self):
        # put duplicate placas into review table
        self.cursor.execute(
            "SELECT *, COUNT(*) c FROM placas GROUP BY Placa HAVING c > 1"
        )
        for dup in self.cursor.fetchall():
            self.cursor.execute(
                f"INSERT OR IGNORE INTO '$review' (IdMember_FK, IdPlaca_FK, Reason) VALUES ({dup[0]}, {dup[1]}, 'DUPLICATE PLACA')"
            )

        self.conn.commit()

        # TODO: erase temp files,
        # TODO: logfile maintenance

    def soat_images(self):

        cmd = "SELECT IdPlaca_FK, PlacaValidate FROM soats WHERE imgFilename = '' AND (Vigencia = 'Activo' or Vigencia = 'Futuro')"
        self.cursor.execute(cmd)
        to_update = self.cursor.fetchall()

        if not to_update:
            return

        scraper = scrapers.SoatImage()

        for record in to_update:
            try:
                img_name = scraper.browser(placa=record[1])
            except KeyboardInterrupt:
                img_name = ""

            cmd = f"UPDATE soats SET ImgFilename = '{img_name}' WHERE IdPlaca_FK = {record[0]}"
            self.cursor.execute(cmd)
            self.conn.commit()

    def sunarp_images(self):

        cmd = "SELECT IdPlaca, Placa FROM placas WHERE IdPlaca NOT IN (SELECT IdPlaca_FK FROM sunarps)"
        self.cursor.execute(cmd)
        to_update = self.cursor.fetchall()

        if not to_update:
            return

        scraper = scrapers.Sunarp()

        for record in to_update:
            try:
                while True:
                    response, img_object = scraper.browser(placa=record[1])
                    # no image found, retry
                    if response == -1:
                        continue
                    # correct captcha, no data for placa - enter update attempt to database, go to next placa
                    elif response == 1:
                        self.cursor.execute(
                            f"INSERT INTO '$review' (IdPlaca_FK, Reason) VALUES ({record[0]}, 'SUNARP')"
                        )
                        self.conn.commit()
                        break
                    elif img_object:
                        _fecha = dt.now().strftime("%Y-%m-%d")
                        _filename = f"SUNARP_{record[1]}.png"
                        sunarp.process_image(img_object, _filename)
                        cmd = f"INSERT INTO sunarps (IdPlaca_FK, ImgFilename, LastUpdate) VALUES ({record[0]}, '{_filename}', '{_fecha}')"
                        self.cursor.execute(cmd)
                        self.conn.commit()
                        break

            except:
                self.LOG.warning(
                    f"< SUNARP > Error processing Placa {record[1]}. Record skipped."
                )
