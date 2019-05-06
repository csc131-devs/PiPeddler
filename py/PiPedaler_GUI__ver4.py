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
                return super(Translator, self).__
        init__("/dev/ttyS0")

# set values for switches
tap = 23
nextSong = 24
lastSong = 25
womb = 27

# setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(tap, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(nextSong, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(lastSong, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(womb, GPIO.OUT)

# GLOBAL VARIABLES for list index and BPM
#global current_index
current_index = 0

# Song class
class Song():
    def __init__(self, song, bpm, bigsky, boomerang):
        self.song = song
        self.bpm = bpm
        self.bigsky = bigsky
        self.boomerang = boomerang

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
            bpm = float(line[1].strip())
            bigsky = line[2].strip()
            boomerang = line[3].strip()

            song = Song(song, bpm, bigsky, boomerang)

            songList.append(song)
        
# Setup GUI
class GUI(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master=master
        self.lastTime = 0.0
        self.bpmFlags = 0
        self.currentbpm = 0
        master.attributes("-fullscreen",True)       

        Grid.rowconfigure(master, 0, weight=1)
        Grid.columnconfigure(master, 0, weight=1)
               
        # create and populate list box on left side of GUI
        self.listbox = Listbox(master,width=25, height=10, font=('Courier', 16), selectmode=SINGLE, exportselection=0)
        self.listbox.grid(row=0, rowspan=3, column=0, pady=3, sticky=N+S+E+W)
        self.index = 0
                
        # populate songs in listbox
        for i in range(len(songList)):
            self.listbox.insert(END, songList[i].song)

        # highlight index 0
        self.listbox.select_set(current_index)
    
        # prev/next song cycle buttons setup
        self.button2 = Button(self.master, height=3, text="-->", fg="blue", command=self.next_song,\
                              font=('Courier',40))
        self.button2.grid(row=2, column=2, sticky=N+S+E+W)

        self.button1 = Button(self.master, height=3, text="<--", fg="blue", command=self.prev_song,\
                              font=('Courier',40))
        self.button1.grid(row=2, column=1, sticky=N+S+E+W)

        # place PiPedaler ascii art in top right of UI
        self.img = PhotoImage(file="PiPedaler_gif.gif")
        pipedaler_img = Label(image=self.img)
        pipedaler_img.image = self.img
        pipedaler_img.grid(row=0, column=1, columnspan=2, sticky=N+S+E+W)

        # Current BPM box
        self.CBPM = Label(self.master, height=3, text="Current BPM: {}".format(songList[current_index].bpm), font=('Courier',24))
        self.CBPM.grid(row=1, column=1, columnspan=2, sticky=N+S+E+W)
 
    # previous song method
    def prev_song(self): 
        self.listbox.select_clear(current_index)
        global current_index
        current_index = current_index - 1

        # handles cycling from beginning to end of list
        if ( current_index < 0 ):
            self.listbox.select_clear(current_index)
            current_index = len(songList)-1

        # updates current BPM box        
        self.listbox.select_set(current_index)
        self.setFlags(songList[current_index].bpm)
        self.CBPM.configure(text="Current BPM: {}".format(self.currentbpm), fg="black")
        
    # next song method        
    def next_song(self):
        self.listbox.select_clear(current_index)
        global current_index
        current_index = current_index + 1 

        # handles cycling from end to beginning of list
        if ( current_index  > len(songList)-1 ):
            self.listbox.select_clear(current_index)
            current_index = 0

        # updates current BPM box        
        self.listbox.select_set(current_index)
        self.setFlags(songList[current_index].bpm)
        self.CBPM.configure(text="Current BPM: {}".format(self.currentbpm), fg="black")

    # update current BPM from pedal taps
    def update_bpm(self, bpm):
        self.setFlags(bpm)
        self.CBPM.configure(text="Current BPM: {}".format(self.currentbpm),fg="red")

    def setFlags(self, value):
        self.currentbpm = value
        self.setBPM(True)

    def setBPM(self, override = False):  # Transistor, I/O values are flipped
        currtime = time.clock()
        if override:    # Destroy everything
                self.bpmFlags |= 1 << 0
                GPIO.output(womb, GPIO.LOW)
                self.lastTime = currtime + 0.1
                return
        
        if currtime < self.lastTime:
                return

        if self.bpmFlags & 1 << 0:
                GPIO.output(womb, GPIO.HIGH)
                self.bpmFlags |= 1 << 1
                self.bpmFlags &= ~1 << 0
                delay = 60.0/self.currentbpm
                print delay
                self.lastTime = currtime + delay

        if self.bpmFlags & 1 << 1:
                GPIO.output(womb, GPIO.LOW)
                self.bpmFlags |= 1 << 2
                self.bpmFlags &= ~1 << 1
                self.lastTime = currtime + 0.1

        if self.bpmFlags & 1 << 2:
                GPIO.output(womb, GPIO.HIGH)
                self.bpmFlags = 0
                self.lastTime = 99999999
                
            
#########################################################################################################
# MAIN
#########################################################################################################s
# parse .txt file song song information, and stong it in a dictionary
songDatabase()

# Create the window
window = Tk()
#window.title("Pi Pedaler")

# Create the GUI as a TKinter canvas inside the window
g = GUI(window)

# Wait for the window to close
#window.mainloop()


debounce = 0
bpmtoggle = False
bpmlast = 0
lastNextSong=0
lastPrevSong=0
try:
        
        # infinite loop listening for user input
        while 1:
                g.setBPM()
                window.update()
                b = GPIO.input(tap) # button state
                c = GPIO.input(nextSong) # button state
                d = GPIO.input(lastSong) # button state
                if(b == GPIO.HIGH and not bpmtoggle):
                        bpmtoggle = True
                        currbpm = time.clock()
                        
                        diff = currbpm - bpmlast
                        if(diff > 0.24):
                                
                                if(0.24 <= diff <= 1.5):
                                        tempo = 60/diff
                                        #print round(tempo,2), 'BPM'
                                        freq = 1 / diff
                                        #pwm.ChangeFrequency(freq)
                                        g.update_bpm((round(tempo,2)))

                                bpmlast = currbpm

                elif (b == GPIO.LOW and bpmtoggle):
                        bpmtoggle = False
                                                         
                if(c == GPIO.HIGH and lastNextSong == 0):
                        g.next_song()
                        lastNextSong=1

                elif(c == GPIO.LOW and lastNextSong == 1):
                        lastNextSong=0

                elif(d == GPIO.HIGH and lastPrevSong == 0):
                        g.prev_song()
                        lastPrevSong=1

                elif(d == GPIO.LOW and lastPrevSong == 1):
                        lastPrevSong=0
                
except KeyboardInterrupt:
        GPIO.cleanup()


