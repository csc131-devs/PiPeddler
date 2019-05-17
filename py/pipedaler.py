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
		system("sudo systemctl stop serial-getty@ttyS0.service")	# Stop the login screen so we can use this serial port
		return super(Translator, self).__init__("/dev/ttyS0")

# Set values for switches
TAP = 23
NEXT_SONG = 24
LAST_SONG = 25
WOMB = 27

# Set pins for serial enable
ENABLE = 12

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TAP, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(NEXT_SONG, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(LAST_SONG, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(WOMB, GPIO.OUT)
GPIO.setup(ENABLE, GPIO.OUT)

# Song class
class Song():
	def __init__(self, song, bpm, timeline, bigsky):
		self.song = song
		self.bpm = bpm
		self.timeline = timeline
		self.bigsky = bigsky

# songList list
SONG_LIST = []

# .txt file must be formatted as: "SongName-BPM"
# One song per line maximum
# Parser will split line into component parts
# Hyphen '-' required for parsing

# Open text file with songs and BPMs
# Parse file object, strip outside whitespace,
# Append to list
def songDatabase():
	with open('songlist.txt') as songlist:
		for line in songlist:
			line = line.split('-')
			song = line[0].strip()
			bpm = int(line[1].strip())
			timeline = line[2].strip()
			bigsky = line[3].strip()

			song = Song(song, bpm, timeline, bigsky)

			SONG_LIST.append(song)

# Setup GUI
class GUI(Frame):
	def __init__(self, master):
		Frame.__init__(self, master)
		self.master = master
		self.lastTime = 0.0
		self.currentbpm = 120
		master.attributes("-fullscreen",True)       

		Grid.rowconfigure(master, 0, weight = 1)
		Grid.columnconfigure(master, 0, weight = 1)

		# Create and populate list box on left side of GUI
		self.listbox = Listbox(master,width = 25, height = 10, font = ('Courier', 16), bg = "black", fg = "white", selectmode = SINGLE, exportselection = 0)
		self.listbox.grid(row = 0, rowspan = 3, column = 0, pady = 3, sticky = N+S+E+W)
		self.index = 0
		self.current_index = 0

		# Song select through touching listbox item
		def touchSelect(event):
			#selection = self.listbox.get(self.listbox.curselection())
			self.listbox.select_clear(self.current_index)
			self.listbox.activate(self.listbox.curselection())
			self.current_index = self.listbox.index(ACTIVE)
			self.listbox.get(self.listbox.curselection())
			self.currentbpm = (SONG_LIST[self.current_index].bpm)
			pwm.ChangeFrequency(1/(60.0/self.currentbpm))
			self.CBPM.configure(text = "Current BPM: {}".format(SONG_LIST[self.current_index].bpm), fg = "black")
			self.serialize()

		self.listbox.bind('<<ListboxSelect>>', touchSelect)        

		# Populate songs in listbox
		for i in range(len(SONG_LIST)):
			self.listbox.insert(END, SONG_LIST[i].song)

		# Highlight index 0
		self.listbox.select_set(self.current_index)

		# Prev/next song cycle buttons setup
		self.button2 = Button(self.master, height = 3, text = "-->", bg = "black", fg = "blue", command = self.next_song,\
							  font = ('Courier',40, 'bold'))
		self.button2.grid(row = 2, column = 2, sticky = N+S+E+W)

		self.button1 = Button(self.master, height = 3, text = "<--", bg = "black", fg = "blue", command = self.prev_song,\
							  font = ('Courier',40, 'bold'))
		self.button1.grid(row = 2, column = 1, sticky = N+S+E+W)

		# Place PiPedaler box in top right of UI
		self.img = PhotoImage(file = "PiPedaler.gif")
		pipedaler_img = Label(image = self.img)
		pipedaler_img.image = self.img
		pipedaler_img.grid(row = 0, column = 1, columnspan = 2, sticky = N+S+E+W)

		# Current BPM box
		self.CBPM = Label(self.master, height = 3, text = "Current BPM: {}".format(SONG_LIST[self.current_index].bpm), font = ('Courier', 24))
		self.CBPM.grid(row = 1, column = 1, columnspan = 2, sticky = N+S+E+W)

		pwm.ChangeFrequency(1/(60.0/self.currentbpm))
		self.serialize()

	# Previous song method
	def prev_song(self): 
		self.listbox.select_clear(self.current_index)
		self.current_index -= 1

		# Handles cycling from beginning to end of list
		if (self.current_index < 0):
			self.listbox.select_clear(self.current_index)
			self.current_index = len(SONG_LIST)-1

		# Updates current BPM box        
		self.listbox.select_set(self.current_index) 
		self.currentbpm = (SONG_LIST[self.current_index].bpm)
		pwm.ChangeFrequency(1/(60.0/self.currentbpm))
		self.CBPM.configure(text = "Current BPM: {}".format(self.currentbpm), fg = "black")
		self.serialize()

	# Next song method        
	def next_song(self):
		self.listbox.select_clear(self.current_index)
		self.current_index = self.current_index + 1 

		# Handles cycling from end to beginning of list
		if (self.current_index > len(SONG_LIST)-1):
			self.listbox.select_clear(self.current_index)
			self.current_index = 0

		# Updates current BPM box        
		self.listbox.select_set(self.current_index)
		self.currentbpm = (SONG_LIST[self.current_index].bpm)
		pwm.ChangeFrequency(1/(60.0/self.currentbpm))
		self.CBPM.configure(text = "Current BPM: {}".format(self.currentbpm), fg = "black")
		self.serialize()

	# Update current BPM from pedal taps
	def update_bpm(self, bpm):
		self.currentbpm=(bpm)
		pwm.ChangeFrequency(1/(60.0/bpm))
		self.CBPM.configure(text = "Current BPM: {}".format(self.currentbpm), fg = "red")
		self.serialize()

	def serialize(self):
		t.write("{},{},{},{}".format(SONG_LIST[self.current_index].song, self.currentbpm,\
			SONG_LIST[self.current_index].timeline, SONG_LIST[self.current_index].bigsky))

#########################################################################################################
# MAIN
#########################################################################################################s
# Parse .txt file song song information, and stong it in a dictionary
songDatabase()

# Create the window
window = Tk()
#window.title("Pi Pedaler")

pwm = GPIO.PWM(WOMB, 2)
pwm.start(90)

# Enable tx and rx pins
GPIO.output(ENABLE, GPIO.HIGH)

# Initialize translator
t = Translator()

# Create the GUI as a TKinter canvas inside the window
g = GUI(window)

bpmtoggle = False
bpmlast = 0
lastNextSong = 0
lastPrevSong = 0
debounce = 0
debounceClock = time.clock()
try:
	# Infinite loop listening for user input
	while 1:
		window.update()
		if (time.clock() - debounceClock > 0.25):
			debounce = 0

		b = GPIO.input(TAP) # Button state
		c = GPIO.input(NEXT_SONG) # Button state
		d = GPIO.input(LAST_SONG) # Button state 

		if (b == GPIO.HIGH and not bpmtoggle):
			bpmtoggle = True
			currbpm = time.clock()

			diff = currbpm - bpmlast
			if (diff >= 0.24):
				if (diff <= 1.5):
					tempo = 60/diff
					g.update_bpm(int(round(tempo)))

				bpmlast = currbpm

		elif (b == GPIO.LOW and bpmtoggle):
			bpmtoggle = False

		if (c == GPIO.HIGH and lastNextSong == 0 and debounce == 0):
			debounceClock = time.clock()
			debounce = 1
			g.next_song()
			lastNextSong = 1

		elif (c == GPIO.LOW and lastNextSong == 1):
			lastNextSong = 0

		elif (d == GPIO.HIGH and lastPrevSong == 0 and debounce == 0):
			debounceClock = time.clock()
			debounce = 1
			g.prev_song()
			lastPrevSong = 1

		elif (d == GPIO.LOW and lastPrevSong == 1):
			lastPrevSong = 0

except KeyboardInterrupt:
	GPIO.cleanup()
	exit()
