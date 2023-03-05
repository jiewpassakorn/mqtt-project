import mysql.connector

USER = "root"
DB_NAME = "test4"
PASSWORD = ""

TABLE_NAME = "sensor_data"


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
        f"CREATE TABLE `{TABLE_NAME}` (time TIMESTAMP, humidity FLOAT, temperature FLOAT, thermal_array MEDIUMTEXT)")


if __name__ == '__main__':
    create_db()
    add_table()
