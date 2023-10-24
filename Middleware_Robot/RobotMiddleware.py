import requests
import threading
import time,pygame
import paho.mqtt.client as mqtt

# MQTT settings
mqtt_broker_address = "172.16.1.166"
mqtt_topic = "location"
incoming_data = None
def play_mp3(mp3_path):
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()
def on_message(client, userdata, message):
    global incoming_data
    incoming_data = message.payload.decode()

def send_data_to_server(data, server_url, results, index):
    payload = {'data': data}
    response = requests.post(server_url, json=payload)

    if response.status_code == 200:
        result = response.json().get('result')
        results[index] = result
    else:
        results[index] = f"Failed to send data. Response: {response.text}"
def call_remote_assign_robot(p):
    payload = {'data': p}
    roboturl = f'http://localhost:888{p}/assign_robot'
    response = requests.post(roboturl, json=payload)

    if response.status_code == 200:
        result = response.json().get('assigned_robot')
        return result
    else:
        return f"Failed to call remote function on the client. Response: {response.text}"

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(mqtt_broker_address, 1883)
    client.subscribe(mqtt_topic)
    client.loop_start()
    while True:
        # Wait for incoming MQTT data
        if incoming_data is not None:
            server_urls = ['http://localhost:8881/process_data', 'http://localhost:8882/process_data','http://localhost:8883/process_data']
            data_to_send = incoming_data
            results = [None] * len(server_urls)
            
            threads = []
            for i, server_url in enumerate(server_urls):
                thread = threading.Thread(target=send_data_to_server, args=(data_to_send, server_url, results, i))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            for i, result in enumerate(results):
                print(f"Received result from Robot {i + 1}: {result}")
            
            # Adjust the sleep time to control the frequency of sending data (e.g., every 5 seconds)
            
            min_result = min(results, key=lambda x: x if x is not None else float('inf'))
            if min_result == 1e1000:
                print("all robots are busy..wait")
            else:    
                print(f"Minimum result: {min_result}")
                for i, result in enumerate(results):
                    if min_result == result:
                        print ("Robot to assign", i+1)
                        p=i+1
                result1=call_remote_assign_robot(p) 
                play_mp3(r"C:\Users\Karthika\Middleware\assign.mp3")             
                print(f"Robot {result1} is assigned")
                incoming_data = None
        time.sleep(5)    