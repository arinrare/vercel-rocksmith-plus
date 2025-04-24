import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DATABASE_URL'),
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USERNAME'),
            password='ccg5!45x$Rt5z!7y',
            port=os.getenv('DATABASE_PORT'),
            charset='utf8mb4'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None