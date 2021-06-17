from flask import Flask, redirect, url_for, render_template, request, flash
from utils import random_color_generate, save_hist_file, check_occupancy
from flask_mqtt import Mqtt # This supports only python 3.6
import datetime


data = []
MAX_OCCUPANCY = 1

# This data variable is the main data storage in the system.
# For each visitor a dictionary object is stored.
# The templete of the dictionary object is;
#
# personal_data = {
#             "name": vname,            # string
#             "email": vemail,          # string
#             "payment": vpayment,      # integer
#             "dev_num": vdev_num,      # integer
#             "position": 0,            # tuple -> (x,y)
#             "position_history" : []   # list stores tuples
#         }
#
#
#



anc_pos = [(0,0),(0,370),(650,185)] 
art_colors = ["#C0392B", "#C39BD3", "#76D7C4", "#F1C40F", "#21618C"]
art_pos = [(0,0),(0,370), (300,370), (350,40),(650,185)]

app = Flask(__name__)
app.secret_key = "VComp"


app.config['MQTT_BROKER_URL'] = '192.168.1.8' # Static IP of broker
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 2  # refresh time in seconds
mqtt = Mqtt(app)



@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    # When Mqtt connection established, subscribe the the following topics

    print("Connection is Succesfull")
    mqtt.subscribe('device_1')
    mqtt.subscribe('device_2')
    mqtt.subscribe('device_3')
    mqtt.subscribe('device_4')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):   

    print("Message Received")
    topic = message.topic
    payload=message.payload.decode()
    
    if payload == "SetupMessage": 
        # This message is an initializer. When handheld device first connect to the network,
        # sent this message to the main processing unit. Then, main processing unit will
        # share payment information with specified device.
        print("Setup Message is received from: {}".format(topic))
        for user in data:
            if topic == "device_" + str(user['dev_num']):
                send_topic = 'dvc'+ str(user['dev_num']) + '/payment'
                mqtt.publish(send_topic, str(user["payment"]))
                flash("{} is connected".format(user['name'])  , "info")
                return redirect(url_for("home"))

    else:
        # Store the position informations coming from multiple visitors.

        msg = payload.split(",")
        x = float(msg[0])
        y = float(msg[1])

        for user in data:        
            if topic == "device_" + str(user['dev_num']):
                user['position'] = (x,y)
                user['position_history'].append((x,y))
                new_section = 2 if x>3 else 1
                if user["section"] == None:
                    user["section"] = new_section
                else:
                    if new_section == user["section"]:
                        # If user remains in the same section do nothing
                        return 
                    else:
                        # if user changes section check how many people inside
                        # the room that the user about to enter. If mac occupancy
                        # is reached than send a occupancy warning to that user
                        if check_occupancy(new_section, user['dev_num'], data) >= MAX_OCCUPANCY:
                            send_topic = 'dvc'+ str(user['dev_num']) + '/warning'
                            mqtt.publish(send_topic, 'OccupancyWarning')
                            user["section"] = new_section
                            flash("Occupancy Warning Message is Sended to {}".format(user['name'])  , "info")
                            return redirect(url_for("home"))
                        else:
                            user["section"] = new_section




@app.route("/")
@app.route("/home")
def home():
    
    positions = []
    names = []        
    colors = []
    
    for user in data:
        colors.append(user["color"])
        positions.append(user["position"])
        names.append(user["name"])

    # Check the crowdness of the room. And send a warning message to new comer.
    # Not implemented yet
    return render_template("map.html", u_data=list(zip(names, positions, colors)) , anc_pos = anc_pos, art=list(zip(art_pos,art_colors)))
    



@app.route("/register", methods=["POST", "GET"])
def register():
    # When the form in the WebApp filled and button is pressed.
    # The information about visitors are stored in personal_data dictionary
    # variable than this dictionary is appended to the data variable.


    if request.method == "POST":
        vname = request.form["nm"]
        vemail = request.form["em"]
        vdev_num = request.form["dn"]
        sec1 = request.form.get("sec1")
        sec2 = request.form.get("sec2")

        s1 = 1 if sec1 == '1' else 0
        s2 = 1 if sec2 == '1' else 0
        vpayment = str(s1) + str(s2)

        color = random_color_generate()

        user = {
            "name": vname,
            "email": vemail,
            "payment": vpayment,
            "dev_num": vdev_num, # integer
            "position": None,
            "position_history" : [],
            "color" : color, 
            "section" : None
        }

        data.append(user)

        return redirect(url_for("home"))
    return render_template("register.html")


@app.route("/checkout", methods=["POST", "GET"])
def checkout():

    if request.method == "POST":
        vdev_num = request.form["dn"]

        for user in data:

            if vdev_num == user['dev_num']:
                date = str(datetime.datetime.now()).split(" ")[0] # Only the date info 21-04-2021
                fname = user["email"] + '_' + date

                # Before checkout, save the history of postion informations to a file
                save_hist_file(user['position_history'], fname)
                
                msg_topic = 'dvc' + user['dev_num'] + '/warning'
                mqtt.publish(msg_topic, "quit")
                u_name = user['name']

                # Kill the instance of the user when they checkout
                data.remove(user)
        
                if user not in data:
                    flash("Checkout is Succesful for {}".format(u_name)  , "info")
                else:
                    flash("Checkout failed", "info")
                
        return redirect(url_for("home"))
    return render_template("checkout.html")



@app.route("/payment", methods=["POST", "GET"])
def payment():

    if request.method == "POST":
        vdev_num = request.form["dn"]

        for user in data:

            if vdev_num == user['dev_num']:
                
                sec1 = request.form.get("sec1")
                sec2 = request.form.get("sec2")

                s1 = 1 if sec1 == '1' else 0
                s2 = 1 if sec2 == '1' else 0
                payment = str(s1) + str(s2)

                user["payment"] = payment

                send_topic = 'dvc'+ str(user['dev_num']) + '/payment'
                mqtt.publish(send_topic, str(user["payment"]))
                
                flash("Payment is updated for {}".format(user["name"]), "info")
                
        return redirect(url_for("home"))
    return render_template("payment.html")


@app.route("/position", methods=["POST", "GET"])
def position():

    if request.method == "POST":
        vdev_num = request.form["dn"]
        xpos = request.form["xps"]
        ypos = request.form["yps"]
        for user in data:

            if vdev_num == user['dev_num']:
                section = 2 if xpos > 3 else 1
                user['position'] = (xpos, ypos)
                user['section'] = section
                
        return redirect(url_for("home"))
    return render_template("update_pos.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, use_reloader=False, debug=True)