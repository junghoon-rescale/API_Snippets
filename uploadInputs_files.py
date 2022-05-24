import os
import sys
import requests
import json
from time import sleep
from pathlib import Path
from tqdm import tqdm


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

for file in Path(PATH_FOLDER_INPUTS).iterdir():
    file_name = str(file)
    # When you use iterdir(), the datatype is not a string. But print(file) would be displayed the string of path.
    List_inputfiles.append(file_name)

num_inputfiles = len(List_inputfiles)
List_inputfilesid = []
pbar = tqdm(List_inputfiles)

for file in pbar:
    sleep(0.1)
    pbar.set_description_str(f'Uploading {file}')
    try:
        uploading = requests.post(
            API_uploadurl,
            data=None,
            headers={"Authorization": API_token},
            files={"file": open(file, "rb")},
        )
        if uploading.status_code == 201:
            uploading_dict = json.loads(uploading.text)
            inputfile_id = uploading_dict['id']
            List_inputfilesid.append(inputfile_id)
        else:
            print('Uploading ' + file.split('\\')[-1] + ' is failed')
            exit(1)
    except FileNotFoundError as e:
        print(e)
        exit(1)
