import os
import sys
import json
import time
from tqdm import tqdm
import argparse
import requests

# Getting a api settings from apiconfig
def get_api_information(path_home):
    path_apiconfig = path_home + os.sep + ".config" + os.sep + "rescale" + os.sep + "apiconfig"
    try:
        f = open(path_apiconfig, 'r', encoding='UTF8')
        lines = f.readlines()
        f.close()
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    api_baseurl = lines[1].split('=')[1].rstrip('\n').lstrip().replace("'", "")
    api_key = lines[2].split('=')[1].rstrip('\n').lstrip().replace("'", "")
    api_token = 'Token ' + api_key

    return api_baseurl, api_token

def get_jobname(api_baseurl, api_token, job_id):
    job_url = f'{api_baseurl}/api/v2/jobs/{job_id}'
    req = requests.get(
        job_url,
        # 'https://kr.rescale.com/api/v2/jobs/<Job ID>
        headers={'Authorization': api_token}
    )

    req_dict = json.loads(req.text)
#    data = json.dumps(req_dict, indent=2)
    job_name = req_dict['name']

    return job_name


def download_outputfile(api_baseurl, api_token, job_id, path_output):
    jobfile_url = f'{api_baseurl}/api/v2/jobs/{job_id}/files/'
    current_page = 1
    last_page = False

    # Initialize lists to store file info
    postoutputfileid = []
    postoutputfilename = []
    postoutputfileurl = []

    while not last_page:
        response = requests.get(
            jobfile_url,
            headers={'Authorization': api_token},
            params={'page': current_page},
        )
        data = response.json()

        # Process each file in the current page
        for result in data['results']:
            postoutputfileid.append(result['id'])
            postoutputfilename.append(result['name'])
            postoutputfileurl.append(result['downloadUrl'])

        # Check if there's a next page
        last_page = (data['next'] is None)
        if not last_page:
            current_page += 1

    # Combine the file names and IDs into a dictionary
    output_files_info = dict(zip(postoutputfilename, postoutputfileid))

    # Specify multiple file extensions
    outputfileextensions = ['.odb', '.dat', '.msg']

    # Filter for specified file extensions
    outputfileidlist = [output_files_info[name] for name in output_files_info if
                        any(name.endswith(ext) for ext in outputfileextensions)]

    if not os.path.exists(path_output):
        os.makedirs(path_output)
        print(f'{path_output} created in Downloads directory.')
    else:
        print(f'{path_output} already exists in Downloads directory')

    # Download files with the specified extensions
    for file_id in outputfileidlist:
        processingfile_name = next(name for name, id_ in output_files_info.items() if id_ == file_id)
        outputfile_url = f'{api_baseurl}/api/v2/files/{file_id}/contents/'
        response = requests.get(
            outputfile_url,
            headers={'Authorization': api_token},
            stream=True
            # Stream the response content
        )

        path_output_job = os.path.join(path_output, processingfile_name)

        # Get the total file size from the response headers
        file_size = int(response.headers.get('content-length', 0))

        with open(path_output_job, 'wb') as fd:
            downloaded_size = 0  # Initialize the downloaded size
            chunk_size = 1024 * 1024
            pbar = tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
                        desc=processingfile_name, dynamic_ncols=True)
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    fd.write(chunk)
                    downloaded_size += len(chunk)  # Update the downloaded size
                    pbar.update(len(chunk))
                    if downloaded_size > 0:
                        percent_complete = (downloaded_size / file_size) * 100
                        pbar.set_description(f"{processingfile_name} ({percent_complete:.2f}%)")
            pbar.close()

        print(f"Download completed successfully: {processingfile_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download files for a given job from Rescale')
    parser.add_argument('job_id', help='Job ID to download files for')
    parser.add_argument('--resume', '-r', action='store_true', help='Enable resuming of downloads (default: False)')
    args = parser.parse_args()

    path_home = os.path.expanduser("~")
    path_downloads = os.path.join(path_home, 'Downloads')
    api_baseurl, api_token = get_api_information(path_home)
    job_name = get_jobname(api_baseurl, api_token, args.job_id)
    path_output = os.path.join(path_downloads, job_name)
    download_outputfile(api_baseurl, api_token, args.job_id, path_output)
