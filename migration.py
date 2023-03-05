import mysql.connector
import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()
USER = os.getenv('USER')
DB_NAME = os.getenv('DB_NAME')
PASSWORD = os.getenv('PASSWORD')
TABLE_NAME = os.getenv('TABLE_NAME')

# function to create database
def create_db():
    # connect to MySQL server with given credentials
    mydb = mysql.connector.connect(
        host="localhost",
        user=USER,
        password=PASSWORD)

    # create a cursor object to execute SQL commands
    mycursor = mydb.cursor()

    # execute SQL command to create a new database with given name
    mycursor.execute(f"CREATE DATABASE `{DB_NAME}`")

# function to create table within the database
def add_table():
    # connect to MySQL server with given credentials and database name
    mydb = mysql.connector.connect(
        host="localhost",
        user=USER,
        password=PASSWORD,
        database=DB_NAME)

    # create a cursor object to execute SQL commands
    mycursor = mydb.cursor()

    # execute SQL command to create a new table with given name and columns
    mycursor.execute(
        f"CREATE TABLE `{TABLE_NAME}` (sensor_name TEXT, received_time TIMESTAMP, time TIMESTAMP, humidity FLOAT, temperature FLOAT, thermal_array MEDIUMTEXT )")

# main function to call create_db() and add_table() functions
if __name__ == '__main__':
    create_db()
    add_table()