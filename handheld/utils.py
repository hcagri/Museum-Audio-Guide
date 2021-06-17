from pygame import mixer
import numpy as np
import os



class AudioPlayer():


    def __init__(self, art_pos, payment):

        self.payment = payment
        self.art_pos = art_pos
        self.pos_2D = (0,0)

        mixer.init() # initialize the mixer
        self.i_channel = mixer.Channel(1)  # Information Channel
        self.w_channel = mixer.Channel(2)  # Payment Warning Channel
        self.w2_channel = mixer.Channel(3) # Occupancy Warning Channel
    
        self.i_channel.set_volume(1)
        self.w_channel.set_volume(1)
        self.w2_channel.set_volume(1)
        
        self.path = os.getcwd()

        self.payment_init()

        self.playing_sound = ''
        print("Player Object Created")

    def payment_init(self):
        payment = int(self.payment)
        s2 = payment%10
        s1 = payment//10 % 10
        self.payment_lst = (s1, s2)


    def check_payment(self, pos_2D):

        if pos_2D == -1:
            print('Returned bc pos is -1 check Payment') 
            return True

        x = pos_2D[0]
        print("Warning x position:   ", x)
        if x<3:
            region = 0
        else:
            region = 1
        print('The payment Bool:  ',self.payment_lst[region])
        print(self.payment_lst)
        return self.payment_lst[region]
                    

    def closesest_Art(self):
        # Calculates the distances from visitor to the anchors, then returns the index of 
        # the anchor closest to the Tag. If the closest distance is smaller than 1.3 meter.
        # if any visitor closer to one of the anchors(art pieces) than the visitor should be
        # informed.
        print("Closes Art Called")
        x1 = self.pos_2D[0]
        y1 = self.pos_2D[1]
        Min_DIST = 100
        for x2,y2 in self.art_pos:

            # Calculate 1D distance of visitor to each anchor
            dist_1D = ((x1 - x2)**2  + (y1 - y2)**2 )**0.5

            if dist_1D < Min_DIST:
                # Find the minimum distance
                Min_DIST = dist_1D
                Min_Idx = self.art_pos.index((x2,y2))
        
        print("Min_dist: ", Min_DIST)
        if Min_DIST < 1: # in meter
            print('Returned Value: {}'.format(Min_Idx))
            return Min_Idx

        print('Returned None') 
        return None
    
    def get_SoundObj(self):
        # if visitor close to any art pieces, it will return corresponding sound object
        # if not, will return None
        
        print("get_SoundObj Called")
        art_sounds = ['Samurai_Armour', 'SculptureTreeLife', 'BookDeadHunefer',
                    'IznikFootedBasin', 'HolyThorn']
       
        idx = self.closesest_Art()
        # index of the closest anchor

        if idx != None: # if not None | Yani herhangi bir art piece e yakinsa
            sound_name = art_sounds[idx]
            f_name = os.path.join(self.path, 'Info_Sounds', sound_name + '.wav')
            print(f_name)
            sound = mixer.Sound(f_name)
            print("Returned Sound", art_sounds[idx] )
            return sound, sound_name

        print('Returned None') 
        return None, None # hic bir art piece yakin degil.
        


    def play_Info(self, pos_2D):

        self.pos_2D = pos_2D
        print('Play Info Called') 
        if pos_2D == -1:
            print('Returned bc pos is -1') 
            return
        
        sound, sound_name = self.get_SoundObj()
        
        # if visitor is close to a art piece, an information about that art piece
        # will be stored in 'sound' object

        if not self.w_channel.get_busy():
            # If there is no warning sound is playing.
            print('w_channedl is not busy') 
            if sound is None:

                if self.i_channel.get_busy():
                    self.playing_sound = ''
                    self.i_channel.stop()

                # if there is no sound object available, than do not play anything
                # Return immediately
                print('Returned sound is none') 
                return 

            if self.i_channel.get_busy() and sound_name == self.playing_sound:
                # if channel is busy and the playing sound is the sound 
                # that should play on a current position. Then return
                print('Returned sound is playing') 
                return
            
            elif self.i_channel.get_busy() and sound_name != self.playing_sound:
                # if channel is busy and the playing sound is the NOT the
                # the sound that should play on a current position. Then
                # stop current sound and play the new sound.

                self.i_channel.stop()
                
                if sound: # If returned value is not None
                    self.playing_sound = sound_name
                    self.i_channel.play(sound)
                
            
            else:
                print('The sound is playing in else block') 
                self.playing_sound = sound_name
                self.i_channel.play(sound)


    def play_Warning(self,Warning_Name):

        # w_channel -> Payment Warning Channel
        # w2_channel -> Occupancy Warning Channel
        # i_channel -> Information Channel
        print('Entered play_Warning') 
        fname = os.path.join(self.path, 'Warning_Sounds', Warning_Name + '.wav')
        print(fname)
        sound = mixer.Sound(fname)

        if self.i_channel.get_busy():
            # If there is an information playing, stop that
            # Because warning sound will be played
            self.i_channel.stop()

        if Warning_Name == 'PaymentWarning':
            if self.w_channel.get_busy() or self.w2_channel.get_busy():
                # If already warning playing return
                return

            else:
                # Channel is free play the warning
                self.w_channel.play(sound)
            
        else: # Occupancy Warning
            # Occupancy Warning has the priority
            if self.w_channel.get_busy():
                self.w_channel.stop()
                self.w2_channel.play(sound)
                return
            if self.w2_channel.get_busy():
                return
            else:
                self.w2_channel.play(sound)




def get_pos(pos_data):

    # return 2D position information
    x1,y1 = pos_data["anc_pos"][0]
    x2,y2 = pos_data["anc_pos"][1]
    x3,y3 = pos_data["anc_pos"][2]
    d1 = pos_data["dist2anc"][0]
    d2 = pos_data["dist2anc"][1]
    d3 = pos_data["dist2anc"][2]

    b1 = x1**2+y1**2-x3**2-y3**2-d1**2+d3**2
    b2 = x2**2+y2**2-x3**2-y3**2-d2**2+d3**2
    rr11 = 2*(x1-x3)
    rr12 = 2*(y1-y3)
    rr21 = 2*(x2-x3)
    rr22 = 2*(y2-y3)

    A = np.array([[rr11, rr12], [rr21, rr22]])
    b = np.array([[b1],[b2]])

    try:
        pos = np.linalg.solve(A,b)
    except:
        pos = np.matmul(np.matmul(np.linalg.inv(np.matmul(np.transpose(A),A)),np.transpose(A)),b)

    x = pos[0]
    y = pos[1]
    return float(x) ,float(y)




def get_dwm_data(DWM):

    # This function communicates with dwm modules, and reads the 
    # position informations given by dwm.

    data = DWM.readline()
    data = str(data.decode())
    data = data.replace("\r\n", '')
    data = data.split(',')
    print(data)

    pos_data = {
                    "anc_pos" : [],
                    "dist2anc" : [],
                    "pos_dwm": [],
                    "pos_vcomp" : []
                }

    if 'DIST' in data:
        numAnchors = int(data[data.index("DIST")+1])

        for i in range(numAnchors):
                
            x = float(data[data.index("AN"+str(i))+2])
            y = float(data[data.index("AN"+str(i))+3])
            pos_data["anc_pos"].append((x,y))
            pos_data["dist2anc"].append(float(data[data.index("AN"+str(i))+5]))

        if("POS" in data):
                
            x = float(data[data.index("POS")+1])
            y = float(data[data.index("POS")+2])
            pos_data["pos_dwm"].append(x)
            pos_data["pos_dwm"].append(y)

        if len(pos_data["anc_pos"])>2:
            x,y = get_pos(pos_data)
            pos_data["pos_vcomp"].append(x)
            pos_data["pos_vcomp"].append(y)

            # Returned position information in "meter"
            return str(x) + ',' + str(y), (x,y)
        
    return -1, -1 # Means there is no location data obtained