from flask import Flask, render_template
app = Flask(__name__)

import sqlite3
import RPi.GPIO as GPIO
import dht11
import datetime
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

#database connection object
conn = sqlite3.connect('databasetest.db')
#cursor object
cursobj = conn.cursor()

#Til at lave vores table
table = """ CREATE TABLE IF NOT EXISTS "DHT11TESTTABLE"(
    ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    TAG TEXT,
    DATETIME TEXT,
    TEMPERATURE REAL,
    HUMIDITY REAL);
    """

#DHT11 sensor pin object
reader = dht11.DHT11(pin = 4)

#Funktion til at tage Fughtihed & Temperatur måling med DHT11
def getDHTdata():
    result = reader.read()
    if result.is_valid():
        print("Temperature: %-3.1f C" % result.temperature)
        print("Humidity: %3.1f %%" % result.humidity)
        return result.temperature, result.humidity
    else:
        print("Error: %d" % result.error_code)

#funktion til at lave vores table
def makeDesk():
    try:
        cursobj.execute(table)
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Could not create table! {e}')


#Til at injecte data ind i vores SQLite database
#'Tag' argumentet, hvis man laver en streng i den skal man skrive anførsels tegn rundt om ""
def insertData(tag):
    try:
        query ='INSERT INTO DHT11TESTTABLE (TAG, DATETIME, TEMPERATURE, HUMIDITY)VALUES(?,?,?,?)'
        temp, hum = getDHTdata()
        print("1")
        sleep(1)
        print("2")
        #tag1 = str(tag)
        data = (tag, datetime.datetime.now(), temp, hum)
        print(f"Inserting data: {data}")
        cursobj.execute(query, data)
        rowid = cursobj.lastrowid
        print(f'id of last row id = {rowid}')
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Could not insert! {e}')
    #finally:
#conn.close()

#få data ud af databasen igen
def takeOut():
    try:
        cursobj.execute("SELECT * FROM DHT11TESTTABLE ORDER BY id DESC LIMIT 1")
        result = cursobj.fetchone()
        print(result, type(result))
        return result
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Could not take out! {e}')

makeDesk()

insertData("temp")
sleep(2)
SQLdata = takeOut()
print(type(SQLdata), SQLdata)
tag = SQLdata[1]
dateTemp = SQLdata[2]
date = dateTemp[0:21]
temperature = SQLdata[3]
humi = SQLdata[4]
print(type(tag), tag, type(date), date, type(temperature), temperature, type(humi), humi)

@app.route('/')
def home():
   return render_template('home.html')
if __name__ == '__main__':
   app.run()
