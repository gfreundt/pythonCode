import requests


# Imports the Google Cloud client library
from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_file_name):
    storage_client = storage.Client(credentials='ya29.a0AfH6SMBZTXC2uIexeKflxKa_ai6Gv68c6FxSP08qWC7N_ePFCcf7D1ucYuj1NQ0pKn0HnexcEH3TFC1Px0tR_9mVxhoFjCNOJtF8CIzx6-Rm_sqSycT9LfriqeH7p3weLdC5999nFF1Y5xpFeDTOJiYFD_a0')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_file_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_file_name
        )
    )



bucket_name = "data-bucket-gft"
source_file_name = "D:/pythonCode/DolarPeru_data/TDC.txt"
destination_file_name = "/DolarPeru_data/yupi.txt"

upload_blob(bucket_name, source_file_name, destination_file_name)