import mysql.connector
from config.db_config import DB_CONFIG  # Importing from the root config.py

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None
    
# TO run this file run this command: python -m db.connection