from pyLoraRFM9x import LoRa, ModemConfig
# from https://github.com/epeters13/pyLoraRFM9x
# This is our callback function that runs when a message is received
def on_recv(payload):
    print("From:", payload.header_from)
    #print("Received:", payload.message)
    print("RSSI: {}; SNR: {}".format(payload.rssi, payload.snr))
    mess = payload.message
    print(mess,"hej fra veriable")
    mess = str(mess)
    frontslicethebitch = mess[3:9]
    print(frontslicethebitch)
    Splitthebitch = frontslicethebitch.split(', ')
    print(Splitthebitch)
    

# Use chip select 1. GPIO pin 5 will be used for interrupts and set reset pin to 25
# The address of this device will be set to 222
lora = LoRa(1, 17, 222, reset_pin = 25, freq=868, modem_config=ModemConfig.Bw125Cr45Sf128, tx_power=14, acks=True)
lora.on_recv = on_recv
while True:
# Send a message to a recipient device with address 10
# Retry sending the message twice if we don't get an  acknowledgment from the recipient
    message = "Hello there!"
    status = lora.send_to_wait(message, 1, retries=20)
    if status is True:
        print("Message sent!")
    else:
        print("No acknowledgment from recipient")
