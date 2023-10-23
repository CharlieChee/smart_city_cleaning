# server1.py
import math,json
from threading import Thread
import time


def load_robot_data(robot_name):
    with open('RobotData.json', 'r') as file:
        robot_data = json.load(file)
    return robot_data.get(robot_name, {})
def save_robot_data(robot_name, robot_data):
    with open('RobotData.json', 'r') as file:
        all_robot_data = json.load(file)
    all_robot_data[robot_name] = robot_data  # Update data for the specific robot
    with open('RobotData.json', 'w') as file:
        json.dump(all_robot_data, file, indent=4)
robot_name = "Robot2"
robot_data = load_robot_data(robot_name)        

def robot_cleanup():
    global lat,long
    print("cleaning in progress")
    time.sleep(10)
    print("Cleaning done")
    robot_data["state"] = "Free"
    robot_data["latitude"] = lat
    robot_data["longitude"] = long
    #print(dict)
    save_robot_data(robot_name, robot_data)
    

def haversine_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    radius = 6371
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c
    dist=round(distance, 2)
    return dist

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process_data', methods=['POST'])
def process_data():
    global lat, long
    data = request.json.get('data')
    numbers = data.split("_")
    if data:
        if robot_data["state"] == "Free":
            #if numbers and len(numbers) == 2:
                lat = float(numbers[0])
                long = float(numbers[1])
                result=haversine_distance(lat, long, robot_data["latitude"], robot_data["longitude"])
                return jsonify({"result": result})
        else:
            return jsonify({"result": 1e1000})
    else:
        return jsonify({"error": "No data received"})
    
@app.route('/assign_robot', methods=['POST'])
def assign_robot():
    data = request.json.get('data')
    if data:
            # Assign the robot and change its state
            robot_data["state"] = "Busy"
            Thread(target=robot_cleanup).start()
            return jsonify({"assigned_robot": robot_data["name"]})
    else:
        return jsonify({"error": "No data received"})

        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8882)
    