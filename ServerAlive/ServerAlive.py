import argparse
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
defaultLogginFile=filename+'.log'# to force a logging name 'ServerAlive.log'
iconCon_img='ServerAlive.png'
iconDis_img='ServerDead.png'
iconLoa_img='ServerLoad.png'
iconCon_tray='TrayWhiteIconAlive.png'
iconDis_tray='TrayWhiteIconDead.png'
iconLoa_tray='TrayWhiteIconLoad.png'

# flags
tray = False
debug = False
elementaryOS=False
noNotify = False
notifiedAlive=False
notifiedDead=False



def trayIcon(icon_img):
	global icon
	image=Image.open(os.path.join(iconsPath,icon_img))
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
	iconConTray = os.path.join(iconsPath,iconCon_tray)
	iconDisTray = os.path.join(iconsPath,iconDis_tray)

	if(status == True):
		image=Image.open(iconConTray)
		icon.icon = image
		text='Server is Alive'
		img = iconCon
		if(elementaryOS):
			img= os.path.splitext(iconCon_img)[0]

	elif(status == False):
		image=Image.open(iconDisTray)
		icon.icon = image
		text='Server is Dead'
		img = iconDis
		if(elementaryOS):
			img= os.path.splitext(iconDis_img)[0]

	subprocess.Popen(['notify-send', '-i', img, filename, text])
	return

def isAlive():
	global icon,notifiedAlive,notifiedDead,rate
	threading.Timer(rate, isAlive).start()
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex((serverIP, serverPort))
	if result == 0:
		logging.warning('Server is alive')
		if(notifiedAlive==False):
			sendmessage(True,icon)
			notifiedAlive=True
			notifiedDead=False
	else:
		logging.warning('Server is dead')
		if(notifiedDead==False):
			sendmessage(False,icon)
			notifiedAlive=False
			notifiedDead=True
	sock.close()

def main():
	global rate,debug,serverPort,serverIP,noNotify,defaultLogginFile
	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument('-r','--rate',type=int,nargs='?',help='Sets the rate in which the server is checked', default=rate)
	parser.add_argument('-p','--port',type=int,nargs='?',help='Sets the port in which the server is checked',default=serverPort)
	parser.add_argument('-i','--ip',type=str,nargs='?',help='Sets the ip in which the server is checked',default=serverIP)
	parser.add_argument('-d', type =str,nargs='?',help='Debug file,if name provided in that file',default=False,const=defaultLogginFile)
	parser.add_argument('--noicon', help='No notification is produced',action='store_true')
	parser.add_argument('-e', help='Just for elementaryOS,makes icons work',action='store_true')
	

	args = parser.parse_args()
	if args.d:
		debug = True
		defaultLogginFile= args.d
		logging.basicConfig(filename=os.path.join(defaultPath,defaultLogginFile),level=logging.DEBUG)
		logging.warning('----------------------------')
		logging.warning(datetime.now())
		logging.warning('----------------------------')
		logging.warning(getpass.getuser())
		logging.warning('----------------------------')
	if args.rate:
		rate = args.rate
	if args.port:
		serverPort = args.port
	if args.ip:
		serverIP = args.ip
	if args.noicon:
		noNotify = True
	if args.e:
		eOSNotification(iconsPath,eOS_iconPath,iconCon_img,iconDis_img)

	try:
		global icon
		icon = trayIcon(os.path.join(iconsPath,iconLoa_tray))
		isAlive()
		icon.run()

	except:
		icon.visible = False
		icon.stop()
		sys.exit("Error, check log")  


if __name__== '__main__':
  	main()




