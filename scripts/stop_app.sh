#!/usr/bin/env bash

# ##################################################
# Stop_App Script
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
entryPoint="calithumpian.py"

# send start message to console
echo "Beginning stop_app.sh helper script"

# run command
ps -ef | grep $entryPoint | grep -v grep | awk '{print $2}' | xargs kill

# Send end message to console
echo "$application stopped!"
