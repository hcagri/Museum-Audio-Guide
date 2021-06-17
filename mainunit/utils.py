import random
import json
import os.path



def random_color_generate():
    return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

def check_occupancy(sec, dev_num, data):
    # How many people inside the particular section.
    usr_list = [] # Users except the one about to enter
    occupancy = 0

    for user in data:
        if user['dev_num'] != dev_num:
            usr_list.append(user)

    for user in usr_list:
        if user['section'] == sec:
            occupancy += 1
    
    return occupancy


def get_data():
    if os.path.isfile("/home/pi/dev/FlaskApp/data.json"):
        with open("data.json", 'r') as f:
            data = json.load(f)         
        return data
    return None


def random_lst():
    lst =[]
    colors = ['#2471A3', '#7D3C98', '#1ABC9C', '#F1C40F', '#D35400 ']
    for i in range(5):
        x = random.randint(20,980)
        y = random.randint(20,580)
        lst.append((x,y, colors[i]))

    return lst


def save_hist_file(data, file_name):

    path = os.getcwd()
    dirName = path + "/Visitor_Loc_Data"

    try:
        os.makedirs(dirName)    
        print("Directory " , dirName ,  " Created ")
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")

    with open(os.path.join(dirName, file_name + '.json'), 'w') as f:
        json.dump(data, f)

    print("File Saved to: {}".format(dirName))
    
