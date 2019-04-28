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

# songlist dictionary, songlist list
songDictionary = {}
songList = []

# index variable for click button song rotation
current_index = 0

# .txt file must be formatted as: "SongName-BPM"
# One song per line maximum
# parser will deal with all capitals and space
# Hyphen '-' required for parsing

# open text file with songs and BPMs
# parse file object, set string to lowercase,
# strip outside whitespace, add to dictionary,
# append to list
with open('../data/songlist.txt') as songlist:
    for line in songlist:
        line = line.split('-')
        song = line[0].strip()
        song = song.lower()
        bpm = line[1].strip()
        songDictionary[song] = bpm 

        songList.append(song)
        
# Setup GUI
class GUI(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master=master

        # prev/next song cycle button setup
        self.button1 = Button(self.master, text="-->", fg="blue", command=self.prev_song,\
                              height=10, width=10)
        self.button1.pack(side=RIGHT)

        self.button2 = Button(self.master, text="<--", fg="blue", command=self.next_song,\
                              height=10, width=10)
        self.button2.pack(side=RIGHT)

        # setup the user input at the bottom of the GUI
        # the widget is a Tkinter Entry
        # set its background to white and bind the return key to the
        # function process in the class
        # push it to the bottom of the GUI and let it fill
        # horizontally
        # give it focus so the user doesn't have to click on it
        self.pack(fill=BOTH, expand=1)

        self.user_input = Entry(self, bg="white")
        self.user_input.bind("<Return>", self.process)
        self.user_input.pack(side=BOTTOM, fill=X)
        self.user_input.focus()

        # setup the image to the left of the GUI
        # the widget is a Tkinter Label
        # don't let the image control the widget's size
        img=None
        self.image = Label(self, width=WIDTH / 2, image=img)
        self.image.image = img
        self.image.pack(side=LEFT, fill=Y)
        self.image.pack_propagate(False)

        # setup the text to the right of the GUI
        # first, the frame in which the text will be placed    
        text_frame = Frame(self, width=WIDTH / 3)

        # the widget is a Tkinter Text
        #disable it by default
        # don't let the widget control the frame's size
        self.text = Text(text_frame, bg="lightgrey", state=DISABLED)
        self.text.pack(fill=Y, expand=1)
        text_frame.pack(side=RIGHT, fill=Y)
        text_frame.pack_propagate(False)

        self.img = PhotoImage(file="PiPedaler_gif.gif")
        self.image.config(image=self.img)
        self.image.image = self.img

    # print status to GUI
    def setStatus(self, response):
        self.text.config(state=NORMAL)
        self.text.delete("1.0", END)

        self.text.insert(END, response)

        self.text.config(state=DISABLED)

    # process user input
    def process(self):
        query = self.user_input.get()
        query = query.lower()

        # song not found response
        response = "That song is not in the list. Please try again"

        # if song is a key in dictionary
        # concatenate appropriate title and BPM output
        if(songDictionary.get(query)):
            response = "Title: " + query + "\n" + "BPM: " + songDictionary[query]

        # send response to setStatus method for printing
        # clear the player's input
        self.setStatus(response)
        self.user_input.delete(0, END)

    def prev_song(self):
        global current_index
        current_index = current_index - 1

        if ( (current_index) < 0 ):
            current_index = len(songList)-1

        current_song = songList[current_index]

        # if song is a key in dictionary
        # concatenate appropriate title and BPM output
        if(songDictionary.get(current_song)):
            response = "Title: " + current_song + "\n" + "BPM: " + songDictionary[current_song]
        
        # display the response on the right of the GUI
        # clear the player's input
        self.setStatus(response)
        self.user_input.delete(0, END)
            
    def next_song(self):
        global current_index
        current_index = current_index + 1 

        if ( (current_index ) > len(songList)-1 ):
            current_index = 0

        current_song = songList[current_index]

        # if song is a key in dictionary
        # concatenate appropriate title and BPM output
        if(songDictionary.get(current_song)):
            response = "Title: " + current_song + "\n" + "BPM: " + songDictionary[current_song]

        # display the response on the right of the GUI
        # clear the player's input
        self.setStatus(response)
        self.user_input.delete(0, END)
        
############################################################################################
# MAIN
############################################################################################
# Default size of the GUI is ?x?
WIDTH = 750
HEIGHT = 600

# Create the window
window = Tk()
window.title("Pi Pedaler")

# Create the GUI as a TKinter canvas inside the window
g = GUI(window)

# Wait for the window to close
window.mainloop()