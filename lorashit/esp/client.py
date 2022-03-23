from time import sleep
from ulora import LoRa, ModemConfig, SPIConfig
from machine import Pin
import dht
import GPSfunk

sensor = dht.DHT11(Pin(15))
#laver en tom liste. som hedder senslist
senslist = []
def sensor2():
    try:
        #måler med DHT11 sensor og putter temp og hum ind i senslist
        sleep(2)
        sensor.measure()
        temp = sensor.temperature()
        tempF = temp * (9/5) + 32.0
        hum = sensor.humidity()
        senslist.append(hum)
        senslist.append(temp)
        print(senslist)
        
    except OSError as e:
        print('failed to read sensor.')
        
    return temp,hum

def gps():
    #bruger GPS til at finde latitude og longtitude og derefter putter dem ind i vores senslist
    gpsxd = GPSfunk.main()
    lat = gpsxd[1]
    lon = gpsxd[2]
    senslist.append(lat)
    senslist.append(lon)
    
#pins:  cs = 5, vin = 3v3, ground = ground, g0 = 0, sck = 14, miso = 12, mosi = 13
# Lora Parameters
RFM95_RST = 27
RFM95_SPIBUS = SPIConfig.esp32_1
RFM95_CS = 5
RFM95_INT = 0
RF95_FREQ = 868.0
RF95_POW = 20
CLIENT_ADDRESS = 1
SERVER_ADDRESS = 222

# initialise radio
lora = LoRa(RFM95_SPIBUS, RFM95_INT, CLIENT_ADDRESS, RFM95_CS, reset_pin=RFM95_RST, freq=RF95_FREQ, tx_power=RF95_POW, acks=True)


# loop and send data
while True:
    sensor2()
    print(senslist)
    sleep(1)
    gps()
    print(senslist)
    sleep(1)
    sendData = str(senslist)
    print(type(sendData), sendData, "fra loopen")
    sleep(2)
    lora.send_to_wait(sendData, SERVER_ADDRESS)
    print("sent")
    sleep(5)
    #til sidst gør vi senslist tom
    senslist = []
