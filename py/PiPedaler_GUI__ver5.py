############################################################################################################################################################################################
#  _ _ _        _ _ _    _ _ _   _ _        _       _       _ _ _   _ _ _   
# |  __  )     |  __  ) |  _ _| |   \      / \     | |     |  _ _| |  __  ) 
# | |__| | _   | |__| | | |__   |  _ \    / _ \    | |     | |__   | |__| | 
# |  _ _/ (_)  |  _ _/  |  __|  | |_| |  / |_| \   | |     |  __|  |  _  /  
# | |     | |  | |      | |_ _  |    /  / /   \ \  | |_ _  | |_ _  | | \ \  
# |_|     |_|  |_|      |_ _ _| |_ _/  /_/     \_\ |_ _ _| |_ _ _| |_|  \_\ 
#                                                                           
# DEVELOPED BY: David Love, John Mascagni, Tony Roberts           
############################################################################################################################################################################################
from Tkinter import *
import RPi.GPIO as GPIO, time
from time import clock
import serial
from os import system
from sys import version_info


class Translator(serial.Serial):
        def __init__(self):
                system("sudo systemctl stop serial-getty@ttyS0.service")
                return super(Translator, self).__init__("/dev/ttyS0")

# set values for switches
tap = 23
nextSong = 24
lastSong = 25
womb = 27

# set pins for serial enable
enable = 12



# setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(tap, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(nextSong, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(lastSong, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(womb, GPIO.OUT)
GPIO.setup(enable, GPIO.OUT)


# GLOBAL VARIABLES for list index and BPM
#global current_index
current_index = 0

# Song class
class Song():
    def __init__(self, song, bpm, timeline, bigsky):
        self.song = song
        self.bpm = bpm
        self.timeline = timeline
        self.bigsky = bigsky

# songList list
songList = []

# .txt file must be formatted as: "SongName-BPM"
# One song per line maximum
# parser will split line into component parts
# Hyphen '-' required for parsing

# open text file with songs and BPMs
# parse file object, strip outside whitespace,
# append to list
def songDatabase():
    with open('songlist.txt') as songlist:
        for line in songlist:
            line = line.split('-')
            song = line[0].strip()
            bpm = int(line[1].strip())
            timeline = line[2].strip()
            bigsky = line[3].strip()

            song = Song(song, bpm, timeline, bigsky)

            songList.append(song)
        
# Setup GUI
class GUI(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master=master
        self.lastTime = 0.0
        self.currentbpm = 120
        master.attributes("-fullscreen",True)       

        Grid.rowconfigure(master, 0, weight=1)
        Grid.columnconfigure(master, 0, weight=1)
               
        # create and populate list box on left side of GUI
        self.listbox = Listbox(master,width=25, height=10, font=('Courier', 16), bg="black", fg="white",selectmode=SINGLE, exportselection=0)
        self.listbox.grid(row=0, rowspan=3, column=0, pady=3, sticky=N+S+E+W)
        self.index = 0

        # song select through touching listbox item
        def touchSelect(event):
            #selection = self.listbox.get(self.listbox.curselection())
            global current_index
            self.listbox.select_clear(current_index)
            self.listbox.activate(self.listbox.curselection())
            current_index = self.listbox.index(ACTIVE)
            self.listbox.get(self.listbox.curselection())
            self.CBPM.configure(text="Current BPM: {}".format(songList[current_index].bpm), fg="black")

            
        self.listbox.bind('<<ListboxSelect>>', touchSelect)        

        # populate songs in listbox
        for i in range(len(songList)):
            self.listbox.insert(END, songList[i].song)

        # highlight index 0
        self.listbox.select_set(current_index)
    
        # prev/next song cycle buttons setup
        self.button2 = Button(self.master, height=3, text="-->", bg="black", fg="blue", command=self.next_song,\
                              font=('Courier',40, 'bold'))
        self.button2.grid(row=2, column=2, sticky=N+S+E+W)

        self.button1 = Button(self.master, height=3, text="<--", bg="black", fg="blue", command=self.prev_song,\
                              font=('Courier',40, 'bold'))
        self.button1.grid(row=2, column=1, sticky=N+S+E+W)

        # place PiPedaler box in top right of UI
        self.img = PhotoImage(file="PiPedaler.gif")
        pipedaler_img = Label(image=self.img)
        pipedaler_img.image = self.img
        pipedaler_img.grid(row=0, column=1, columnspan=2, sticky=N+S+E+W)

        # Current BPM box
        self.CBPM = Label(self.master, height=3, text="Current BPM: {}".format(songList[current_index].bpm), font=('Courier',24))
        self.CBPM.grid(row=1, column=1, columnspan=2, sticky=N+S+E+W)

        
        pwm.ChangeFrequency(1/(60.0/self.currentbpm))
        self.serialize()
 
    # previous song method
    def prev_song(self): 
        global current_index
        self.listbox.select_clear(current_index)
        current_index = current_index - 1

        # handles cycling from beginning to end of list
        if ( current_index < 0 ):
            self.listbox.select_clear(current_index)
            current_index = len(songList)-1

        # updates current BPM box        
        self.listbox.select_set(current_index) 
        self.currentbpm=(songList[current_index].bpm)
        pwm.ChangeFrequency(1/(60.0/self.currentbpm))
        self.CBPM.configure(text="Current BPM: {}".format(self.currentbpm), fg="black")
        self.serialize()
        
    # next song method        
    def next_song(self):
        global current_index
        self.listbox.select_clear(current_index)
        current_index = current_index + 1 

        # handles cycling from end to beginning of list
        if ( current_index  > len(songList)-1 ):
            self.listbox.select_clear(current_index)
            current_index = 0

        # updates current BPM box        
        self.listbox.select_set(current_index)
        self.currentbpm=(songList[current_index].bpm)
        pwm.ChangeFrequency(1/(60.0/self.currentbpm))
        self.CBPM.configure(text="Current BPM: {}".format(self.currentbpm), fg="black")
        self.serialize()

    # update current BPM from pedal taps
    def update_bpm(self, bpm):
        self.currentbpm=(bpm)
        pwm.ChangeFrequency(1/(60.0/bpm))
        self.CBPM.configure(text="Current BPM: {}".format(self.currentbpm),fg="red")
        self.serialize()

    def serialize(self):
        global current_index
        t.write("{},{},{},{}".format(songList[current_index].song, self.currentbpm,\
            songList[current_index].timeline, songList[current_index].bigsky))
            
                
            
#########################################################################################################
# MAIN
#########################################################################################################s
# parse .txt file song song information, and stong it in a dictionary
songDatabase()

# Create the window
window = Tk()
#window.title("Pi Pedaler")

pwm = GPIO.PWM(womb, 2)
pwm.start(90)

# enable tx and rx pins
GPIO.output(enable, GPIO.HIGH)


# Initialize translator
t = Translator()

# Create the GUI as a TKinter canvas inside the window
g = GUI(window)


bpmtoggle = False
bpmlast = 0
lastNextSong=0
lastPrevSong=0
debounce=0
debounceClock=time.clock()
try:
        
        # infinite loop listening for user input
        while 1:
                window.update()
                if (time.clock()-debounceClock > .24):
                        debounce = 0
                b = GPIO.input(tap) # button state
                c = GPIO.input(nextSong) # button state
                d = GPIO.input(lastSong) # button state 
                if(b == GPIO.HIGH and not bpmtoggle and debounce==0):
                        debounceClock = time.clock()
                        debounce = 1
                        bpmtoggle = True
                        currbpm = time.clock()
                        
                        diff = currbpm - bpmlast
                        if(diff >= 0.24):
                                if(diff <= 1.5):
                                        tempo = 60/diff
                                        g.update_bpm(int((round(tempo))))

                                bpmlast = currbpm

                elif (b == GPIO.LOW and bpmtoggle):
                        bpmtoggle = False
                                                         
                if(c == GPIO.HIGH and lastNextSong == 0 and debounce == 0):
                        debounceClock = time.clock()
                        debounce = 1
                        g.next_song()
                        lastNextSong=1

                elif(c == GPIO.LOW and lastNextSong == 1):
                        lastNextSong=0

                elif(d == GPIO.HIGH and lastPrevSong == 0 and debounce == 0):
                        debounceClock = time.clock()
                        debounce = 1
                        g.prev_song()
                        lastPrevSong=1

                elif(d == GPIO.LOW and lastPrevSong == 1):
                        lastPrevSong=0
                
except KeyboardInterrupt:
        GPIO.cleanup()


