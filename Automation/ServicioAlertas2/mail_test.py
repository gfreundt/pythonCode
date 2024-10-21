import os
import win32com.client

outlook = win32com.client.Dispatch("Outlook.Application")
k = 0x0
message = outlook.CreateItem(k)

message.Recipients.Add("gfreundt@gmail.com")
message.Subject = "Message from Python Now"
message.Body = "This is the Message Body Text"

attach = ["D:\\erase.json", os.path.abspath(os.path.join(os.curdir, "settings.yaml"))]

for a in attach:
    message.Attachments.Add(a)
# os.path.abspath("erase.json"))
# message.Attachments.add(os.path.abspath(os.path.join(os.curdir, "settings.yaml")))
message.Send()
