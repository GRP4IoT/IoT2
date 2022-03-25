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
conn = sqlite3.connect('/home/pi/Desktop/LoneLora/databasen.db', check_same_thread=False)
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
        conn = sqlite3.connect('/home/pi/Desktop/LoneLora/databasen.db', check_same_thread=False)
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
        conn = sqlite3.connect('/home/pi/Desktop/LoneLora/databasen.db', check_same_thread=False)
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
        conn = sqlite3.connect('/home/pi/Desktop/LoneLora/databasen.db', check_same_thread=False)
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
        conn = sqlite3.connect('/home/pi/Desktop/LoneLora/databasen.db', check_same_thread=False)
        curs = conn.cursor()
        curs.execute("""SELECT * FROM (
            SELECT * FROM IOTINFOEN ORDER BY ID DESC LIMIT 12)
            ORDER BY ID ASC;""")
        allData = curs.fetchall()
        print(allData)
        return allData
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Could not retrieve data! {e}')
    finally:
        conn.close()

#Lave koordinat systemer med matplot til at vise vores data
def matPlotsTemp():
    altData = alData()
    dates = []
    temps = []
    hums = []
    for i in altData:
        dates.append(i[2])
        temps.append(i[3])
        hums.append(i[4])
    x = dates
    y = temps
    z = hums
    #matplotting
    fig = Figure()
    ax = fig.subplots()
    #fig.subplots_adjust(bottom=0.3)
    ax.tick_params(axis='x', which="both", rotation=30)
    ax = fig.subplots()
    ax.set_facecolor("#fff") # inner plot background color HTML white
    fig.patch.set_facecolor('#fff') # outer plot background color HTML white
    ax.plot(x, y, linestyle = 'dashed', c = '#11f', linewidth = '1.5',
    marker = 'o', mec = 'hotpink', ms = 10, mfc = 'hotpink' )
    ax.plot(x, z, linestyle = 'dashed', c= '#11f', linewidth = '1.5',
    marker = 'o', mec = 'black', ms = 10, mfc = 'black')
    ax.set_xlabel('Dato & tid')
    ax.set_ylabel('Temperatur')
    ax.xaxis.label.set_color('hotpink') #setting up X-axis label color to hotpink
    ax.yaxis.label.set_color('hotpink') #setting up Y-axis label color to hotpink
    ax.tick_params(axis='x', colors='black') #setting up X-axis tick color to black
    ax.tick_params(axis='y', colors='black') #setting up Y-axis tick color to black
    ax.spines['left'].set_color('blue') # setting up Y-axis tick color to blue
    ax.spines['top'].set_color('blue') #setting up above X-axis tick color to blue
    ax.spines['bottom'].set_color('blue') #setting up above X-axis tick color to blue
    ax.spines['right'].set_color('blue') #setting up above X-axis tick color to blue
    #fig.subplots_adjust(bottom=0.3) 
    ax.tick_params(axis="x", which="both", rotation=30) 
    #Save to temp buff
    buf = BytesIO()
    fig.savefig(buf, format="png")
    #embed result in html output
    data1 = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data1
"""
def matPlotsHum():
    altData = alData()
    dates = []
    hums = []
    for i in altData:
        dates.append(i[2])
        hums.append(i[4])
    x = dates
    y = hums
    print(y, x)
    #matplotting
    fig = Figure()
    ax = fig.subplots()
    fig.subplots_adjust(bottom=0.3)
    ax.tick_params(axis='x', which="both", rotation=30)
    ax = fig.subplots()
    ax.set_facecolor("#fff") # inner plot background color HTML black
    fig.patch.set_facecolor('#fff') # outer plot background color HTML black
    ax.plot(x, y, linestyle = 'dashed', c = '#11f', linewidth = '1.5',
    marker = 'o', mec = 'hotpink', ms = 10, mfc = 'hotpink' )
    ax.set_xlabel('Dato & tid')
    ax.set_ylabel('Fugtighed')
    ax.xaxis.label.set_color('hotpink') #setting up X-axis label color to hotpink
    ax.yaxis.label.set_color('hotpink') #setting up Y-axis label color to hotpink
    ax.tick_params(axis='x', colors='black') #setting up X-axis tick color to white
    ax.tick_params(axis='y', colors='black') #setting up Y-axis tick color to white
    ax.spines['left'].set_color('blue') # setting up Y-axis tick color to blue
    ax.spines['top'].set_color('blue') #setting up above X-axis tick color to blue
    ax.spines['bottom'].set_color('blue') #setting up above X-axis tick color to blue
    ax.spines['right'].set_color('blue') #setting up above X-axis tick color to blue
    fig.subplots_adjust(bottom=0.3) 
    ax.tick_params(axis="x", which="both", rotation=30) 
    #Save to temp buff
    buf = BytesIO()
    fig.savefig(buf, format="png")
    #embed result in html output
    data2 = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data2
"""
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
    alData()
    aPlot = matPlotsTemp()
    #bPlot = matPlotsHum()
    print(rowData, "fra hjemmeside")
    print(rowData[0][0], "fra hjemmeside")
    return render_template('home.html', rowData=rowData, aPlot=aPlot)

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
