import os
import sys
import requests
import json
from pathlib import Path
from requests_toolbelt import MultipartEncoder
from requests_toolbelt import MultipartEncoderMonitor


# Getting a api settings from apiconfig
HOME = os.path.expanduser("~")
PATH_APICONFIG = HOME + "\\.config\\rescale\\apiconfig"
try:
    f = open(PATH_APICONFIG, 'r', encoding='UTF8')
    lines = f.readlines()
    f.close()
except FileNotFoundError as e:
    print(e)
    sys.exit(1)

API_baseurl = lines[1].split('=')[1].rstrip('\n').lstrip().replace("'", "")
API_key = lines[2].split('=')[1].rstrip('\n').lstrip().replace("'", "")
API_token = 'Token ' + API_key
API_uploadurl = API_baseurl + '/api/v2/files/contents/'

# This PATH block should be change for your folder structure
CWD = os.getcwd()
FOLDER_INPUTS = 'Test_Inputs'
PATH_FOLDER_INPUTS = os.path.dirname(CWD) + '\\' + FOLDER_INPUTS

List_inputfiles = []
List_inputfileid = []

for file in Path(PATH_FOLDER_INPUTS).iterdir():
    file_name = str(file)
    List_inputfiles.append(file_name)

for i in range(len(List_inputfiles)):
    try:
        with open(List_inputfiles[i], "rb") as ifile:

            def upload_status(monitor):
                sys.stdout.write('\r'+List_inputfiles[i]+' {:.2f}% uploaded ({} of {} bytes)'.format(
                    100.0 * monitor.bytes_read / monitor.len, monitor.bytes_read, monitor.len))
                sys.stdout.flush()

            encoder = MultipartEncoder(fields={"file": (ifile.name, ifile)})
            monitor = MultipartEncoderMonitor(encoder, upload_status)

            uploading = requests.post(
                API_uploadurl,
                data=monitor,
                headers={"Authorization": API_token,
                         "Content-Type": encoder.content_type},
            )

            if uploading.status_code == 201:
                print(' - Uploading the ' + List_inputfiles[i].split('\\')[-1] + ' is completed')
                uploading_dict = json.loads(uploading.text)
                inputfile_id = uploading_dict["id"]
                List_inputfileid.append({"id": inputfile_id[i], "decompress": False})
            else:
                print('Uploading ' + List_inputfiles[i] + ' is failed')
                exit(1)
    except FileNotFoundError as e:
        print(e)
        exit(1)