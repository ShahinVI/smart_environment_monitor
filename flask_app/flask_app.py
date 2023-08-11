
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime, timedelta
from decouple import config

SECRET_PASSWORD = config('SECRET_PASSWORD')


app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_db():
    password = request.headers.get("password")
    if password != SECRET_PASSWORD:
        return jsonify({"error": "Invalid authentication"}), 403

    file = request.files['file']
    file.save("/home/shahinvi/mysite/data.db")
    return jsonify({"success": True})



def get_metrics_for_day(target_date):
    conn = sqlite3.connect('/home/shahinvi/mysite/data.db')
    cursor = conn.cursor()

    # Current temperature
    cursor.execute("SELECT temperature, humidity FROM data WHERE date = ? ORDER BY time DESC LIMIT 1", (target_date,))
    current_temp, current_humidity = cursor.fetchone()

    # Average temperature and humidity
    cursor.execute("SELECT AVG(temperature), AVG(humidity) FROM data WHERE date = ?", (target_date,))
    avg_temp, avg_humidity = [round(value, 2) for value in cursor.fetchone()]

    # Highest and lowest temperature
    cursor.execute("SELECT MAX(temperature), MIN(temperature) FROM data WHERE date = ?", (target_date,))
    highest_temp, lowest_temp = cursor.fetchone()

    # Highest and lowest humidity
    cursor.execute("SELECT MAX(humidity), MIN(humidity) FROM data WHERE date = ?", (target_date,))
    highest_humidity, lowest_humidity = cursor.fetchone()

    conn.close()

    # Return the metrics
    return {
        "current_temp": current_temp,
        "avg_temp": avg_temp,
        "highest_temp": highest_temp,
        "lowest_temp": lowest_temp,
        "current_humidity": current_humidity,
        "avg_humidity": avg_humidity,
        "highest_humidity": highest_humidity,
        "lowest_humidity": lowest_humidity,
        "date":target_date
    }

@app.route('/')
def display_metrics():
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    today_metrics = get_metrics_for_day(today)
    yesterday_metrics = get_metrics_for_day(yesterday)

    return render_template('metrics.html', today_metrics=today_metrics, yesterday_metrics=yesterday_metrics)

