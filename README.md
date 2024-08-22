# Backup Script for Atlassian Jira and Confluence
This project has been made to automate Jira and Confluence backups.

## Description
You can use this script and adapt it to your usage. To do so you will have to configure the following variables in order to make the script work:
* ATLASSIAN_SITE
* ATLASSIAN_TOKEN
* ATLASSIAN_USERNAME
* AZURE_STORAGE_URL

You can find these variables in Settings > CI/CD > Variables or [here](https://gitlab.sophiagenetics.io/efilleaufronville/atlassian-backup/-/settings/ci_cd#:~:text=of%20group%20runners.-,Variables,-Collapse)


## Installation
All the requirements for the python script to run are in the requirements.txt


## Usage
The expected use of this script is to combine it with a scheduler that triggers every Monday,Wednesday,Friday because Atlassian limits the number of backups to one every 48h.


## Contributing
This project is open to any kind of contribution and with great appreciation.

Here are few usefull links:
* https://jira.atlassian.com/browse/CLOUD-6498 (based on the solution provided here)
* https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview


## Authors and acknowledgment
Thanks Chris Aldridge for giving me this project.

