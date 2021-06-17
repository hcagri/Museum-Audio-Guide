import paho.mqtt.client as mqtt
import time
import serial
import datetime
import os
from utils import AudioPlayer, get_dwm_data


def on_connect(client, userdata, flags, rc):

    # When the handhelded device connected to mqtt network, first 
    # it will send a message to main processing unit as SetupMessage
    # in return the main processing unit will share the payment 
    # information of visitor with handheld device.

    if rc==0:
        print('connected OK')
        client.publish("device_1","SetupMessage")

    else:
        print('Bad connection Returned code = ', rc)

def on_disconnect(client, userdata, flags, rc=0):
    print('Disconnected result code ' + str(rc))

def on_message(client, userdata, message):
    ftopic = message.topic
    fmessage = message.payload.decode()

    global run_flag
    if ftopic == "dvc1/warning":

        if fmessage == 'quit':
            run_flag = 0
            return
        
        elif fmessage == 'OccupancyWarning':
            
            try:
                player.play_Warning(fmessage)
            except NameError:
                print("AudioPlayer instance is not yet created!")
        

    elif ftopic == "dvc1/payment":
        global payment
        if payment == -1:
            # Payment info first time received
            payment = fmessage # type of payment -> str
            print("Payment Info is: {}".format(payment))
        else:
            try:
                player.payment = fmessage
                player.payment_init()
                print("Payment info updated")
            except NameError:
                print("AudioPlayer instance is not yet created!")
        return



# !!! This part should be updated !!!
art_pos = [(0,0),(0, 3.70),(3,3.70),(3.50, 0.4),(6.5,1.85)] 


# Infinite Loop Condition
run_flag = 1

payment = -1

#--------------- Create MQTT Client -----------------

broker = "192.168.1.8" # Static IP of broker

client = mqtt.Client(client_id='dvc1')


client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

print('Connecting to broker ', broker)

client.connect(broker)
time.sleep(1.5)
client.loop_start()

client.subscribe(topic='dvc1/payment')
client.subscribe(topic='dvc1/warning')

# Wait for payment info
while payment == -1:
    time.sleep(0.2)


print(type(payment), "   ", payment)


# Initialize the Audio Player Object
player = AudioPlayer(art_pos=art_pos,payment = payment)


#---------------  DWM Connection -----------------
# Connect to dwm modules with serial connection
DWM = serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1)
print("Connected to " + DWM.name)
DWM.write(b'\r\r')
time.sleep(2)
DWM.write(b'lec\r')
time.sleep(1)

current_path = os.getcwd()
f_name = str(datetime.datetime.now()).replace(" ", "_") + '.txt'


try:
    os.makedirs(os.path.join(current_path, 'data_history'))    
except FileExistsError:
    print("Directory already exists")

f_out = open(os.path.join(current_path, 'data_history', f_name), 'w')

try:
    
    while run_flag:
        # NOT Complete
        pos_2D_str, pos_2D_tuple = get_dwm_data(DWM)
    
        if player.check_payment(pos_2D_tuple):
            player.play_Info(pos_2D_tuple)
        else:
            player.play_Warning('PaymentWarning')

        if pos_2D_str != -1:
            # send the current position information to Main Processing Unit
            f_out.write(pos_2D_str+'\n')
            client.publish("device_1", pos_2D_str)

except KeyboardInterrupt:
    
    DWM.write(b'quit\r')
    time.sleep(3)
    DWM.close()
    time.sleep(2)
    client.loop_stop()
    client.disconnect()
    time.sleep(2)
    print("Stopped")
    f_out.close()


f_out.close()
DWM.write(b'quit\r')
time.sleep(3)
DWM.close()
time.sleep(2)
client.loop_stop()
client.disconnect()
time.sleep(2)
print("Stopped")

