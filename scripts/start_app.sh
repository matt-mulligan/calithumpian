#!/usr/bin/env bash

# ##################################################
# Start_App Script
# Starts the flask application in its pipenv environment
#
version="1.0.0"               # Sets version variable
# HISTORY:
#
# * 2020-04-13 - v1.0.0  - Initial creation
#
# ##################################################

# Provide a variable with the location of this script.
scriptPath="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
application="calithumpian"
logDate=$(date '+%Y%m%d_%H%M%S')
logName="calithumpian_webserver_$logDate.log"
logPath="/var/application_logs/$application"
logPathFull="$logPath/$logName"
entryPoint="calithumpian.py"

# send start message to console
echo "Beginning start_app.sh helper script"

# change dir
cd "$scriptPath/.." || echo "CD FAILED :("
currentDir=$(pwd)
echo "current directory is $currentDir"


# run pipenv
echo "Command to run is 'pipenv run python $entryPoint > $logPathFull &'"
nohup pipenv run python $entryPoint &> "$logPathFull" &

# Send end message to console
echo "$application started! logs can be found at $logPathFull"
