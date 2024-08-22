import requests
import time
import re
from azure.storage.fileshare import ShareFileClient
import os
from base64 import b64encode
import tempfile
import datetime
import sys
import threading 

def progressBar(dl,name):
    done = int(100 * dl / 100)
    sys.stdout.write("\r Updating the "+name+" backup: |%s%s| " % ('▓' * done, '░' * (100-done)) + "(" + str(dl) + "%)" )    
    sys.stdout.flush()

def conf_backup(account, basic, az_url):
    # Create the full base url for the JIRA instance using the account name.
    url = 'https://' + account + '.atlassian.net/wiki'
    # Open new session for cookie persistence and auth.
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "Content-Type": "application/json",  "Authorization": "Basic "+basic})
    #Start the backup for confluence
    json = b'{"cbAttachments": "true", "exportToCloud": "true"}'
    backup_start = session.post(url + '/rest/obm/1.0/runbackup', data=json)
    # Catch error response from backup start and exit if error found.
    backup_resp_code = int(re.search(r'(?<=<Response \[)(.*?)(?=\])', str(backup_start)).group(1))
    if backup_resp_code != 200:
        print("Confluence: "+backup_start.text, flush=True)
        if 'frequency is limited' in backup_start.text or 'Another export is' in backup_start.text :
            print("")
        else:
            exit(1)

    #if datetime.datetime.today().weekday() == 3:
        #Wait until the backup is completed
    progress_req = session.get(url + '/rest/obm/1.0/getprogress')
    task_progress = int(progress_req.json()["alternativePercentage"])
    while task_progress != 100:
        progressBar(task_progress,"Confluence")
        time.sleep(300)
        task_progress = int(progress_req.json()["alternativePercentage"])
    print(progress_req.text)
    file_name = str(progress_req.json()["fileName"])
    #Proceed saving the backup in Azure
    if file_name != 'None':
        date = time.strftime("%d-%b-%Y")
        filename = "confluence-export("+date+").zip"
        try:
            print("-")
            sfc = ShareFileClient.from_connection_string(conn_str=az_url,share_name="prod-eu-w-confluencecloud-backups",file_path=filename)
            print("0")
            files = session.get(url + '/download/' + file_name, stream=True)
            print("1")
            files.raise_for_status()
            print("2")
            with open(files.content) as handle:
                print("3")
                sfc.upload_file(bytes(handle),length=sys.getsizeof(handle) )
            print("The Confluence backup have succesfully been uploaded to Azure.", flush=True)
        except:
            print("An error was raised during the uploading of the confluence backup to Azure. Please do it manually.", flush=True)


def jira_backup(account, basic, az_url):
    # Create the full base url for the JIRA instance using the account name.
    url = 'https://' + account + '.atlassian.net'
    # Open new session for cookie persistence and auth.
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Basic "+basic})
    #Start the backup for Jira
    json = b'{"cbAttachments": "true", "exportToCloud": "true"}'
    backup_req = session.post(url + '/rest/backup/1/export/runbackup', data=json)
    backup_resp_code = int(re.search(r'(?<=<Response \[)(.*?)(?=\])', str(backup_req)).group(1))
    # Catch error response from backup start and exit if error found.
    if backup_resp_code != 200:
        print("Jira: "+backup_req.json()["error"], flush=True)
        if 'frequency is limited' in backup_req.json()["error"] or 'Another export is' in backup_req.json()["error"] :
            print("")
        else:
            exit(1)

    #if datetime.datetime.today().weekday() == 4:
    
    # Get task ID of backup.
    task_req = session.get(url + '/rest/backup/1/export/lastTaskId')
    task_id = task_req.text
    # set starting task progress values outside of while loop and if statements.
    progress_req = session.get(url + '/rest/backup/1/export/getProgress?taskId=' + task_id)
    task_progress = int(progress_req.json()["progress"])
    while task_progress != 100:
        progressBar(task_progress,"Jira")
        time.sleep(300)
        progress_req = session.get(url + '/rest/backup/1/export/getProgress?taskId=' + task_id)
        task_progress = int(progress_req.json()["progress"])
    download = progress_req.json()["result"]
    print(download)
    date = time.strftime("%d-%b-%Y")
    filename = "jira-export("+date+").zip"
    #file = session.get(url + '/plugins/servlet/' + download, stream=True)
    try:
        print("-")
        sfc = ShareFileClient.from_connection_string(conn_str=az_url,share_name="prod-eu-w-confluencecloud-backups",file_path=filename)
        print("0")
        files = session.get(url + '/plugins/servlet/' + download, stream=True)
        print("1")
        files.raise_for_status()
        print("2")
        with open(files.content) as handle:
            print("3")
            sfc.upload_file(bytes(handle),length=sys.getsizeof(handle) )
        print("The Jira backup have succesfully been uploaded to Azure.", flush=True)
    except:
        print("An error was raised during the uploading of the jira backup to Azure. Please do it manually.", flush=True)



def main():

    site = os.environ.get("ATLASSIAN_SITE")
    at_username = os.environ.get("ATLASSIAN_USERNAME")
    at_token = os.environ.get("ATLASSIAN_TOKEN")
    az_url = os.environ.get("AZURE_STORAGE_URL")
    login = at_username+':'+at_token
    basic = b64encode(login.encode('ascii')).decode('ascii')


    t1 = threading.Thread(target=jira_backup, args=(site, basic, az_url))
    t2 = threading.Thread(target=conf_backup, args=(site, basic, az_url))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    #jira_backup(site, basic, az_url)

    #conf_backup(site, basic, az_url)

    if datetime.datetime.today().weekday() != 3:
        print("Backups get upload only on Friday's, this backup won't be uploaded on Azure !")

if __name__ == '__main__':
    main()
