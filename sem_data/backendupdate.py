import sqlite3
import requests
import mysql.connector
from datetime import datetime, timedelta
from global_var import *

def get_db_connection():
    global conn, cursor, conn2, cursor2
    try:
        if not conn:
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
        #if not conn2:
        #    conn2 = mysql.connector.connect(**config_sql)
        #    cursor2 = conn2.cursor()
    except Exception as e:
        print(f"Error establishing database connection: {e}")
        # If there's an error, set connections to None and retry in the next call
        conn, cursor =  None, None
        conn2, cursor2 = None, None
    return conn, cursor, conn2, cursor2

def get_db_connection2(pu_conn, pu_cursor):
    try:
        if not pu_conn:
            pu_conn = sqlite3.connect('data.db')
            pu_cursor = pu_conn.cursor()
    except Exception as e:
        print(f"Error establishing database connection: {e}")
        # If there's an error, set connections to None and retry in the next call
        pu_conn, pu_cursor =  None, None

    return pu_conn, pu_cursor
def filter_outliers(conn, cursor):

    if conn == None or cursor == None:
        conn, cursor, conn2, cursor2 = get_db_connection()

    cursor.execute("SELECT id, temperature, humidity, date, time FROM data ORDER BY date, time")
    records = cursor.fetchall()

    # Preprocess the records to convert temperature and humidity to float values
    processed_records = []
    for record in records:
        id_, temp, humidity, date, time = record
        temp = float(temp.replace('°C', '').strip())
        humidity = float(humidity.replace('%', '').strip())
        processed_records.append((id_, temp, humidity, date, time))

    outliers = []

    for i in range(len(processed_records)):
        current_id, current_temp, current_humidity, current_date, current_time = processed_records[i]
        current_datetime = datetime.strptime(f"{current_date} {current_time}", '%Y-%m-%d %H:%M:%S')

        # For the first record
        if i == 0:
            next_id, next_temp, next_humidity, next_date, next_time = processed_records[i + 1]
            next_datetime = datetime.strptime(f"{next_date} {next_time}", '%Y-%m-%d %H:%M:%S')
            ref_temp, ref_humidity, ref_datetime = next_temp, next_humidity, next_datetime

        # For the last record
        elif i == len(processed_records) - 1:
            prev_id, prev_temp, prev_humidity, prev_date, prev_time = processed_records[i - 1]
            prev_datetime = datetime.strptime(f"{prev_date} {prev_time}", '%Y-%m-%d %H:%M:%S')
            ref_temp, ref_humidity, ref_datetime = prev_temp, prev_humidity, prev_datetime

        # For records in between
        else:
            prev_id, prev_temp, prev_humidity, prev_date, prev_time = processed_records[i - 1]
            next_id, next_temp, next_humidity, next_date, next_time = processed_records[i + 1]
            prev_datetime = datetime.strptime(f"{prev_date} {prev_time}", '%Y-%m-%d %H:%M:%S')
            next_datetime = datetime.strptime(f"{next_date} {next_time}", '%Y-%m-%d %H:%M:%S')

            # Determine which record (previous or next) is closer in time to the current record
            if abs(current_datetime - prev_datetime) < abs(current_datetime - next_datetime):
                ref_temp, ref_humidity, ref_datetime = prev_temp, prev_humidity, prev_datetime
            else:
                ref_temp, ref_humidity, ref_datetime = next_temp, next_humidity, next_datetime

        # If the time difference with the reference record is greater than 15 minutes, skip
        if abs((current_datetime - ref_datetime).total_seconds()) > 15 * 60:
            continue

        if abs(current_temp - ref_temp) > 5:
            outliers.append(current_id)

        if abs(current_humidity - ref_humidity) > 10:
            outliers.append(current_id)

    for outlier_id in set(outliers):
        cursor.execute("DELETE FROM data WHERE id=?", (outlier_id,))

    conn.commit()

def filter_outliers2():
    global conn2, cursor2
    if  conn2 == None or cursor2 == None:
        conn, cursor, conn2, cursor2 = get_db_connection()

    cursor2.execute("SELECT id, temperature, humidity, date, time FROM data ORDER BY date, time")
    records = cursor2.fetchall()

    # Preprocess the records to convert temperature and humidity to float values
    processed_records = []
    for record in records:
        id_, temp, humidity, date, time = record
        temp = float(temp.replace('°C', '').strip())
        humidity = float(humidity.replace('%', '').strip())
        processed_records.append((id_, temp, humidity, date, time))

    outliers = []

    for i in range(len(processed_records)):
        current_id, current_temp, current_humidity, current_date, current_time = processed_records[i]
        current_datetime = datetime.strptime(f"{current_date} {current_time}", '%Y-%m-%d %H:%M:%S')

        # For the first record
        if i == 0:
            next_id, next_temp, next_humidity, next_date, next_time = processed_records[i + 1]
            next_datetime = datetime.strptime(f"{next_date} {next_time}", '%Y-%m-%d %H:%M:%S')
            ref_temp, ref_humidity, ref_datetime = next_temp, next_humidity, next_datetime

        # For the last record
        elif i == len(processed_records) - 1:
            prev_id, prev_temp, prev_humidity, prev_date, prev_time = processed_records[i - 1]
            prev_datetime = datetime.strptime(f"{prev_date} {prev_time}", '%Y-%m-%d %H:%M:%S')
            ref_temp, ref_humidity, ref_datetime = prev_temp, prev_humidity, prev_datetime

        # For records in between
        else:
            prev_id, prev_temp, prev_humidity, prev_date, prev_time = processed_records[i - 1]
            next_id, next_temp, next_humidity, next_date, next_time = processed_records[i + 1]
            prev_datetime = datetime.strptime(f"{prev_date} {prev_time}", '%Y-%m-%d %H:%M:%S')
            next_datetime = datetime.strptime(f"{next_date} {next_time}", '%Y-%m-%d %H:%M:%S')

            # Determine which record (previous or next) is closer in time to the current record
            if abs(current_datetime - prev_datetime) < abs(current_datetime - next_datetime):
                ref_temp, ref_humidity, ref_datetime = prev_temp, prev_humidity, prev_datetime
            else:
                ref_temp, ref_humidity, ref_datetime = next_temp, next_humidity, next_datetime

        # If the time difference with the reference record is greater than 15 minutes, skip
        if abs((current_datetime - ref_datetime).total_seconds()) > 15 * 60:
            continue

        if abs(current_temp - ref_temp) > 5:
            outliers.append(current_id)

        if abs(current_humidity - ref_humidity) > 10:
            outliers.append(current_id)

    for outlier_id in set(outliers):
        cursor2.execute("DELETE FROM data WHERE id=?", (outlier_id,))

    conn2.commit()

def send_db_to_server():
    with open("data.db", "rb") as f:
        response = requests.post(
            "https://shahinvi.pythonanywhere.com/upload",
            files={"file": f},
            headers={"password": SECRET_PASSWORD}
        )
    print(response.text)