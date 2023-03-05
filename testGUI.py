import mysql.connector
import tkinter as tk
from tkinter import *
from tkinter import ttk


# Connect to the database
conn = mysql.connector.connect(host = "localhost",user = "root", passwd = "stank5843"
                               , database = "MQTT_PROJECT")

c = conn.cursor()

# Fetch data from the database
c.execute("SELECT * FROM sensor_data")
data = c.fetchall()

# Create a GUI window
root = tk.Tk()
root.title('Sensor Data Table')
root.geometry("1000x800")
root.state('zoomed')

# Create a table widget
columns = ('IP', 'Time', 'Humidity', 'Temperature', 'Thermal Array')
tree = ttk.Treeview(root, columns=columns, show='headings', height= 25)

# Create frame
f1 = Frame(root)
f1.pack(pady=20)

#Name label
nameLabel = tk.Label(f1, text="MQTT Project", font= 40)

#tree.column("id",anchor=CENTER, width=40)
tree.column("IP",anchor=CENTER,width=80)
tree.column("Time",anchor=CENTER,width=150)
tree.column("Humidity",anchor=CENTER,width=80)
tree.column("Temperature",anchor=CENTER,width=80)
tree.column("Thermal Array",anchor=CENTER,width=1200)

#Define Column Heading

#tree.heading("id",text="Id",anchor=CENTER)
tree.heading("IP",text="IP Address",anchor=CENTER)
tree.heading("Time",text="Time",anchor=CENTER)
tree.heading("Humidity",text="Humidity",anchor=CENTER)
tree.heading("Temperature",text="Temperature",anchor=CENTER)
tree.heading("Thermal Array",text="Thermal Array",anchor=CENTER)

# Populate the table with data
for row in data:
    tree.insert('', 'end', values=row)
    
search_label = tk.Label(f1, text="Search:")
search_entry = tk.Entry(f1)
search_button = tk.Button(f1, text="Filter")

# Define the callback function for the search button
def on_search_button_click():
    search_term = search_entry.get()

    # Clear the table
    tree.delete(*tree.get_children())

    # Retrieve the matching rows from the database
    query = f"SELECT * FROM sensor_data WHERE ip_address LIKE '%{search_term}%' "
    c.execute(query)
    rows = c.fetchall()

    # Populate the table with the matching rows
    for row in rows:
        tree.insert("", tk.END, text=row[0], values=(row[0], row[1], row[2], row[3], row[4] ))

# Bind the callback function to the search button
search_button.config(command=on_search_button_click)

# Pack the GUI elements
nameLabel.grid(row=0, column= 1, pady= 10)
search_label.grid(row=1, column=0)
search_entry.grid(row=1, column=1)
search_button.grid(row=1, column=2, padx= 30)
tree.pack()

# Start the GUI event loop
root.mainloop()

# Close the database connection
conn.close()