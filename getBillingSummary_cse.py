import os
import sys
import pandas as pd
import requests

"""
Arguments and Help for using this script
"""
startYear = None
startMonth = None
endYear = None
endMonth = None
numargs = len(sys.argv)


def printhelp():
    print("")
    print("Description: Rescale REST API Python script.")
    print("             Collects Billing Summaries for all the workspaces")
    print("             of a hardcoded organization and saves to csv file. \n")
    print(
        "Usage: getBillingSummary_cse.py [-help] -startYear <YYYY> -startMonth <MM> -endYear <YYYY> -endMonth <MM>")
    print("")


if numargs == 1:
    print("ERROR No arguments given! Try -help")
    exit()
elif numargs >= 2:
    for i in range(numargs):
        if sys.argv[i] == "-startYear":
            startYear = str(sys.argv[i + 1])
        if sys.argv[i] == "-startMonth":
            startMonth = str(sys.argv[i + 1])
        if sys.argv[i] == "-endYear":
            endYear = str(sys.argv[i + 1])
        if sys.argv[i] == "-endMonth":
            endMonth = str(sys.argv[i + 1])
        if sys.argv[i] == "-help":
            printhelp()
            exit()

"""
Get a information for running this script file - All of customer
"""
HOME = os.path.expanduser("~")
PATH_APICONFIG = HOME + "\\.config\\rescale\\apiconfig-CWS"
try:
    f = open(PATH_APICONFIG, 'r', encoding='UTF8')
    lines = f.readlines()
    f.close()
except FileNotFoundError as e:
    print(e)
    sys.exit(1)

List_companycode = []
List_workspacename = []
List_workspaceid = []
List_apikey = []

for i in range(7):
    List_companycode.append(lines[i].split('/')[0].rstrip('\n').lstrip().replace("'", ""))
    List_workspacename.append(lines[i].split('/')[1].split('=')[0].rstrip('\n').lstrip().replace("'", ""))
    List_workspaceid.append(lines[i].split('=')[1].split(':')[0].rstrip('\n').lstrip().replace("'", ""))
    List_apikey.append(lines[i].split('=')[1].split(':')[1].rstrip('\n').lstrip().replace("'", ""))

Dict_codeid = {x: y for x, y in zip(List_companycode, List_workspaceid)}
Dict_codeapikey = {x: y for x, y in zip(List_companycode, List_apikey)}

DF_info = pd.DataFrame(
    [List_companycode, List_workspaceid, List_apikey],
    index=['code', 'id', 'apikey'],
    columns=List_workspacename
).transpose()

"""
Get a billing summary from each of customers
"""


def getbilling(ccode, wsid, wsapikey, sy, sm, ey, em):
    r = requests.get(
        'https://kr.rescale.com/api/v2/organizations/{}/workspaces/{}/billing/'.format(ccode, wsid),
        headers={'Content-Type': 'application/json',
                 'Authorization': 'Token {}'.format(wsapikey)},
        params={'startYear': sy,
                'startMonth': sm,
                'endYear': ey,
                'endMonth': em},
    )
    return r


List_wsid = []
List_wslabel = []
List_wsactiveUsers = []
List_wsjobs = []
List_hardwareUsage = []
List_hardwareCharge = []
List_softwareCharge = []
List_storageUsage = []
List_storageCharge = []
List_transferUsage = []
List_transferCharge = []
List_connectionsCharge = []
List_platformCharge = []
List_deposits = []
List_appliedCredit = []
List_appliedDeposit = []
List_Total = []

for key in Dict_codeid:
    billing = getbilling(key, Dict_codeid[key], Dict_codeapikey[key], startYear, startMonth, endYear, endMonth)
    json_dict = billing.json()
    List_wsid.append(json_dict["id"])
    List_wslabel.append(json_dict["label"])
    List_wsactiveUsers.append(json_dict["activeUsers"])
    List_wsjobs.append(json_dict["jobs"])
    List_hardwareUsage.append(json_dict["hardwareUsage"])
    List_hardwareCharge.append(json_dict["hardwareCharge"])
    List_softwareCharge.append(json_dict["softwareCharge"])
    List_storageUsage.append(json_dict["storageUsage"])
    List_storageCharge.append(json_dict["storageCharge"])
    List_transferUsage.append(json_dict["transferUsage"])
    List_transferCharge.append(json_dict["transferCharge"])
    List_connectionsCharge.append(json_dict["connectionsCharge"])
    List_platformCharge.append(json_dict["platformCharge"])
    List_deposits.append(json_dict["deposits"])
    List_appliedCredit.append(json_dict["appliedCredit"])
    List_appliedDeposit.append(json_dict["appliedDeposit"])
    List_Total.append(json_dict["totalCharge"])

DF_billing = pd.DataFrame(
    [List_wsactiveUsers, List_wsjobs, List_hardwareUsage, List_hardwareCharge, List_softwareCharge, List_storageUsage,
     List_storageCharge, List_transferUsage, List_transferCharge, List_connectionsCharge, List_platformCharge,
     List_deposits, List_appliedCredit, List_appliedDeposit, List_Total],
    index=['Active Users', 'Jobs', 'Core Hours', 'Compute [$]', 'Software [$]', 'Storage Usage [B]', 'Storage [$]',
           'Transfer Usage [B]', 'Transfer [$]', 'Connections [$]', 'Platform [$]', 'Deposits [$]',
           'Applied Credits [$]', 'Applied Deposits [$]', 'Total [$]'],
    columns=List_workspacename
).transpose()

CSV_FOLDER = 'C:\\Rescale\\Usage_Analysis'
CSV_NAME = 'Usage_report__From_{}-{}__To_{}-{}.csv'.format(startYear, startMonth, endYear, endMonth)
CSV_PATH = CSV_FOLDER + '\\' + CSV_NAME

DF_billing.to_csv(CSV_PATH)
