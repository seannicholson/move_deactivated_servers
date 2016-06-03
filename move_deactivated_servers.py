###############################################################################
# Import statements
# This script requires the following Python modules
# json, base64, datetime, sys, argparse
# use PIP import for these if you are encountering errors for pytz, requests,
# iso8601
#   > pip install requests, pytz, iso8601
#

import json, base64, requests, datetime, sys, argparse, pytz, iso8601
from config import clientID, clientSecret, apiurl, deactivate_num_days, moveToGroupName, moveToGroupID

###############################################################################


###############################################################################
# Variables
# Please edit these values in the config.auth.  You can find these information
# from HALO "[Site Administration] -> [API Keys]" page

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
###############################################################################
# Other variables
client_credential = api_key_id + ":" + api_secret_key
user_credential_b64 = "Basic " + base64.b64encode(client_credential)

###############################################################################

###############################################################################
# Define Methods

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
    retry_loop_counter = 0
    moveurl = apiurl + "/v1/servers/" + host_id
    #print ("URL: %s") % moveurl
    #print ("Request Body: %s" % data)

    # Loop to attempt server move PUT request
    # will retry 4 times to move server if status_code not 204
    while (retry_loop_counter < 3):
        reply = requests.put( moveurl, data=json.dumps(data), headers=headers)
        status_code = str(reply.status_code)
        #print ("Result of group move: %s" % status_code)
        retry_loop_counter += 1
        if status_code == "204":
            # Arbitrary number to exit loop
            retry_loop_counter = 5
            return True
        else:
            print "Failed to move server...Retry attempt %d" % retry_loop_counter


# Get groupID from group name specified
def get_group_id(groupName):
    groupID_found = 0
    groupurl = api_request_url + "/v1/groups"
    reply = requests.request("GET", groupurl, data=None, headers=headers)
    for group in reply.json()["groups"]:
        if group['name'] == groupName:
            newgroupID = group['id']
            groupID_found += 1
    # Sanity checks for group name matched
    if groupID_found == 1:
        return newgroupID
    elif groupID_found > 1:
        print "More than 1 group matched group name"
        print "Please specify unique group name"
        print "Exiting..."
        sys.exit(1)
    else:
        print "Group name match not found"
        print "Please check group name or API Key scope"
        print "Exiting..."
        sys.exit(1)

# check for defined groupID to move servers to
# if not groupID specified in config file, then
# run get_group_id
def check_group_id():
    if (moveToGroupID):
        newgroupID = str(moveToGroupID)
        #print "group_id set to %s" % newgroupID
        return newgroupID
    else:
        newgroupID = str(get_group_id(moveToGroupName))
        #print "Moving to group %s with group_id: %s" % moveToGroupName, newgroupID
        #print moveToGroupName, newgroupID
        return newgroupID

def get_deactivated_server_list():
    deactivatedServersURL = api_request_url + "/v1/servers?state=deactivated"
    reply = requests.request("GET", deactivatedServersURL, data=None, headers=headers)
    return reply

def move_deactivated_servers():
    global newgroupID
    servers_moved = 0
    servers_ignored = 0
    servers_previously_moved = 0

    # Check for defined groupID to move servers to
    #print "Move to Group ID: %s" % moveToGroupID
    newgroupID = check_group_id()

    # How many days should a server be offline before being moved?
    deactivate_days = deactivate_num_days

    # Get list of deactivated servers
    reply = get_deactivated_server_list()

    # Loop through deactivated servers list
    # and move if move criteria met
    for server in reply.json()["servers"]:
        server_id = server['id']
        server_hostname = server['hostname']

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

        # If server older than deactivate_days days, move to newgroupID
        elif (diff_days > deactivate_days and server_id):
            #print server_id
            #print server_hostname
            #print newgroupID
            # Move Server to Deactivated group
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

    #Print summary of script actions
    print "\n********Script Summary********"
    print "Servers moved: %d" % servers_moved
    print "Servers ignored, less than specified days deactivated: %d " % servers_ignored
    print "Servers already in deactivated group: %d" % servers_previously_moved
    current_date_time = datetime.datetime.utcnow()
    print "Script completed: %s UTC" % current_date_time
    print "********************************"
###############################################################################


#---MAIN---------------------------------------------------------------------


headers=get_headers()
move_deactivated_servers()
