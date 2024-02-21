import requests
import json
import sys
import os
import argparse
from datetime import datetime

# Get the api key from apiconfig file(if exist)
HOME = os.path.expanduser("~")
PATH_APICONFIG = HOME + os.sep + ".config" + os.sep + "rescale" + os.sep + "apiconfig"
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
URL_job = API_baseurl + '/api/v2/jobs/'


# Create an argument parser
parser = argparse.ArgumentParser(description='Retrieve job information from Rescale API with optional date range.')

# Add optional date range arguments
parser.add_argument('--start_date', help='Start date in YYYY-MM-DD format')
parser.add_argument('--end_date', help='End date in YYYY-MM-DD format')

# Parse the command line arguments
args = parser.parse_args()

# Check if start_date and end_date were provided, otherwise set them to None
start_date = args.start_date if args.start_date else None
end_date = args.end_date if args.end_date else None

# Calculate date range
if start_date and end_date:
    date_range = f"?start_date={start_date}&end_date={end_date}"
elif start_date:
    date_range = f"?start_date={start_date}"
elif end_date:
    date_range = f"?end_date={end_date}"
else:
    date_range = ""

# Create the API URL
api_url = f'https://kr.rescale.com/api/v2/jobs/{args.job_id}{date_range}'

# Send the request
req = requests.get(api_url, headers={'Authorization': 'Token ' + apikey})

# Check the response status code
if req.status_code == 200:
    req_dict = json.loads(req.text)
    data = json.dumps(req_dict, indent=2)

    # Information of the job is written in Job_Info.txt file
    with open("Job_Info.txt", 'w') as f:
        f.write(data)
else:
    print(f"Failed to retrieve job information. Status code: {req.status_code}")
'''