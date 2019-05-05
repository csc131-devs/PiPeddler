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
#import RPi.GPIO as GPIO, time
from time import clock
#from guiLoop import guiLoop ## https://gist.github.com/niccokunzmann/8673951

### switch is connected to 19
##switch = 19
##
### setup GPIO
##GPIO.setmode(GPIO.BCM)
##GPIO.setwarnings(False)
##GPIO.setup(switch,GPIO.IN)


# .txt file must be formatted as: "SongName-BPM"
# One song per line maximum
# parser will deal with all capitals and space
# Hyphen '-' required for parsing

# songlist dictionary, songlist list
songDictionary = {}
songList = []

# global index variable for click button song rotation
global current_index
current_index = 0

# global variable for current BPM
global current_bpm
current_bpm = 0

# open text file with songs and BPMs
# parse file object, set string to lowercase,
# strip outside whitespace, add to dictionary,
# append to list
def songDatabase():
    with open('songlist.txt') as songlist:
        for line in songlist:
            line = line.split('-')
            song = line[0].strip()
            song = song.lower()
            bpm = line[1].strip()
            #hexval 1
            #hexval 2

            songDictionary[song] = bpm 
            songList.append(song)
        
# Setup GUI
class GUI(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master=master
 
        # create and populate list box on left side of GUI
        self.listbox = Listbox(master,font=('Courier', 16), selectmode=SINGLE, exportselection=0)
        self.listbox.grid(row=0, rowspan=3, column=0, pady=3, sticky=N+S+E+W)
        self.index = 0

        # populate songs in listbox
        for i in range(len(songList)):
            self.listbox.insert(END, songList[i])

        # highlight index 0
        self.listbox.select_set(current_index)
    
        # prev/next song cycle buttons setup
        self.button2 = Button(self.master, text="-->", fg="blue", command=self.next_song,\
                              font=('Courier',40))
        self.button2.grid(row=2, column=2, sticky=N+S+E+W)

        self.button1 = Button(self.master, text="<--", fg="blue", command=self.prev_song,\
                              font=('Courier',40))
        self.button1.grid(row=2, column=1, sticky=N+S+E+W)

        # place PiPedaler ascii art in top right of UI
        self.img = PhotoImage(file="PiPedaler_gif.gif")
        pipedaler_img = Label(image=self.img)
        pipedaler_img.image = self.img
        pipedaler_img.grid(row=0, column=1, columnspan=2, sticky=N+S+E+W)

        # Current BPM box
        self.CBPM = Label(self.master, text="Current BPM: {}".format(songDictionary[songList[current_index]]), font=('Courier',24))
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
        global current_bpm
        current_bpm = songDictionary[songList[current_index]]
        self.CBPM.configure(text="Current BPM: {}".format(current_bpm))
        
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
        global current_bpm
        current_bpm = songDictionary[songList[current_index]]
        self.CBPM.configure(text="Current BPM: {}".format(current_bpm))

    # update current BPM from pedal taps
    def update_bpm(self, bpm):
        global current_bpm
        current_bpm = bpm
        self.CBPM.configure(text="Current BPM: {}".format(current_bpm),fg="red")
        
############################################################################################
# MAIN
############################################################################################
# parse .txt file song song information, and stong it in a dictionary
songDatabase()

# Create the window
window = Tk()
#window.title("Pi Pedaler")

# Create the GUI as a TKinter canvas inside the window
g = GUI(window)

# Wait for the window to close
window.mainloop()

### infinite loop listening for user input
##while 1:
##    window.update()
##    b = GPIO.input(switch) # button state
##    if(b == GPIO.HIGH):
##        t1 = t2
##        t2 = time.clock()
##        diff = t2 - t1
##        
##    if (t1!=0 and diff <= 1.5 and diff >= 0.24): # between 40 and 250 bpm 
##        tempo = 60/diff
##        print round(tempo,2), 'BPM'
##        freq = 1 / diff
##        #pwm.ChangeFrequency(freq)
##            
##                 
##    elif (b == GPIO.LOW and N == 3):
##        N = 0

