import paho.mqtt.client as mqtt
import sqlite3
import mysql.connector
from datetime import datetime
from backendupdate import filter_outliers, filter_outliers2, send_db_to_server, get_db_connection, get_db_connection2
from global_var import *
import threading


def create_db():
    # Connect to the database (it will create the file if it does not exist)
    global conn, cursor, conn2, cursor2
    if conn == None or cursor == None or conn2 == None or cursor2 == None:
        print("what the hell")
        conn, cursor, conn2, cursor2 = get_db_connection()

    # Create the table with separate date and time columns
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature TEXT,
        humidity TEXT,
        date TEXT,
        time TEXT
    )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS average_metric (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature_ave TEXT,
            humidity_ave TEXT,
            date TEXT
        )
        ''')

    # Commit the changes and close the connection
    conn.commit()

    #Create the table with separate date and time columns
    #cursor2.execute('''
    #CREATE TABLE IF NOT EXISTS data (
    #    id INT AUTO_INCREMENT PRIMARY KEY,
    #    temperature VARCHAR(255),
    #    humidity VARCHAR(255),
    #    date DATE,
    #    time TIME
    #)
    #''')
    #cursor2.execute('''
    #CREATE TABLE IF NOT EXISTS average_metric (
    #    id INT AUTO_INCREMENT PRIMARY KEY,
    #    temperature_ave VARCHAR(255),
    #    humidity_ave VARCHAR(255),
    #    date DATE
    #)
    #''')
#
    ## Commit the changes and close the connection
    #conn2.commit()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("/topic/esp32/sensor_data")
def on_message(client, userdata, msg):
    global message_counter
    global conn, cursor, conn2, cursor2
    try:
        # Parse the received message
        data = msg.payload.decode()
        temp = data.split(",")[0].split(":")[1].strip()
        humidity = data.split(",")[1].split(":")[1].strip()

        # Get the current date and time separately
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')

        if conn == None or cursor == None:# or conn2 == None or cursor2 == None:
            conn, cursor, conn2, cursor2 = get_db_connection()

        # Insert data with separate date and time
        cursor.execute("INSERT INTO data (temperature, humidity, date, time) VALUES (?, ?, ?, ?)",
                       (temp, humidity, current_date, current_time))
        #cursor2.execute("INSERT INTO data (temperature, humidity, date, time) VALUES (?, ?, ?, ?)",(temp, humidity, current_date, current_time))

        # Calculate the average temperature and humidity for the current day
        cursor.execute("SELECT AVG(temperature), AVG(humidity) FROM data WHERE date = ?", (current_date,))
        #cursor2.execute("SELECT AVG(temperature), AVG(humidity) FROM data WHERE date = ?", (current_date,))

        avg_temp, avg_humidity = cursor.fetchone()

        # Check if an entry for the current day already exists in the average_metric table
        cursor.execute("SELECT id FROM average_metric WHERE date = ?", (current_date,))
        #cursor2.execute("SELECT id FROM average_metric WHERE date = ?", (current_date,))
        entry = cursor.fetchone()

        if entry is None:
            # Insert a new row with the averages
            cursor.execute("INSERT INTO average_metric (temperature_ave, humidity_ave, date) VALUES (?, ?, ?)",
                           (avg_temp, avg_humidity, current_date))
            #cursor2.execute("INSERT INTO average_metric (temperature_ave, humidity_ave, date) VALUES (?, ?, ?)",(avg_temp, avg_humidity, current_date))
        else:
            # Update the existing row with the new averages
            cursor.execute("UPDATE average_metric SET temperature_ave = ?, humidity_ave = ? WHERE date = ?",
                           (avg_temp, avg_humidity, current_date))
            #cursor2.execute("UPDATE average_metric SET temperature_ave = ?, humidity_ave = ? WHERE date = ?",(avg_temp, avg_humidity, current_date))

        try:
            conn.commit()
            #conn2.commit()
        except Exception as db_err:
            print(f"Database error: {db_err}")
            # Optionally, reconnect to the database if there's an error
            if conn == None or cursor == None:# or conn2 == None or cursor2 == None:
                conn, cursor, conn2, cursor2 = get_db_connection()


        print(f"Date: {current_date}, Time: {current_time}, Temperature: {temp}, Humidity: {humidity}")

        message_counter += 1
        if message_counter >= SEND_THRESHOLD:
            filter_outliers(conn,cursor)
            #filter_outliers2()
            send_db_to_server()
            message_counter = 0  # Reset counter

    except Exception as e:
        print(f"Error processing message: {e}")

def periodic_upload():
    try:
        pu_conn, pu_cursor = None,None
        pu_conn, pu_cursor = get_db_connection2(pu_conn, pu_cursor)
        filter_outliers(pu_conn, pu_cursor)
        #filter_outliers2()
        send_db_to_server()
        pu_conn.close()
    except Exception as e:
        print(f"Error during periodic upload: {e}")
    finally:
        # Schedule the next upload after 15 minutes
        threading.Timer(15*60, periodic_upload).start()

create_db()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.102", 1883, 60)  # Default port for MQTT is 1883
periodic_upload()
client.loop_forever()