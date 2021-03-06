from tokenize import _all_string_prefixes
from pyLoraRFM9x import LoRa, ModemConfig
# from https://github.com/epeters13/pyLoraRFM9x
import threading
import sqlite3
import datetime
from time import sleep
from flask import Flask, render_template
import base64
from io import BytesIO
from matplotlib.figure import Figure

app = Flask(__name__)
saveToDB = False

#Database connection object
conn = sqlite3.connect('Desktop/LoneLora/databasen.db', check_same_thread=False)
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
        conn = sqlite3.connect('Desktop/LoneLora/databasen.db', check_same_thread=False)
        curs = conn.cursor()
        curs.execute(table)
        print("IOTINFOEN table created or found")
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Could not create table! {e}')
    finally:
        conn.close()

if tal == 0:
    tableCreation()
    tal = 1

#Injecte SQL data i databasen
def insertData(tag, temp, hum, lat, lon):
    try:
        conn = sqlite3.connect('Desktop/LoneLora/databasen.db', check_same_thread=False)
        curs = conn.cursor()
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
    finally:
        conn.close()

#Tager de sidste 5 entries ud af SQLite i descending order
def getData():
    try:
        conn = sqlite3.connect('Desktop/LoneLora/databasen.db', check_same_thread=False)
        curs = conn.cursor()
        curs.execute('SELECT * FROM IOTINFOEN ORDER BY ID DESC LIMIT 5;')
        ourData = curs.fetchall()
        return ourData
    except sqlite3.Error as e:
        print(f'Error calling SQL: "{e}"')
    finally:
        conn.close()

#Tag alt data ud af SQLite databasen
def alData():
    try:
        conn = sqlite3.connect('Desktop/LoneLora/databasen.db', check_same_thread=False)
        curs = conn.cursor()
        curs.execute('SELECT * FROM IOTINFOEN;')
        allData = curs.fetchall()
        return allData
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Could not retrieve data! {e}')
    finally:
        conn.close()

#Lave koordinat systemer med matplot til at vise vores data
def matPlots():
    date = []
    fugt = []
    temp = []
    vorData = alData() #Data udtr??kning og valg a den data vi vil have
    for i in vorData:
        i[2].append(date)
    for j in vorData:
        j[3].append(temp)
    for u in vorData:
        u[4].append(fugt)
    #matplotting
    fig = Figure()
    ax = fig.subplots()
    buf = BytesIO()
    ax.plot(date, temp)
    fig.savefig(buf, format="png")
    data = base64.b64decode(buf.getbuffer()).decode("ascii")
    aPlot = f"<img src ='data:image/png;base64,{data}'/>"
    
    ax.plot(date, fugt)
    data1 = base64.b64decode(buf.getbuffer()).decode("ascii")
    bPlot = f"<img src ='data:image/png;base64,{data1}'/>"
    return aPlot, bPlot

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

# Send a message to a recipient device with address 10
# Retry sending the message twice if we don't get an acknowledgment from the recipient
message = "Hello there!"
status = lora.send_to_wait(message, 1, retries=20)
if status is True:
    print("Message sent!")
else:
    print("No acknowledgment from recipient")

@app.route('/')
def home():
    rowData = getData()
    aPlot, bPlot = matPlots()
    print(rowData, "fra hjemmeside")
    print(rowData[0][0], "fra hjemmeside")
    return render_template('home.html', rowData=rowData, aPlot=aPlot, bPlot=bPlot)

if __name__ == '__main__':
   thread = threading.Thread(target=app.run, args=())
   thread.start()

print("flask has started")

while True:
    if saveToDB == True:
        try:
            print("Trying to save to database")
            insertData("device1", ourInts[0], ourInts[1], ourFloats[0], ourFloats[1])
            print(saveToDB)
            data = getData()
            print(data)
            saveToDB = False
        except:
            print("Couldn't insert data in SQL")
            saveToDB = False
            print(saveToDB)
