import subprocess
import time
import paho.mqtt.client as mqtt
import pygame
import tkinter as tk
import random
import mysql.connector

class TableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Table Example")
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        # Create table titles
        self.titles = ["Zone", "Current Value", "Lasting Time", "Arriving Value", "Next Operation"]

        # Initialize last time
        self.last_time = time.time()

        # Rows and columns
        self.rows = 12
        self.cols = 5

        self.row_last_time = {}

        # Populate table content
        self.populate_table()

        # Set column and row weights to allow resizing
        for col in range(self.cols):
            self.frame.columnconfigure(col, weight=1)
        for row in range(1, self.rows + 1):
            self.frame.rowconfigure(row, weight=1)

        # Update the table every 3 seconds
        self.root.after(3000, self.update_table)

        self.latest_mosquitto_data = "0"
        self.init_mqtt_client()
        self.previous_mosquitto_data = "0"
        self.init_mysql_connection()


    def play_mp3(self, mp3_path):
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()

    def populate_table(self):
        for col, title in enumerate(self.titles):
            label = tk.Label(self.frame, text=title)
            label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

        for row in range(1, self.rows + 1):
            for col in range(self.cols):
                if col == 0:
                    values = ["(1,1)", "(2,1)", "(3,1)", "(4,1)", "(1,2)", "(2,2)", "(3,2)", "(4,2)",
                              "(1,3)", "(2,3)", "(3,3)", "(4,3)"]
                    value = values[row - 1]
                elif col == 1:
                    value = "0"
                else:
                    value = ""
                entry = tk.Entry(self.frame, justify="center")
                entry.insert(0, value)
                entry.config(state="readonly")
                entry.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

                if row == 1:
                    entry.config(fg='red')
        for row in range(1, self.rows + 1):
            self.row_last_time[row] = time.time()

    def init_mqtt_client(self):
        def on_message(client, userdata, message):
            self.latest_mosquitto_data = message.payload.decode()
            arriving_value_widget = self.frame.grid_slaves(row=1, column=3)[0]
            arriving_value_widget.config(state="normal")
            arriving_value_widget.delete(0, "end")
            arriving_value_widget.insert(0, message.payload.decode())
            arriving_value_widget.config(state="readonly")

        self.client = mqtt.Client()
        self.client.on_message = on_message
        mqtt_broker_host = "172.16.1.166"
        self.client.connect(mqtt_broker_host, 1883, 60)
        topic = "predict"
        self.client.subscribe(topic)
        self.client.loop_start()

    def init_mysql_connection(self):
        self.mydb = mysql.connector.connect(
            host="localhost",  # replace with your MySQL host
            port=3306,
            user="jcl",  # replace with your MySQL username
            password="",  # replace with your MySQL password
            database="mosquitto"  # replace with your MySQL database name
        )
        self.mycursor = self.mydb.cursor()

    def save_to_mysql(self, host, topic, message):
        sql = "INSERT INTO mosquitto_data (host, topic, message) VALUES (%s, %s, %s)"
        val = (host, topic, message)
        self.mycursor.execute(sql, val)
        self.mydb.commit()
    def publish_to_mosquitto(self):
        host = "172.16.1.166"
        topic = "location"
        message = "1_1"
        cmd = [
            "mosquitto_pub",
            "-h", host,
            "-t", topic,
            "-m", message
        ]
        try:
            subprocess.run(cmd, check=True)
            print("Published successfully: 1_1")
            # Save the published message to MySQL
            self.save_to_mysql(host, topic, message)
        except subprocess.CalledProcessError as e:
            print(f"Publish failed: {e}")

    def update_table(self):
        print("Updating table...")
        for row in range(1, self.rows + 1):
            current_time = time.time()
            elapsed_time = current_time - self.row_last_time[row]
            if row == 1:
                arriving_value = int(self.latest_mosquitto_data)
            else:
                arriving_value = random.choice([0, 1])

            current_value_widget = self.frame.grid_slaves(row=row, column=1)[0]
            arriving_value_widget = self.frame.grid_slaves(row=row, column=3)[0]
            lasting_time_widget = self.frame.grid_slaves(row=row, column=2)[0]
            next_operation_widget = self.frame.grid_slaves(row=row, column=4)[0]

            try:
                current_value = int(current_value_widget.get())
            except ValueError:
                current_value = 0

            try:
                lasting_time = float(lasting_time_widget.get())
            except ValueError:
                lasting_time = 0

            if row == 1 and arriving_value == self.previous_mosquitto_data:
                lasting_time += elapsed_time

            arriving_value_widget.config(state="normal")
            arriving_value_widget.delete(0, "end")
            arriving_value_widget.insert(0, str(arriving_value))
            arriving_value_widget.config(state="readonly")

            if arriving_value == current_value:
                next_operation_widget.config(state="normal")
                next_operation_widget.delete(0, "end")
                next_operation_widget.insert(0, "to filter")
                next_operation_widget.config(state="readonly")

                lasting_time += elapsed_time
            else:
                if arriving_value == 0:
                    next_operation = "to change current value"
                else:
                    next_operation = "to change and publish"
                    if row == 1:
                        self.publish_to_mosquitto()

                current_value_widget.config(state="normal")
                current_value_widget.delete(0, "end")
                current_value_widget.insert(0, str(arriving_value))
                current_value_widget.config(state="readonly")

                next_operation_widget.config(state="normal")
                next_operation_widget.delete(0, "end")
                next_operation_widget.insert(0, next_operation)
                next_operation_widget.config(state="readonly")

                lasting_time = 0

            lasting_time_widget.config(state="normal")
            lasting_time_widget.delete(0, "end")
            lasting_time_widget.insert(0, "{:.1f}".format(lasting_time))
            lasting_time_widget.config(state="readonly")

            self.row_last_time[row] = current_time

            if row == 1:
                if current_value == 0 and arriving_value == 1:
                    self.play_mp3("/Users/jichanglong/Desktop/voice/appear.mp3")
                elif current_value == 1 and arriving_value == 0:
                    self.play_mp3("/Users/jichanglong/Desktop/voice/clean.mp3")

        self.last_time = current_time
        self.root.after(1000, self.update_table)


root = tk.Tk()
window_width = 850
window_height = 500
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = screen_width - window_width - 100
y = 30
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
app = TableApp(root)
root.mainloop()
