import argparse
import requests
import json
import sys
import os

job_id = str(sys.argv[1])


def get_api_information():
    path_configfile = os.path.expanduser("~") + os.sep + ".config" + os.sep + "rescale" + os.sep + "apiconfig"
    try:
        f = open(path_configfile, 'r', encoding='UTF8')
        lines = f.readlines()
        f.close()
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    api_baseurl = lines[1].split('=')[1].rstrip('\n').lstrip().replace("'", "")
    api_key = lines[2].split('=')[1].rstrip('\n').lstrip().replace("'", "")
    api_token = 'Token ' + api_key

    return api_baseurl, api_token


def get_job_information(api_baseurl, api_token):
    req = requests.get(
        api_baseurl + '/api/v2/jobs/' + job_id,
        # 'https://kr.rescale.com/api/v2/jobs/<Job ID>
        headers={'Authorization': api_token}
    )
    
    req_dict = json.loads(req.text)
    data = json.dumps(req_dict, indent=2)
    
    # Information of Job is written in Job_Info.txt file which is located at the same os api script
    f = open("Job_Info.txt", 'w')
    f.write(data)
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download files for a given job from Rescale')
    parser.add_argument('job_id', help='Job ID to download files for')
    args = parser.parse_args()
    api_baseurl, api_token = get_api_information()
    get_job_information(api_baseurl, api_token)
