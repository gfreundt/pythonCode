import easyocr

READER = easyocr.Reader(["en"], gpu=False)
result = READER.readtext('captcha.jpg')

print(result)