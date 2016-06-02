#!/usr/bin/env python


##########################################################################################################
# Import statements
# This script requires the following Pyton modules
# json, base64, datetime, sys, argparse
# use PIP import for these if you are encoutering errors for pytz, requests, iso8601
#   > pip install requests, pytz, iso8601
#

import json, base64, requests, datetime, sys, argparse, pytz, iso8601
from config import clientID, clientSecret, apiurl, deactivate_num_days, moveToGroupName, moveToGroupID

##########################################################################################################


##########################################################################################################
# Variables
# Please edit these values in the config.auth.  You can find these information from HALO "[Site Administration] -> [API Keys]" page
if len(clientID) == 8 and len(clientSecret) == 32:
    api_key_id = clientID
    api_secret_key = clientSecret
    api_request_url = apiurl
else:
    print "NO API KEY CONFIGRED!"
    print "Please configure API Key in config.py"
    print "Exiting..."
    sys.exit(1)

if not (moveToGroupName or moveToGroupID):
    print "NO GROUP TO MOVE TO CONFIGRED!"
    print "Please configure destination group in config.py"
    print "Exiting..."
    sys.exit(1)

# Other variables
client_credential = api_key_id + ":" + api_secret_key
user_credential_b64 = "Basic " + base64.b64encode(client_credential)

##########################################################################################################


def get_headers():
    # Create headers
    reply = get_access_token(api_request_url, "/oauth/access_token?grant_type=client_credentials",
                             {"Authorization": user_credential_b64})
    reply_clean = reply.encode('utf-8')
    headers = {"Content-type": "application/json", "Authorization": "Bearer " + reply_clean}
    return headers

def get_access_token(url, query_string, headers):
    reply = requests.post(url + query_string, headers=headers)
    return reply.json()["access_token"]

def move_group(host_id,group_id):
    data = { "server": {"group_id": group_id}}
    status_code = str("404")
    moveurl = apiurl + "/v1/servers/" + host_id
    #print ("URL: %s") % moveurl
    #print ("Request Body: %s" % data)
    reply = requests.put( moveurl, data=json.dumps(data), headers=headers)
    status_code = str(reply.status_code)
    print ("Result of group move: %s" % status_code)
    return True

def get_group_id(groupName):
    groupurl = api_request_url + "/v1/groups"
    reply = requests.request("GET", groupurl, data=None, headers=headers)
    for group in reply.json()["groups"]:
        if group['name'] == groupName:
            return group['id']


def move_deactivated_servers():
    deactivatedServersURL = api_request_url + "/v1/servers?state=deactivated"
    reply = requests.request("GET", deactivatedServersURL, data=None, headers=headers)
    servers_moved = 0
    servers_ignored = 0
    servers_previously_moved = 0
    for server in reply.json()["servers"]:
        if (moveToGroupID):
            newgroupID = str(moveToGroupID)
            #print "group_id set to %s" % newgroupID
        else:
            newgroupID = str(get_group_id(moveToGroupName))
            #print "Moving to group %s with group_id: %s" % moveToGroupName, newgroupID
            #print moveToGroupName, newgroupID
        server_id = server['id']
        server_hostname = server['hostname']
        # How many days should a server be offline before being retired?
        #retire_days = -1
        deactivate_days = deactivate_num_days
        # Create aware datetime object for last time seen
        lastseen = iso8601.parse_date(server['last_state_change'])

        # Create aware datetime object for current time
        utc = pytz.timezone('UTC')
        utcnow = datetime.datetime.utcnow()
        utcnow_aware = utc.fromutc(utcnow)

        # Calculate time diff in days
        # After 1 day, last_state_change rounds off to days
        time_diff = utcnow_aware - lastseen
        diff_days = int(time_diff.days)

        # Don't move a server that's already in the desired deactivated group
        if server['group_name'] == moveToGroupName:
            print "Server %s already moved -- ignoring." % server_hostname
            servers_previously_moved += 1

        # If server older than retire_days days, move to retired
        elif (diff_days > deactivate_days and server_id):
            #print server_id
            #print server_hostname
            #print newgroupID
            data  = move_group(server['id'],newgroupID)
            if data:
                print "Server %s moved successfully." % server_hostname
                servers_moved += 1
            else:
                print "Unable to move server."
                if not server_id:
                    print "Server: %s (id %s) does not exist.\n" % (server_hostname, server_id)
                elif diff_days <= deactivate_days:
                    print "Server %s has been offline for %s days.\n" % (server_hostname, diff_days)
                    servers_ignored += 1
    print "\n********Script Summary********"
    print "Servers moved: %d" % servers_moved
    print "Servers ignored, less than specified days deactivated: %d " % servers_ignored
    print "Servers already in deactivated group: %d" % servers_previously_moved
    current_date_time = datetime.datetime.now()
    print "Script completed: %s" % current_date_time
    print "********************************"
#---MAIN---------------------------------------------------------------------


headers=get_headers()
move_deactivated_servers()
