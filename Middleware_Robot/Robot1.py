
import math,json
from threading import Thread
import time, pygame
from flask import Flask, request, jsonify

app = Flask(__name__)
def play_mp3(mp3_path):
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()

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
robot_name = "Robot1"
robot_data = load_robot_data(robot_name)        

def robot_cleanup():
    global lat,long
    time.sleep(3)
    play_mp3(r"C:\Users\Karthika\Middleware\going.mp3")
    print("Robot 1 is Going to location")
    time.sleep(5)
    play_mp3(r"C:\Users\Karthika\Middleware\inprogress.mp3")
    print("Cleaning in progress")
    time.sleep(10)
    play_mp3(r"C:\Users\Karthika\Middleware\Down.mp3")
    print("Cleaning done")
    robot_data["state"] = "Free"
    robot_data["latitude"] = lat
    robot_data["longitude"] = long
    save_robot_data(robot_name, robot_data)
    print("Database updated with new location")
    

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
    app.run(host='0.0.0.0', port=8881)
    