import tkinter as tk
from tkinter import ttk
import mysql.connector
import time


class MosquittoDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mosquitto Data Viewer")

        # Set up treeview to display data
        self.tree = ttk.Treeview(self.root, columns=("Timestamp", "Host", "Topic", "Message"), show="headings")
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("Host", text="Host")
        self.tree.heading("Topic", text="Topic")
        self.tree.heading("Message", text="Message")
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Load data and update every 3 seconds
        self.update_data()

    def init_mysql_connection(self):
        mydb = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="jcl",
            password="",
            database="mosquitto"
        )
        return mydb

    def load_data(self):
        # Clear existing data
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Fetch data from database
        mydb = self.init_mysql_connection()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT timestamp, host, topic, message FROM mosquitto_data")
        rows = mycursor.fetchall()

        for row in rows:
            self.tree.insert("", "end", values=row)

        # Close the connection
        mycursor.close()
        mydb.close()

    def update_data(self):
        self.load_data()
        self.root.after(3000, self.update_data)  # Refresh every 3 seconds


root = tk.Tk()
root.geometry("800x400")
app = MosquittoDataApp(root)
root.mainloop()
