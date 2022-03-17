from time import sleep
from ulora import LoRa, ModemConfig, SPIConfig
from machine import Pin
import dht

sensor = dht.DHT11(Pin(15))
senslist = []
def sensor2():
    try:
        sleep(2)
        sensor.measure()
        temp = sensor.temperature()
        tempF = temp * (9/5) + 32.0
        hum = sensor.humidity()
        senslist = [temp,hum]
        print(senslist)
        
    except OSError as e:
        print('failed to read sensor.')
        
    return temp,hum
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
    temp, hum = sensor2()
    senslist = [temp, hum]
    sleep(2)
    sendData = str(senslist)
    print(type(sendData), sendData, "fra loopen")
    sleep(2)
    lora.send_to_wait(sendData, SERVER_ADDRESS)
    print("sent")
    sleep(5)
