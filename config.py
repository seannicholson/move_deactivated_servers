
#*******************  Variables  **********************
# clientid:         API key
# clientsecret:     API secret
# apiurl            Halo API URL
# moveToGroup       Server Group to move deactivated servers to
# moveToGroupID     Server Group ID in hex format
# retire_num_days   Number of days that a server has to be deactivated for
#******************************************************

#******************************************************
# IMPORTANT:
#   Ensure the group you want to move to is within the scope
#   of the API Key specified
#******************************************************
#clientID     = '1234ABCD'
#clientSecret = '050732791334f4a04c9ab64d572625d7'
clientID     = ''
clientSecret = ''
#******************************************************

#******************************************************
# Default value do not change unless instructed to by
# CP Customer Success
apiurl = 'https://api.cloudpassage.com'
#******************************************************

#******************************************************
# Specify name of group to move deactivated servers to
# IMPORTANT: Must be exact name match
# moveToGroupName  = 'X-Deactivated Servers'
moveToGroupName  = ''
#******************************************************
#******************************************************
# Specify group ID if known
# (uuid format 0123456789ABCDE0123456789ABCDE)
# Leave moveToGroupID blank if not known
moveToGroupID = ''
#******************************************************

#******************************************************
# Specify number of Days a server should be deactivated
# Default value is 7
# for to move choose a value of -1 to move all
# deactivated servers regardless of time deactivated
deactivate_num_days = 7
#******************************************************
