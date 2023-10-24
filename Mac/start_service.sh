#!/bin/bash

# 1. Check if Hadoop is already running
if ! jps | grep -q "NameNode"; then
    echo "Starting Hadoop..."
    /usr/local/Cellar/hadoop/3.3.6/libexec/sbin/start-all.sh
else
    echo "Hadoop is already running."
fi

# 2. Check if Mosquitto is already running
if ! brew services list | grep -q "mosquitto.*started"; then
    echo "Starting Mosquitto..."
    brew services start mosquitto
else
    echo "Mosquitto is already running."
fi

# Open a new terminal and run the first Python script
osascript -e 'tell app "Terminal" to do script "python3 /Users/jichanglong/PycharmProjects/pythonProject/vedio_picture.py"'

# Open a new terminal and run the second Python script
osascript -e 'tell app "Terminal" to do script "python3 /Users/jichanglong/PycharmProjects/pythonProject/state_machine.py"'

# Open a new terminal and run the third Python script
osascript -e 'tell app "Terminal" to do script "python3 /Users/jichanglong/PycharmProjects/pythonProject/test_mysql.py"'
