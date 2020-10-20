import sys
import os
import math
import time
import json
import logging
import getpass
import subprocess
import threading
import shutil
import socket
from datetime import datetime
import pystray
from PIL import Image, ImageDraw

# settings
serverIP='192.168.1.8' # has to be a string
serverPort=90 		   # has to be integer
rate=30.0              # integer in seconds

# paths
defaultPath=os.path.dirname(os.path.realpath(__file__)) #  to force the location os.path.expanduser('~/ServerAlive/')
iconsPath=os.path.join(defaultPath,'icons')
eOS_iconPath=os.path.expanduser('~/.local/share/icons/')

# filenames
filename=os.path.splitext(os.path.basename(__file__))[0]
defaultConfigFile='config.json'
defaultLogginFile=filename+'.log'# to force a logging name 'midi2vol.log'
iconCon_img='ServerAlive.png'
iconDis_img='ServerDead.png'
iconLoa_img='ServerLoad.png'

# flags
tray = False
debug = False
elementaryOS=False
noNotify = False
notifiedAlive=False
notifiedDead=False

def trayIcon(icon_img):
	global icon
	width=12
	height=12
	image=Image.open(icon_img)
	icon=pystray.Icon(filename, image)
	return icon


def eOSNotification(defaultPath,eOS_iconPath,iconCon_img,iconDis_img):
	global elementaryOS
	elementaryOS = True
	if os.path.isfile(os.path.join(eOS_iconPath,iconCon_img)) == False:
		shutil.copyfile(os.path.join(iconsPath,iconCon_img), os.path.join(eOS_iconPath,iconCon_img))
	if os.path.isfile(os.path.join(eOS_iconPath,iconDis_img)) == False:
		shutil.copyfile(os.path.join(iconsPath,iconDis_img), os.path.join(eOS_iconPath,iconDis_img))


def sendmessage(status,icon):
	global image,tray
	if(noNotify):
		return
	text=''
	iconCon = os.path.join(iconsPath,iconCon_img)
	iconDis = os.path.join(iconsPath,iconDis_img)

	if(status == True):
		image=Image.open(iconCon)
		icon.icon = image
		text='Server is Alive'
		img = iconCon
		if(elementaryOS):
			img= os.path.splitext(iconCon_img)[0]

	elif(status == False):
		image=Image.open(iconDis)
		icon.icon = image
		text='Server is Dead'
		img = iconDis
		if(elementaryOS):
			img= os.path.splitext(iconDis_img)[0]

	subprocess.Popen(["notify-send", "-i", img, filename, text])
	return

def isAlive():
	global icon,notifiedAlive,notifiedDead,rate
	threading.Timer(rate, isAlive).start()
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex((serverIP, serverPort))
	if result == 0:
		logging.warning("Server is alive")
		if(notifiedAlive==False):
			sendmessage(True,icon)
			notifiedAlive=True
			notifiedDead=False
	else:
		logging.warning("Server is dead")
		if(notifiedDead==False):
			sendmessage(False,icon)
			notifiedAlive=False
			notifiedDead=True
	sock.close()

def main():
	argv = sys.argv
	count=0
	for arg in argv:
		if(arg == '-r' or arg == '--rate'):
			global rate
			rate = argv[count+1]
		if(arg == '--port' or arg == '-p'):
			global serverPort
			serverPort = int(argv[count+1])
		if(arg == '--ip' or arg == '-i'):
			global serverIP
			serverIP = argv[count+1]
		if(arg == '--noicon'):
			global noNotify
			noNotify = True
		if(arg == "-e"):
			eOSNotification(iconsPath,eOS_iconPath,iconCon_img,iconDis_img)
		if(arg == "-d"):
			global debug
			debug = True
			logging.basicConfig(filename=os.path.join(defaultPath,defaultLogginFile),level=logging.WARNING)
			logging.warning('----------------------------')
			logging.warning(datetime.now())
			logging.warning('----------------------------')
			logging.warning(getpass.getuser())
			logging.warning('----------------------------')
		count=count+1
	try:
		if(debug == True):
			logging.warning(argv)
			logging.warning('----------------------------')
		global icon
		icon = trayIcon(os.path.join(iconsPath,iconLoa_img))
		isAlive()
		icon.run()

	except:
		icon.visible = False
		icon.stop()
		sys.exit("Error, check log")  

if __name__== "__main__":
  	main()


