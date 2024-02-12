import requests
import json
import sys

# Input you API Key
apikey='958c3d92ae0dce4feec0d1957f3aedde876e9f7c'

#file_id = str(sys.argv[1])

req = requests.get(
#    'https://kr.rescale.com/api/v2/files/' + file_id,
    'https://kr.rescale.com/api/v2/files/',
    # 'https://kr.rescale.com/api/v2/files/<File ID>
    headers = {'Authorization': 'Token ' + apikey}
)

req_dict = json.loads(req.text)
data = json.dumps(req_dict, indent=2)

# Information of Job is written in Job_Info.txt file which is located at the same os API script
f = open("File_Info.txt", 'w')
f.write(data)
f.close()
