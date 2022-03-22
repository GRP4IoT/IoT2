from pyLoraRFM9x import LoRa, ModemConfig
# from https://github.com/epeters13/pyLoraRFM9x
import threading
import sqlite3
import datetime
from time import sleep
from flask import Flask, render_template

app = Flask(__name__)
saveToDB = False

#Database connection object
conn = sqlite3.connect('Desktop/LoneLora/databasen.db')
#cursor object
curs = conn.cursor()

#Lave vores table i databasen
table = """ CREATE TABLE IF NOT EXISTS IOTINFOEN(
    ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    TAG TEXT,
    DATETIME TEXT,
    TEMPERATURE REAL,
    HUMIDITY REAL, 
    LATITUDE FLOAT,
    LONGITUDE FLOAT);
"""

tal = 0

def tableCreation():
    try:
        curs.execute(table)
        print("IOTINFOEN table created or found")
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Could not create table! {e}')

if tal == 0:
    tableCreation()
    tal = 1

#Injecte SQL data i databasen
def insertData(tag, temp, hum, lat, lon):
    try:
        query = "INSERT INTO IOTINFOEN (TAG, DATETIME, TEMPERATURE, HUMIDITY, LATITUDE, LONGITUDE)VALUES(?,?,?,?,?,?)"
        dato = str(datetime.datetime.now())
        dato = dato[0:19]
        data = (tag, dato, temp, hum, lat, lon)
        print(f'inserting data: {data}')
        curs.execute(query, data)
        rowid = curs.lastrowid
        print(f'id of last row id = {rowid}')
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Could not insert! {e}')
        

# This is our callback function that runs when a message is received
def on_recv(payload):
    global ourInts
    global ourFloats
    global saveToDB
    print("From:", payload.header_from)
    #print("Received:", payload.message)
    print("RSSI: {}; SNR: {}".format(payload.rssi, payload.snr))
    mess = payload.message
    #print(mess,"hej fra veriable")
    mess = str(mess)
    slice = mess[3:9]
    slice2 = mess[12:32]
    #print("slice 2", slice2)
    #print(slice)
    Split = slice.split(', ')
    Split2 = slice2.split("', '")
    #print(type(Split), Split)
    #print(type(Split2), Split2)
    ourInts = [int(x) for x in Split]
    ourFloats = [float(x) for x in Split2]
    print(type(ourInts[0]), ourInts[0], type(ourInts[1]), ourInts[1], type(ourFloats[0]), ourFloats[0], type(ourFloats[1]), ourFloats[1])
    saveToDB = True
    print(saveToDB)
    return ourInts, ourFloats, saveToDB

# Use chip select 1. GPIO pin 5 will be used for interrupts and set reset pin to 25
# The address of this device will be set to 222
lora = LoRa(1, 17, 222, reset_pin = 25, freq=868, modem_config=ModemConfig.Bw125Cr45Sf128, tx_power=14, acks=True)
lora.on_recv = on_recv

message = "Hello there!"
status = lora.send_to_wait(message, 1, retries=20)
if status is True:
    print("Message sent!")
else:
    print("No acknowledgment from recipient")

@app.route('/')
def home():
   return render_template('home.html')
if __name__ == '__main__':
   thread = threading.Thread(target=app.run, args=())
   thread.start()

print("flask has started")

while True:
    if saveToDB == True:
        try:
            print("Trying to save to databse")
            insertData("device1", ourInts[0], ourInts[1], ourFloats[0], ourFloats[1])
            saveToDB = False
            print(saveToDB)
        except:
            print("Couldn't insert data in SQL")
            saveToDB = False
            print(saveToDB)

# Send a message to a recipient device with address 10
# Retry sending the message twice if we don't get an acknowledgment from the recipient
"""    message = "Hello there!"
    status = lora.send_to_wait(message, 1, retries=20)
    if status is True:
        print("Message sent!")
    else:
        print("No acknowledgment from recipient")
    if status is False:
        print("No acknowledgment from recipient")
    
    try:
        print("Our temp and hum readings from ESP: ", ourInts)
        print("Our GPS readings, lat-lon", ourFloats)
        insertData("device1", ourInts[0], ourInts[1], ourFloats[0], ourFloats[1])
        sleep(11) #en sleep for at prøve at stoppe os fra at ligge den samme entry ind flere gange
    except:
        print("didn't work")"""
