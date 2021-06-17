from utils import random_color_generate
from flask import Flask, redirect, url_for, render_template, request, flash
import datetime
import random
import time


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
art_pos = [(0,0),(0,370), (300,370), (350,0), (650,185)]

app = Flask(__name__)
app.secret_key = "VComp"




@app.route("/")
@app.route("/home")
def home():
    
    positions = []
    names = []        
    colors = []

    print(data)
    for user in data:
        colors.append(user['color'])
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
        payment = str(s1) + str(s2)
        
        color = random_color_generate() 

        user = {
            "name": vname,
            "email": vemail,
            "payment": payment,
            "dev_num": vdev_num, # integer
            "position": None,
            "position_history" : [],
            "color" : color
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
                fname = user["email"].split("@")[0] + '_' + date

                # Before checkout, save the history of postion informations to a file
                
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

                
                flash("Payment is updated for {}".format(user["name"]), "info")
                
        return redirect(url_for("home"))
    return render_template("payment.html")

@app.route("/position", methods=["POST", "GET"])
def position():

    if request.method == "POST":
        vdev_num = request.form["dn"]
        xpos = float(request.form["xps"])
        ypos = float(request.form["yps"])
        for user in data:

            if vdev_num == user['dev_num']:
                section = 2 if xpos > 3 else 1
                user['position'] = (xpos, ypos)
                user['section'] = section
                
        return redirect(url_for("home"))
    return render_template("update_pos.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, use_reloader=False, debug=True)