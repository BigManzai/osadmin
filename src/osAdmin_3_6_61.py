#!/usr/bin/python3
# OpenSim Remoteadmin
# Python 3.6 - 2018 by Manfred Aabye Version  3.6.61

# import library
import idlelib
import sys
import os

import xmlrpc.client
from ftplib import FTP
from ftplib import FTP_TLS
import webbrowser
import telnetlib
import configparser
from appJar import gui
from tkinter import *
import tkinter as tk
import tkinter.filedialog
from tkinter.filedialog import askopenfilename, asksaveasfilename
import tkinter.messagebox
from tkinter.colorchooser import askcolor
import tkinter.scrolledtext as tkst
import datetime
from PIL import Image, ImageTk
import tarfile

import osAdmin_help
import oscommands

# import gettext
# gettext.bindtextdomain('OpenSimRemote', '/language')
# gettext.textdomain('OpenSimRemote')
# _ = gettext.gettext
# // gettext einfügen funktioniert so:
# // print(_('This is a translatable string.'))

def line():
    lin = "_" * 60
    text.insert(INSERT,lin)
    
def date():
    data = datetime.date.today()
    text.insert(INSERT,data)
   
def normal():
    text.config(font = ("Arial", 10))

def bold():
    text.config(font = ("Arial", 10, "bold"))

def underline():
    text.config(font = ("Arial", 10, "underline"))

def italic():
    text.config(font = ("Arial",10,"italic"))

def font():
    (triple,color) = askcolor()
    if color:
       text.config(foreground=color)

def kill():
    root.destroy()

def about():
	pass

def opn():
    text.delete(1.0 , END)
    file = open(askopenfilename() , 'r')
    if file != '':
        txt = file.read()
        text.insert(INSERT,txt)
    else:
        pass

def save():
    filename = asksaveasfilename()
    if filename:
        alltext = text.get(1.0, END)                      
        open(filename, 'w').write(alltext) 

def copy():
    text.clipboard_clear()
    text.clipboard_append(text.selection_get()) 

def paste():
    try:
        teext = text.selection_get(selection='CLIPBOARD')
        text.insert(INSERT, teext)
    except:
        tkinter.messagebox.showerror("Errore","Gli appunti sono vuoti!")

def clear():
    sel = text.get(SEL_FIRST, SEL_LAST)
    text.delete(SEL_FIRST, SEL_LAST)

def clearall():
    text.delete(1.0 , END)

def background():
    (triple,color) = askcolor()
    if color:
       text.config(background=color)

def showTexture(self):
	load = Image.open("PyOpensimulatorAdmin512.png")
	render = ImageTk.PhotoImage(load)

	# labels can be text or images
	img = Label(self, image=render)
	img.image = render
	img.place(x=0, y=0)
		
# --------- ftp ---------------------------------
def ftpupload():
#In der Datei vsftpd.conf muss folgendes geändert werden: von pam_service_name=vsftpd auf pam_service_name=ftp
	config = configparser.ConfigParser()
	config.sections()
	config.read('osconfig.ini')
	ftpAdress = config['FTPSERVER']['ftpAdress']
	ftpuser = config['FTPSERVER']['ftpuser']
	ftppass = config['FTPSERVER']['ftppass']
	ftpdirectory = config['FTPSERVER']['ftpdirectory']

	tclconsole.raw_filename = tkinter.filedialog.askopenfilename()

	ftp=FTP_TLS()
	ftp.set_debuglevel(2)
	ftp.connect(ftpAdress)
	ftp.sendcmd('USER ' + ftpuser)
	ftp.sendcmd('PASS ' + ftppass)

	#ftp.cwd("/home") # Verzeichnis wechseln
	ftp.cwd(ftpdirectory) # Verzeichnis wechseln
	
	ftp.set_pasv(False)
	file_name = tclconsole.raw_filename
	file = open(file_name, 'rb')
	ftp.storbinary('STOR ' + file_name, file)
	file.quit()

	ftp.close()
	
# --------- ftp Ende---------------------------------

# --------- telnet Konsole -------------------------
def telnetkonsole():
	# Fenstername tclconsole
	
	config = configparser.ConfigParser()
	config.sections()
	config.read('osconfig.ini')
	Telnetadress = config['TELNET']['Telnetadress']
	Telnetuser = config['TELNET']['Telnetuser']
	Telnetpass = config['TELNET']['Telnetpass']
	ftpdirectory = config['TELNET']['Telnetdirectory']
	
	# Konfigurationsdaten Ende
	
	tclconsolenausgabe = "server@prompt/>"
	tclconsole.insert(INSERT,tclconsolenausgabe)

	password = Telnetpass

	tn = telnetlib.Telnet(Telnetadress)

	tn.read_until(b"login: ")
	tn.write(Telnetuser.encode('ascii') + b"\n")
	if password:
		tn.read_until(b"Password: ")
		tn.write(password.encode('ascii') + b"\n")

	tn.write(b"ls\n")
	tn.write(b"exit\n")

	print(tn.read_all().decode('ascii'))
	
# --------- telnet Ende ---------------------------------

# -----------------------------   OAR Informationen   ------------------------------------
def OARInformation():
	oar = tarfile.open(tkinter.filedialog.askopenfilename())

	generalContents = { 
		'Assets' : 0, 
		'Scene objects' : 0 
	}

	assetFileExtToKey = {
		'animation.bvh' : 'Animations',
		'bodypart.txt' : 'Bodyparts',
		'callingcard.txt' : 'Calling cards',
		'clothing.txt' : 'Clothing',
		'gesture.txt' : 'Gestures',
		'image.jpg' : 'Images JPEG',
		'image.tga' : 'Images TGA',
		'landmark.txt' : 'Landmarks',
		'material.xml' : 'Materials',
		'mesh.llmesh' : 'Mesh',
		'notecard.txt' : 'Notecards',
		'script.lsl' : 'Scripts',
		'object.xml' : 'Serialized objects',
		'sound.ogg' : 'Sounds OGG',
		'sound.wav' : 'Sounds WAV',
		'texture.jp2' : 'Textures JP2',
		'texture.png' : 'Textures PNG',
		'texture.tga' : 'Textures TGA'
	}

	assetContents = { 'Unknown' : 0 }

	for value in list(assetFileExtToKey.values()):
		assetContents[value] = 0
		

	for name in oar.getnames():
		if name.startswith("objects/"):
			generalContents['Scene objects'] += 1
		elif name.startswith("assets/"):
			generalContents['Assets'] += 1
			
			assetExt = name.split("_")[-1]
			
			if assetExt in assetFileExtToKey:
				assetContentsKey = assetFileExtToKey[assetExt]
				assetContents[assetContentsKey] += 1
				

	# Print results of analysis
	longestKey = max(list(generalContents.keys()) + list(assetContents.keys()), key = len)
		   
	for type, count in generalContents.items():
		#print("%-*s: %s" % (len(longestKey), type, count))
		txt1 = "%-*s: %s\n" % (len(longestKey), type, count)
		text.insert(INSERT,txt1,"\n")

	#print("\nAssets Composition:")
	text.insert(INSERT,"\nAssets Composition:\n")

	for type, count in assetContents.items():
		#print("%-*s: %s" % (len(longestKey), type, count))
		txt2 = "%-*s: %s\n" % (len(longestKey), type, count)
		text.insert(INSERT,txt2,"\n\n\n\n\n")
	
# -----------------------------   OAR Informationen   ------------------------------------


# -----------------------------   broadcast   ---------------------------------------------
def broadcastapp():

	# Button Auswertung
	def broadcastbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.\nDas Edit Fenster funktioniert wie eine Textverarbeitung.\nErst nach dem klick auf Senden wird die Nachricht abgesendet.\nMaximum an Zeichen: 254.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			RegionMessage = app.getTextArea('RegionMessage')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_broadcast({'password': ConsolePass, 'message': RegionMessage})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("Admin Broadcast", "255x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("Nachricht")

	# Nachrichten Text Abfragen
	app.addTextArea("RegionMessage")

	# Buttons ruft die Function broadcastbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], broadcastbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()
	
# -----------------------------   broadcast  ENDE   ---------------------------------------------
# -----------------------------   authenticateuser   ---------------------------------------------
	
def authenticateuser():

	# Button Auswertung
	def authenticbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			user_firstname = app.getEntry('user_firstname')
			user_lastname = app.getEntry('user_lastname')
			user_password = app.getEntry('user_password')
			token_lifetime = app.getEntry('token_lifetime')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_authenticate_user({'password':ConsolePass,'user_firstname':user_firstname,'user_lastname':user_lastname,'user_password':user_password,'token_lifetime':token_lifetime})
			return



	# Erstelle GUI Variablen Aufruf mit app
	app = gui("Admin Broadcast", "405x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("Authenticate User")

	# Nachrichten Text Abfragen
	app.addLabelEntry("user_firstname")
	app.addLabelEntry("user_lastname")
	app.addLabelSecretEntry("user_password")
	app.addLabelEntry("token_lifetime")

	# Buttons ruft die Function authenticbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], authenticbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()

# -----------------------------   authenticateuser  ENDE   ---------------------------------------------
# -----------------------------   closeregion   ---------------------------------------------
	
def closeregion():

	# Button Auswertung
	def closeregionbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_close_region({'password':ConsolePass,'region_name':region_name})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("Close Region", "355x120") # Fenster erstellen mit Namen und Groesse
	app.setBg("red")
	app.setFont(12) # Textgroesse
	app.startLabelFrame("Close Region")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")

	# Buttons ruft die Function closeregionbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], closeregionbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()
	
# -----------------------------   closeregion  ENDE   ---------------------------------------------
# -----------------------------   createregion   ---------------------------------------------	

def createregion():

	# Button Auswertung
	def createregionbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			listen_ip = app.getEntry('listen_ip')
			listen_port = app.getEntry('listen_port')
			external_address = app.getEntry('external_address')
			region_x = app.getEntry('region_x')
			region_y = app.getEntry('region_y')
			estate_name = app.getEntry('estate_name')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_create_region({'password':ConsolePass,'region_name':region_name,'listen_ip':listen_ip,'listen_port':listen_port,'external_address':external_address,'region_x':region_x,'region_y':region_y,'estate_name':estate_name})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("create Region", "355x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("create region")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")
	app.addLabelEntry("listen_ip")
	app.addLabelEntry("listen_port")
	app.addLabelEntry("external_address")
	app.addLabelEntry("region_x")
	app.addLabelEntry("region_y")
	app.addLabelEntry("estate_name")

	# Buttons ruft die Function createregionbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], createregionbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()

# -----------------------------   createregion  ENDE   ---------------------------------------------
# -----------------------------   createuser   ---------------------------------------------
def createuser():

	# Button Auswertung
	def createuserbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			user_firstname = app.getEntry('user_firstname')
			user_lastname = app.getEntry('user_lastname')
			user_password = app.getEntry('user_password')
			start_region_x = app.getEntry('start_region_x')
			start_region_y = app.getEntry('start_region_y')
			user_email = app.getEntry('user_email')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_create_user({'password':ConsolePass,'user_firstname':user_firstname,'user_lastname':user_lastname,'user_password':user_password,'start_region_x':start_region_x,'start_region_y':start_region_y,'user_email':user_email})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("create user", "355x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("create user")

	# Nachrichten Text Abfragen
	app.addLabelEntry("user_firstname")
	app.addLabelEntry("user_lastname")
	app.addLabelSecretEntry("user_password")
	app.addLabelEntry("start_region_x")
	app.addLabelEntry("start_region_y")
	app.addLabelEntry("user_email")

	# Buttons ruft die Function createuserbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], createuserbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()

# -----------------------------   createuser  ENDE   ---------------------------------------------
# -----------------------------   deleteregion   ---------------------------------------------
def deleteregion():

	# Button Auswertung
	def deleteregionbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_delete_region({'password':ConsolePass,'region_name':region_name})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("delete Region", "355x160") # Fenster erstellen mit Namen und Groesse
	app.setBg("red")
	app.setFont(12) # Textgroesse
	app.startLabelFrame("delete region")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")

	# Buttons ruft die Function deleteregionbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], deleteregionbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()

# -----------------------------   deleteregion  ENDE   ---------------------------------------------
# -----------------------------   estatereload   ---------------------------------------------

def estatereload():

	# Button Auswertung
	def estatereloadbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']

			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_estate_reload({'password':ConsolePass})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("Estate Reload", "490x140") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("Estate Reload")

	# Nachrichten Text Abfragen
	app.addLabel("title", "Estate Reload hat keine weiteren Einstellungen.")

	# Buttons ruft die Function estatereloadbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], estatereloadbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()

# -----------------------------   estatereload  ENDE   ---------------------------------------------
# -----------------------------   existsuser   ---------------------------------------------

def existsuser():

	# Button Auswertung
	def existsuserbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			user_firstname = app.getEntry('user_firstname')
			user_lastname = app.getEntry('user_lastname')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_exists_user({'password':ConsolePass,'user_firstname':user_firstname,'user_lastname':user_lastname})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("Exists User", "305x160") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("Exists User")

	# Nachrichten Text Abfragen
	app.addLabelEntry("user_firstname")
	app.addLabelEntry("user_lastname")

	# Buttons ruft die Function existsuserbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], existsuserbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()

# -----------------------------   existsuser  ENDE   ---------------------------------------------
# -----------------------------   getagents   ---------------------------------------------
	
def getagents():

	# Button Auswertung
	def getagentsbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			Regions_ID = app.getEntry('Regions_ID')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_get_agents({'password':ConsolePass,'region_name':region_name,'Regions-ID':Regions_ID})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("get agents", "305x160") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("get agents")

	# Nachrichten Text Abfragen
	app.addLabelEntry("user_firstname")
	app.addLabelEntry("user_lastname")

	# Buttons ruft die Function getagentsbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], getagentsbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()
	
# -----------------------------   getagents  ENDE   ---------------------------------------------
# -----------------------------   loadheightmap   ---------------------------------------------
def loadheightmap():

	# Button Auswertung
	def loadheightmapbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			filename = app.openBox(title=None, dirName=None, fileTypes=None, asFile=False, parent=None)
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_load_heightmap({'password': ConsolePass,'region_name': region_name,'filename': filename})
			print(filename)
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("load heightmap", "305x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("load heightmap")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")

	# Buttons ruft die Function loadheightmapbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], loadheightmapbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	

# -----------------------------   loadheightmap  ENDE   ---------------------------------------------
# -----------------------------   loadxml   ---------------------------------------------	
def loadxml():

	# Button Auswertung
	def loadxmlbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			filename = app.openBox(title=None, dirName=None, fileTypes=[('xml', '*.xml')], asFile=False, parent=None)
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_load_xml({'password': ConsolePass,'region_name':region_name,'filename': filename})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("load xml", "305x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("load xml")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")

	# Buttons ruft die Function loadxmlbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], loadxmlbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()
	
# -----------------------------   loadxml  ENDE   ---------------------------------------------
# -----------------------------   loadoar   ---------------------------------------------
def loadoar():

	# Button Auswertung
	def loadoarbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			filename = app.openBox(title=None, dirName=None, fileTypes=[('oar', '*.oar')], asFile=False, parent=None)
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_load_oar({'password': ConsolePass,'region_name':region_name,'filename': filename})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("load oar", "305x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("load oar")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")

	# Buttons ruft die Function loadoarbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], loadoarbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	
	
# -----------------------------   loadoar  ENDE   ---------------------------------------------
# -----------------------------   modifyregion   ---------------------------------------------
def modifyregion():

	# Button Auswertung
	def modifyregionbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_modify_region({'password':ConsolePass,'region_name':region_name})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("modify region", "305x160") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("modify region")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")

	# Buttons ruft die Function modifyregionbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], modifyregionbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	
	
# -----------------------------   modifyregion  ENDE   --------------------------------------
# -----------------------------   regionquery   ---------------------------------------------
def regionquery():

	# Button Auswertung
	def regionquerybutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_region_query({'password':ConsolePass,'region_name':region_name})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("region query", "305x160") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("region query")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")

	# Buttons ruft die Function regionquerybutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], regionquerybutton)
	app.stopLabelFrame()
	# start GUI
	app.go()
	
# -----------------------------   regionquery  ENDE   --------------------------------------
# -----------------------------   regionrestart   ---------------------------------------------
def regionrestart():

	# Button Auswertung
	def regionrestartbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_id = app.getEntry('region_id')
			
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_restart({'password':ConsolePass,'region_id':region_id})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("region restart", "305x160") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("region restart")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_id")

	# Buttons ruft die Function regionrestartbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], regionrestartbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()


# -----------------------------   regionrestart  ENDE   --------------------------------------
# -----------------------------   saveheightmap   ---------------------------------------------
def saveheightmap():

	# Button Auswertung
	def saveheightmapbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			filename = app.openBox(title=None, dirName=None, fileTypes=None, asFile=False, parent=None)
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_save_heightmap({'password': ConsolePass,'region_name':region_name,'filename': filename})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("save heightmap", "305x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("save heightmap")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")

	# Buttons ruft die Function saveheightmapbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], saveheightmapbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	



# -----------------------------   saveheightmap  ENDE   --------------------------------------
# -----------------------------   saveoar   ---------------------------------------------

def saveoar():

	# Button Auswertung
	def saveoarbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			filename = app.saveBox(title=None, fileName=None, dirName=None, fileExt=".oar", fileTypes=None, asFile=None, parent=None)
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_save_oar({'password': ConsolePass,'region_name':region_name,'filename': filename})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("save oar", "305x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("save oar")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")

	# Buttons ruft die Function saveoarbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], saveoarbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	


# -----------------------------   saveoar  ENDE   --------------------------------------
# -----------------------------   savexml   ---------------------------------------------

def savexml():

	# Button Auswertung
	def savexmlbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			region_name = app.getEntry('region_name')
			filename = app.saveBox(title=None, fileName=None, dirName=None, fileExt=".xml", fileTypes=None, asFile=None, parent=None)
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_save_xml({'password': ConsolePass,'region_name':region_name,'filename': filename})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("save xml", "305x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("save xml")

	# Nachrichten Text Abfragen
	app.addLabelEntry("region_name")

	# Buttons ruft die Function savexmlbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], savexmlbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	
# -----------------------------   savexml ENDE  ---------------------------------------------
# -----------------------------   adminshutdown   ---------------------------------------------

def adminshutdown():

	# Button Auswertung
	def adminshutdownbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			milliseconds = app.getEntry('milliseconds')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_shutdown({'password':ConsolePass,'milliseconds':milliseconds})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("Shutdown", "305x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("Shutdown")

	# Nachrichten Text Abfragen
	app.addLabelEntry("milliseconds")

	# Buttons ruft die Function adminshutdownbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], adminshutdownbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	


# -----------------------------   adminshutdown  ENDE   --------------------------------------
	
# -----------------------------   teleportagent   ---------------------------------------------

def teleportagent():

	# Button Auswertung
	def teleportagentbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			agent_first_name = app.getEntry('agent_first_name')
			agent_last_name = app.getEntry('agent_last_name')
			region_name = app.getEntry('region_name')
			pos_x = app.getEntry('pos_x')
			pos_y = app.getEntry('pos_y')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_teleport_agent({'password':ConsolePass,'agent_first_name':agent_first_name,'agent_last_name':agent_last_name,'region_name':region_name, 'pos_x':pos_x, 'pos_y':pos_y})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("teleport agent", "355x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("teleport agent")

	# Nachrichten Text Abfragen
	app.addLabelEntry("agent_first_name")
	app.addLabelEntry("agent_last_name")
	app.addLabelEntry("region_name")
	app.addLabelEntry("pos_x")
	app.addLabelEntry("pos_y")

	# Buttons ruft die Function teleportagentbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], teleportagentbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	


# -----------------------------   teleportagent  ENDE   --------------------------------------

# -----------------------------   updateuser   ---------------------------------------------

def updateuser():

	# Button Auswertung
	def updateuserbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die osconfig.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			user_firstname = app.getEntry('user_firstname')
			user_lastname = app.getEntry('user_lastname')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_update_user({'password':ConsolePass,'user_firstname':user_firstname,'user_lastname':user_lastname})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("update user", "305x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("update user")

	# Nachrichten Text Abfragen
	app.addLabelEntry("user_firstname")
	app.addLabelEntry("user_lastname")

	# Buttons ruft die Function updateuserbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], updateuserbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	


# -----------------------------   updateuser  ENDE   --------------------------------------

# -----------------------------   updateini   ---------------------------------------------

def updateini():

	# Button Auswertung
	def updateinibutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Setzt Ihre Server Daten in die osconfig.ini ein.")
			return
		if button == "Save":

			user_SimulatorAdress = app.getEntry('SimulatorAdress')
			user_ConsoleUser = app.getEntry('ConsoleUser')
			user_ConsolePass = app.getEntry('ConsolePass')
			
			parser = configparser.RawConfigParser()

			# Bitte beachten Sie, dass Sie mit den Set-Funktionen von RawConfigParser intern Schlüsseln Nicht-String-Werte zuweisen können, 
			# aber einen Fehler erhalten, wenn Sie versuchen, in eine Datei zu schreiben oder wenn Sie sie im nicht-raw-Modus bekommen. 
			# Das Festlegen von Werten mit dem Mapping-Protokoll oder dem set () von ConfigParser lässt solche Zuordnungen nicht zu.
			#parser.add_section('Default')
			parser.set('DEFAULT', 'SimulatorAdress', user_SimulatorAdress)
			parser.set('DEFAULT', 'ConsoleUser', user_ConsoleUser)
			parser.set('DEFAULT', 'ConsolePass', user_ConsolePass)
			# Schreibt die Werte nicht
			parser.write(sys.stdout)
			# Writing our configuration file to 'osconfig.ini'
			with open('osconfig.ini', 'w') as configfile:
				parser.write(configfile)
			
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("Config Editor", "355x260") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("Config Edit")

	# Nachrichten Text Abfragen
	app.addLabelEntry("SimulatorAdress")
	app.addLabelEntry("ConsoleUser")
	app.addLabelEntry("ConsolePass")

	# Buttons ruft die Function updateinibutton auf
	app.addButtons(["Save", "Hilfe", "Ende"], updateinibutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	


# -----------------------------   updateini  ENDE   --------------------------------------

# -----------------------------   consolecommand   ---------------------------------------------

def consolecommand():

	# Button Auswertung
	def consolecommandbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Hier können sie je nach freigabe in der Opensim.ini Konsolen Befehle ausführen lassen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('osconfig.ini')
			SimulatorAdress = config['DEFAULT']['SimulatorAdress']
			ConsoleUser = config['DEFAULT']['ConsoleUser']
			ConsolePass = config['DEFAULT']['ConsolePass']
			console_command = app.getEntry('console_command')
			Simulator = xmlrpc.client.Server(SimulatorAdress)
			Simulator.admin_console_command({'password': ConsolePass,'command': console_command})
			return


	# Erstelle GUI Variablen Aufruf mit app
	app = gui("Console Command", "600x200") # Fenster erstellen mit Namen und Groesse
	app.setFont(12) # Textgroesse
	app.startLabelFrame("Console Command")
	app.config(bg="orange")

	# Nachrichten Text Abfragen
	app.addLabelEntry("console_command")

	# Buttons ruft die Function consolecommandbutton auf
	app.addButtons(["Senden", "Hilfe", "Ende"], consolecommandbutton)
	app.stopLabelFrame()
	# start GUI
	app.go()	

# -----------------------------   consolecommand  ENDE   --------------------------------------

# Hauptmenue
def donothing():
   filewin = Toplevel(root)
   button = Button(filewin, text="Do nothing button")
   button.pack()

# -----------------------------   help   ---------------------------------------------



# -----------------------------   help  ENDE   --------------------------------------
   
root = Tk()

# --------------------------   Menu start
menubar = Menu(root)
configmenu = Menu(menubar, tearoff = 0)
configmenu.add_command(label = "Öffnen", command = opn)
#configmenu.add_command(label = "Speichern", command = save)
configmenu.add_command(label = "Speichern als...", command = save)
configmenu.add_command(label = "Datei schließen", command = clearall)
configmenu.add_separator()
configmenu.add_command(label = "Beenden", command = root.quit)
menubar.add_cascade(label = "Datei", menu = configmenu)

modmenu = Menu(menubar, tearoff=0)
modmenu.add_command(label="Kopieren", command = copy)
modmenu.add_command(label="Einfügen", command=paste)
modmenu.add_separator()
modmenu.add_command(label = "Löschen", command = clear)
modmenu.add_command(label = "Lösche alles", command = clearall)
menubar.add_cascade(label = "Bearbeiten", menu = modmenu)

insmenu = Menu(menubar, tearoff=0)
insmenu.add_command(label="Datum einfügen",command=date)
insmenu.add_command(label="Linie einfügen",command=line)
menubar.add_cascade(label = "Einfügen", menu = insmenu)

formatmenu = Menu(menubar, tearoff=0)
formatmenu.add_cascade(label="Schriftfarbe", command = font)
formatmenu.add_command(label="Hintergrundfarbe", command=background)
formatmenu.add_separator()
formatmenu.add_radiobutton(label='Normal',command=normal)
formatmenu.add_radiobutton(label='Fett',command=bold)
formatmenu.add_radiobutton(label='Unterstrichen',command=underline)
formatmenu.add_radiobutton(label='Italic',command=italic)
menubar.add_cascade(label="Schrift",menu = formatmenu)

agentmenu = Menu(menubar, tearoff=0)
agentmenu.add_command(label = "Teleportiere Benutzer", command = teleportagent)
#agentmenu.add_command(label = "get agents", command = getagents)
menubar.add_cascade(label = "Avatare", menu = agentmenu)

#accountmenu = Menu(menubar, tearoff=0)
#accountmenu.add_command(label = "create user", command = createuser)
#accountmenu.add_command(label = "create user_email", command = createuser)
#accountmenu.add_command(label = "exists user", command = existsuser)
#accountmenu.add_command(label = "update user", command = updateuser)
#accountmenu.add_command(label = "authenticate user", command = authenticateuser)
#menubar.add_cascade(label = "Account", menu = accountmenu)

regionmenu = Menu(menubar, tearoff=0)
regionmenu.add_command(label = "Nachricht senden", command = broadcastapp)
regionmenu.add_command(label = "Region schließen", command = closeregion)
#regionmenu.add_command(label = "create region", command = createregion)
regionmenu.add_command(label = "Region löschen", command = deleteregion)
regionmenu.add_command(label = "Region modifizieren", command = modifyregion)
#regionmenu.add_command(label = "region query", command = regionquery)
#regionmenu.add_command(label = "region restart", command = regionrestart)

menubar.add_cascade(label = "Region", menu = regionmenu)

#filemenu = Menu(menubar, tearoff=0)
#filemenu.add_command(label = "load heightmap", command = loadheightmap)
#filemenu.add_command(label = "load oar", command = loadoar)
#filemenu.add_command(label = "load xml", command = loadxml)
#filemenu.add_separator()
#filemenu.add_command(label = "save heightmap", command = saveheightmap)
#filemenu.add_command(label = "save oar", command = saveoar)
#filemenu.add_command(label = "save xml", command = savexml)
#menubar.add_cascade(label = "File", menu = filemenu)

#accessmenu = Menu(menubar, tearoff=0)
#accessmenu.add_command(label = "acl list", command = donothing)
#accessmenu.add_command(label = "acl clear", command = donothing)
#accessmenu.add_command(label = "acl add", command = donothing)
#accessmenu.add_command(label = "acl remove", command = donothing)
#menubar.add_cascade(label = "Access", menu = accessmenu)

estatemenu = Menu(menubar, tearoff=0)
estatemenu.add_command(label = "Estate neu laden", command = estatereload)
menubar.add_cascade(label = "Estate", menu = estatemenu)

adminmenu = Menu(menubar, tearoff=0)
adminmenu.add_command(label = "Konsolenbefehl", command = consolecommand)
adminmenu.add_command(label = "OpenSim herunterfahren", command = adminshutdown)
menubar.add_cascade(label = "Admin", menu = adminmenu)

#miscmenu = Menu(menubar, tearoff=0)
#miscmenu.add_command(label = "dialog", command = donothing)
#miscmenu.add_command(label = "reset land", command = donothing)
#miscmenu.add_command(label = "refresh search", command = donothing)
#miscmenu.add_command(label = "refresh map", command = donothing)
#miscmenu.add_command(label = "opensim version", command = donothing)
#miscmenu.add_command(label = "agent count", command = donothing)
#menubar.add_cascade(label = "Misc", menu = miscmenu)

persomenu = Menu(menubar, tearoff=0)
persomenu.add_command(label="Konfigurationsdatei schreiben", command = updateini)
menubar.add_cascade(label = "Konfiguration", menu = persomenu)

texturemenu = Menu(menubar, tearoff=0)
texturemenu.add_command(label = "Texturen", command = showTexture)
menubar.add_cascade(label = "Texturen", menu = texturemenu)

ftpmenu = Menu(menubar, tearoff=0)
ftpmenu.add_command(label = "Upload", command = ftpupload)
#ftpmenu.add_command(label = "Download", command = ftpdownload)
menubar.add_cascade(label = "FTP", menu = ftpmenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label = "OAR Informationen...", command = OARInformation)
helpmenu.add_command(label = "Befehlsindex", command = osAdmin_help.help)
helpmenu.add_command(label = "Über osAdmin...", command = about)
menubar.add_cascade(label = "Hilfe", menu = helpmenu)
# -------------------   Menu Ende

root.title("osAdmin")

x, y = map(int, root.geometry().split('+')[1:])
root.geometry("+%d+%d" % (x, y + 175))

# Haupttextfenster
text = tk.Text(root)
text = Text(root, height=40, width=140, font = ("Arial", 10))
scroll = Scrollbar(root, command=text.yview)
scroll.config(command=text.yview)                  
text.config(yscrollcommand=scroll.set)           
scroll.grid(row=0, column=2)
text.grid(row=0, column=1)

# tcl console
tclconsole = tk.Text(root)
tclconsole = Text(root, height=5, width=140, font = ("Arial", 10))
tclconsole.config(foreground="green1")
tclconsole.config(background="black")
scroll2 = Scrollbar(root, command=tclconsole.yview)
scroll2.config(command=tclconsole.yview)                  
tclconsole.config(yscrollcommand=scroll.set)           
scroll2.grid(row=1, column=2)
tclconsole.grid(row=1, column=1)

# commandliste linke seite
Lb1 = Listbox(root, height=43, width=35, font = ("Arial", 8))
Lb1.config(foreground="gray40")
Lb1.config(background="black")
Lb1.insert(1, "Alert(message)")
Lb1.insert(2, "AlertUser(firstname,lastname,message)")
Lb1.insert(3, "AppearanceRebake(firstname,lastname)")
Lb1.insert(4, "AppearanceSend(firstname,lastname)")
Lb1.insert(5, "Backup()")
Lb1.insert(6, "bypasspermissions(onoff)")
Lb1.insert(7, "ChangeRegion(region)")
Lb1.insert(8, "ClearImageQueues(firstname,lastname)")
Lb1.insert(9, "CommandScript(script)")
Lb1.insert(10, "ConfigSave(path)")
Lb1.insert(11, "ConfigSet(section,key,value)")
Lb1.insert(12, "CreateRegion(regionname)")
Lb1.insert(13, "DebugAttachments(log)")
Lb1.insert(14, "DebugAttachmentsThrottle(ms)")
Lb1.insert(15, "DebugEq(number)")
Lb1.insert(16, "DebugGroupsMessagingVerbe(setting)")
Lb1.insert(17, "DebugGroupsMessaging(setting)")
Lb1.insert(18, "DebugHttp(level)")
Lb1.insert(19, "DebugJobengine(level)")
Lb1.insert(20, "DebugPermissions(truefalse)")
Lb1.insert(21, "DebugSceneSet(param,value)")
Lb1.insert(22, "DebugScriptsLog(itemid,loglevel)")
Lb1.insert(23, "DebugThreadpoolLevel(level)")
Lb1.insert(24, "DebugThreadpoolSet(workeriocp,minmax)")
Lb1.insert(25, "DebugXengineLog(level)")
Lb1.insert(26, "DeleteObjectCreator(UUID)")
Lb1.insert(27, "DeleteObjectId(UUIDorlocalID)")
Lb1.insert(28, "DeleteObjectName(name)")
Lb1.insert(29, "DeleteObjectOutside()")
Lb1.insert(30, "DeleteObjectOwner(ownerUUID)")
Lb1.insert(31, "DeleteObjectP(startx,starty,startz,endx,endy,endz)")
Lb1.insert(32, "DeleteRegion(name)")
Lb1.insert(33, "DumpAsset(assetid)")
Lb1.insert(34, "DumpObjectId(UUIDlocalID)")
Lb1.insert(35, "EditScale(name,x,y,z)")
Lb1.insert(36, "EstateCreate(ownerUUID,estatename)")
Lb1.insert(37, "EstateSetName(estateid,newname)")
Lb1.insert(38, "EstateSetOwner(estateid,UUID,Firstname,Lastname)")
Lb1.insert(39, "ExportMap(path)")
Lb1.insert(40, "FcacheAssets()")
Lb1.insert(41, "FcacheClear(file,memory)")
Lb1.insert(42, "FcacheExpire(datetime)")
Lb1.insert(43, "ForceGc()")
Lb1.insert(44, "ForcePermissions(truefalse)")
Lb1.insert(45, "ForceUpdate()")
Lb1.insert(46, "GenerateMap()")
Lb1.insert(47, "J2kDecode(j2kID)")
Lb1.insert(48, "KickUser(firstname,lastname,message)")
Lb1.insert(49, "LandClear()")
Lb1.insert(50, "LinkMapping(x,y)")
Lb1.insert(51, "LinkRegion(Xloc,Yloc)")
Lb1.insert(52, "LoadIar(firstname,lastname,inventorypath,password,IARpath)")
Lb1.insert(53, "LoadOar(loadoaroption)")
Lb1.insert(54, "LoadXml(loadxmloption)")
Lb1.insert(55, "LoadXml2(filename)")
Lb1.insert(56, "LoginDisable()")
Lb1.insert(57, "LoginEnable()")
Lb1.insert(58, "PhysicsSet(param)")
Lb1.insert(59, "RegionRestartAbort(message)")
Lb1.insert(60, "RegionRestartBluebox(message)")
Lb1.insert(61, "RegionRestartNotice(message,seconds)")
Lb1.insert(62, "RemoveRegion(name)")
Lb1.insert(63, "ResetUserCache()")
Lb1.insert(64, "RotateScene(degrees,centerX,centerY)")
Lb1.insert(65, "SaveIar(iarparameters)")
Lb1.insert(66, "SaveOar(oarparameters)")
Lb1.insert(67, "SavePrimsXml2(primname,filename)")
Lb1.insert(68, "SaveXml(xmlfilename)")
Lb1.insert(69, "SaveXml2(xml2filename)")
Lb1.insert(70, "ScaleScene(factor)")
Lb1.insert(71, "ScriptsResume(scriptitemuuid)")
Lb1.insert(72, "ScriptsStart(scriptitemuuid)")
Lb1.insert(73, "ScriptsStop(scriptitemuuid)")
Lb1.insert(74, "ScriptsSuspend(scriptitemuuid)")
Lb1.insert(75, "SetLogLevel(level)")
Lb1.insert(76, "SetTerrainHeights(parameters)")
Lb1.insert(77, "SetTerrainTexture(parameters)")
Lb1.insert(78, "SetWaterHeight(heightxy)")
Lb1.insert(79, "Shutdown(script)")
Lb1.insert(80, "SitUserName(firstname,lastname)")
Lb1.insert(81, "StandUserName(firstname,lastname)")
Lb1.insert(82, "StatsRecord(startstop)")
Lb1.insert(83, "StatsSave(path)")
Lb1.insert(84, "SunCurrentTime(value)")
Lb1.insert(85, "SunDayLength(value)")
Lb1.insert(86, "SunDayNightOffset(value)")
Lb1.insert(87, "SunDayTimeSunHourScale(value)")
Lb1.insert(88, "SunUpdateInterval(value)")
Lb1.insert(89, "SunYearLength(value)")
Lb1.insert(90, "TeleportUser(firstname,lastname,destination)")
Lb1.insert(91, "TerrainBake()")
Lb1.insert(92, "TerrainEffect(name)")
Lb1.insert(93, "TerrainElevate(amount)")
Lb1.insert(94, "TerrainFill(value)")
Lb1.insert(95, "TerrainFlip(direction)")
Lb1.insert(96, "TerrainLoad(script)")
Lb1.insert(97, "TerrainLoadTile(script)")
Lb1.insert(98, "TerrainLower(amount)")
Lb1.insert(99, "TerrainMax(max)")
Lb1.insert(100, "TerrainMin(min)")
Lb1.insert(101, "TerrainModify(operation,value,area,taper)")
Lb1.insert(102, "TerrainMultiply(tmvalue)")
Lb1.insert(103, "TerrainNewbrushes(Enabled)")
Lb1.insert(104, "TerrainRescale(min,max)")
Lb1.insert(105, "TerrainRevert()")
Lb1.insert(106, "TerrainSave(filename)")
Lb1.insert(107, "TerrainSaveTile(filename,filewidth,fileheight,minimumXtile,minimumYtile)")
Lb1.insert(108, "TreeActive()")
Lb1.insert(109, "TreeFreeze()")
Lb1.insert(110, "TreeLoad(xmlfile)")
Lb1.insert(111, "TreePlant()")
Lb1.insert(112, "TreeRate(mSec)")
Lb1.insert(113, "TreeReload()")
Lb1.insert(114, "TreeRemove()")
Lb1.insert(115, "UnlinkRegion(localname)")
Lb1.insert(116, "VivoxDebug(onoff)")
Lb1.insert(117, "WindlightDisable()")
Lb1.insert(118, "WindlightEnable()")
Lb1.insert(119, "WindlightLoad()")
Lb1.grid(row=0, column=0)


root.config(menu = menubar)
# ---------------------------------------------test

#telnetkonsole() # Telnetkonsolentest


root.mainloop()