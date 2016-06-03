
#*******************  Variables  **********************
# apiurl            Halo API URL
# api_keys_path     Path to api_keys.txt file
# moveToGroup       Server Group to move deactivated
#                   servers to
# retire_num_days   Number of days that a server has to
#                   be deactivated for
#******************************************************

#******************************************************
# Default value do not change unless instructed to by
# CP Customer Success
apiurl = 'https://api.cloudpassage.com'
#******************************************************

#******************************************************
# Default value ./api_keys.txt, change to path of
# api_keys file if not stored in same directory as
# the script files
api_keys_path = './api_keys.txt'
#******************************************************

#******************************************************
# Specify name of group to move deactivated servers to
# IMPORTANT: Must be exact name match
# moveToGroupName  = 'X-Deactivated Servers'
moveToGroupName  = ''
#******************************************************

#******************************************************
# Specify number of Days a server should be deactivated
# Default value is 7
# for to move choose a value of -1 to move all
# deactivated servers regardless of time deactivated
deactivate_num_days = 7
#******************************************************
