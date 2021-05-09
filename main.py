#!/usr/local/bin/python3.9

import time
from pynput import mouse
import tkinter as tk
import os
import threading

path = os.getcwd()
print("Current working directory is %s" % path)

settingsdict = {}

defaultValues = {
	"language" : "en_CA",
	"regclickinterval" : 10
}

lastActionTime = time.time()


def checknumeric(string):
	#print("Check if '%s' is integer" % string)
	if string == "":
		return False
	for char in string:
		if char not in "1234567890.":
			return False
	return True

def retrieveValue(key):
	try: return settingsdict[key]
	except KeyError:
		settingsdict[key] = defaultValues[key]

# Open configuration and load into settingsdict
print("Loading configuration...")
changed = 0
if os.path.isfile(path+ "/config.sav"):
	with open(path +"/config.sav","r") as cfg:
		for line in cfg:
			if line == "":
				print("Skipping empty line.")
				continue
			tmp = line.split("=")
			tmp[1] = tmp[1][:-1]
			if checknumeric(tmp[1]):
				#print("value is numeric")
				tmp[1] = float(tmp[1])
			settingsdict[tmp[0]] = tmp[1]
			print("Loaded '%s' into '%s'" % (tmp[1],tmp[0]))
			changed += 1
print("Configuration loaded. %i values initialized" % changed)

def save():
	with open(path + "/config.sav","w+") as cfg:
		global settingsdict
		cfg.truncate(0)
		for a in settingsdict.keys():
			if a == "":
				continue
			tstr = a + "=" + str(settingsdict[a])+"\n"
			#print("writing '%s'" % str(settingsdict[a]))
			cfg.write(tstr)

for x in defaultValues.keys():
	if x not in settingsdict:
		settingsdict[x] = defaultValues[x]

def onMouseAction(*args):
	global lastActionTime
	lastActionTime = time.time()
	#print("Inactivity timer has been reset.")


toggle = False
threadactive = False
widget = tk.Tk()

activity = tk.Label(text="Status: Standby", background="gray")
inactiveTL = tk.Label(text="Time Inactive: 0", background="yellow")
btn = tk.Button(text="Start")
cspd = tk.Entry()

def entryReset(num):
	cspd.delete(0,tk.END)
	cspd.insert(0,str(num))

entryReset(settingsdict["regclickinterval"])

def toggleThread(event):
	#print("the button was clicked!")
	global toggle
	global threadactive
	if not toggle and not threadactive:
		if not checknumeric(cspd.get()):
			activity["text"] = "Error: Invalid Time"
			activity["background"] = "red"
			entryReset(settingsdict["regclickinterval"])
			return
		settingsdict["regclickinterval"] = float(cspd.get())
		threadactive = True
		activity["text"] = "Status: Running"
		activity["background"] ="green"
		btn["text"] = "Stop"
		ms = threading.Thread(target=autoThread,daemon=True)
		ms.start()
	toggle = not toggle


btn.bind("<Button-1>", toggleThread)


btn.pack()
cspd.pack()
activity.pack()
inactiveTL.pack()




def autoThread():
	global toggle
	global lastActionTime
	global threadactive
	controller = mouse.Controller()
	tracker = mouse.Listener(on_click = onMouseAction)
	tracker.start()
	print("Tracker has started!")
	lastActionTime = time.time()
	while toggle:
		time.sleep(1)
		a = time.time()-lastActionTime
		#print("Click Duration: %d" % a, end = "\r")
		inactiveTL["text"] = "Inactive for: {0}:{1}:{2}".format(
			int(a // 3600),
			int(a // 60),
			str(int(a % 60))
		)

		if time.time()-lastActionTime > settingsdict["regclickinterval"]:
			#print("You haven't clicked in a while. Clicking!")
			controller.click(mouse.Button.left,1)
	inactiveTL["text"] = "Inactive for: 0:0:0"
	print("Waiting for tracker to stop...")
	tracker.stop()
	threadactive = False
	activity["text"] = "Status: Standby"
	activity["background"] = "gray"
	btn["text"] = "Start"
	print("Tracker has stopped.")

widget.mainloop()
print("Saving...")
save()
print("Thank you for using pyautoclicker.")









