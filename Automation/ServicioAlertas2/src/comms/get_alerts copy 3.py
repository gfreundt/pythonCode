import os
from gft_utils import EmailUtils
from html.parser import HTMLParser

# send emails if switch on
def send(monitor, messages):

    # loop on all html files in outbound folder
    parser = HTMLParser()
    
    messages = [i for i in os.listdir(os.path.join("..", "outbound")) if "message" in i]

    with open(messages[0], "r") as file:
        data = file.read()

    x = parser.feed(data)

    print(x)

    quit()        
    




    # activate mail API and send all
    email = EmailUtils(account="servicioalertasperu@outlook.com")



    results = email.send_from_outlook(emails=messages)

    # TODO: create alerts to let members know that email has been sent

    # update mensaje and mensajeContenido tables depending on success reply from email attempt
    table, fields = "mensajes", ("IdMember_FK", "Fecha", "HashCode")
    table2, fields2 = "mensajeContenidos", ("IdMensaje_FK", "IdTipoMensaje_FK")
    for result, message in zip(results, messages):
        if result:
            self.LOG.info(
                f"Email sent to {message['to']} (IdMember = {message['idMember']}). Type: {message['tipoMensajes']}"
            )
            # populate mensaje tables
            cmd = self.sql(table, fields)
            values = (
                message["idMember"],
                message["timestamp"],
                message["hashcode"],
            )
            self.cursor.execute(cmd, values)
            # get just crafted record
            self.cursor.execute(
                f"SELECT * FROM {table} WHERE HashCode = '{message['hashcode']}'"
            )
            _x = self.cursor.fetchone()
            for msgtype in message["tipoMensajes"]:
                cmd = self.sql(table2, fields2)
                values = _x[0], msgtype
                self.cursor.execute(cmd, values)
        else:
            self.LOG.warning(f"ERROR sending email to {message['to']}.")
    self.conn.commit()

else:
    self.LOG.warning("Emails not sent. SWITCH OFF.")
