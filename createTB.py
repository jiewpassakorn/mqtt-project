import mysql.connector

import os
from dotenv import load_dotenv
load_dotenv()
USER = os.getenv('USER')
DB_NAME = os.getenv('DB_NAME')
PASSWORD = os.getenv('PASSWORD')
TABLE_NAME = os.getenv('TABLE_NAME')


def create_db():
    mydb = mysql.connector.connect(
        host="localhost",
        user=USER,
        password=PASSWORD)

    mycursor = mydb.cursor()
    mycursor.execute(f"CREATE DATABASE `{DB_NAME}`")


def add_table():
    mydb = mysql.connector.connect(
        host="localhost",
        user=USER,
        password=PASSWORD,
        database= DB_NAME)
    mycursor = mydb.cursor()
    mycursor.execute(
        f"CREATE TABLE `{TABLE_NAME}` (ip_address TEXT, time TIMESTAMP, humidity FLOAT, temperature FLOAT, thermal_array MEDIUMTEXT)")


if __name__ == '__main__':
    create_db()
    add_table()
