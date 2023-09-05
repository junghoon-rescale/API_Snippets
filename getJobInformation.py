import requests
import json
import sys

# Input you API Key
apikey='Your API Key'

job_id = str(sys.argv[1])

req = requests.get(
    'https://kr.rescale.com/api/v2/jobs/' + job_id,
    # 'https://kr.rescale.com/api/v2/jobs/<Job ID>
    headers = {'Authorization': 'Token ' + apikey}
)

req_dict = json.loads(req.text)
data = json.dumps(req_dict, indent=2)

# Information of Job is written in Job_Info.txt file which is located at the same os API script
f = open("Job_Info.txt", 'w')
f.write(data)
f.close()
