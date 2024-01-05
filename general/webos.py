from pywebostv.discovery import *  # Because I'm lazy, don't do this.
from pywebostv.connection import *
from pywebostv.controls import *

# 1. For the first run, pass in an empty dictionary object. Empty store leads to an Authentication prompt on TV.
# 2. Go through the registration process. `store` gets populated in the process.
# 3. Persist the `store` state to disk.
# 4. For later runs, read your storage and restore the value of `store`.
"""if your_custom_storage_is_empty():
    store = {}
else:
    store = load_from_your_custom_storage()"""

store = {}

# Scans the current network to discover TV. Avoid [0] in real code. If you already know the IP,
# you could skip the slow scan and # instead simply say:
#    client = WebOSClient("<IP Address of TV>")
# or for newer models:
#    client = WebOSClient("<IP Address of TV>", secure=True)
client = WebOSClient.discover(
    secure=True
)  # Use discover(secure=True) for newer models.
client.connect()
for status in client.register(store):
    if status == WebOSClient.PROMPTED:
        print("Please accept the connect on the TV!")
    elif status == WebOSClient.REGISTERED:
        print("Registration successful!")

# Keep the 'store' object because it contains now the access token
# and use it next time you want to register on the TV.
print(store)  # {'client_key': 'ACCESS_TOKEN_FROM_TV'}

# persist_to_your_custom_storage(store)
