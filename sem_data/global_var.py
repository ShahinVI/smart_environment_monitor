from decouple import config

YOUR_PASSWORD = config('YOUR_PASSWORD')
# Configuration for the PythonAnywhere MySQL database
SECRET_PASSWORD = config('SECRET_PASSWORD')
# Configuration for the PythonAnywhere MySQL database
config_sql= {
    'user': 'shahinvi',
    'password': YOUR_PASSWORD,  # Replace with your actual password
    'host': 'shahinvi.mysql.pythonanywhere-services.com',
    'database': 'shahinvi$default',
    'raise_on_warnings': True
}
# Global database connections
conn = None
cursor = None
conn2 = None
cursor2 = None
# Counter for rate limiting
message_counter = 0
SEND_THRESHOLD = 180  # Send data every 180 messages, adjust as needed 900 seconds