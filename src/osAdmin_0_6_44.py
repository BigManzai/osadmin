#!/usr/bin/python3
# OpenSim Remoteadmin
# Python 3.6 - 2018 by Manfred Aabye Version  0.6.43

# import library
from appJar import gui
import xmlrpc.client
import configparser
from tkinter import *
import tkinter.filedialog
from tkinter.filedialog import askopenfilename, asksaveasfilename
import tkinter.messagebox
from tkinter.colorchooser import askcolor
import datetime
import webbrowser
import tkinter as tk
import tkinter.scrolledtext as tkst
from PIL import Image, ImageTk
from idlelib.delegator import Delegator
import idlelib
import sys
import os
from ftplib import FTP
import gettext
gettext.bindtextdomain('OpenSimRemote', '/language')
gettext.textdomain('OpenSimRemote')
_ = gettext.gettext
# gettext einfügen funktioniert so:
# print(_('This is a translatable string.'))

# --------------------------- Textcolor -----------------------------------
from idlelib.delegator import Delegator
from idlelib.redirector import WidgetRedirector

def resetcache(self):
	"Removes added attributes while leaving original attributes."
	# Function is really about resetting delagator dict
	# to original state.  Cache is just a means
	for key in self.__cache:
		try:
			delattr(self, key)
		except AttributeError:
			pass
	self.__cache.clear()

def setdelegate(self, delegate):
	"Reset attributes and change delegate."
	self.resetcache()
	self.delegate = delegate

class Percolator:

    def __init__(self, text):
        # XXX would be nice to inherit from Delegator
        self.text = text
        self.redir = WidgetRedirector(text)
        self.top = self.bottom = Delegator(text)
        self.bottom.insert = self.redir.register("insert", self.insert)
        self.bottom.delete = self.redir.register("delete", self.delete)
        self.filters = []

    def close(self):
        while self.top is not self.bottom:
            self.removefilter(self.top)
        self.top = None
        self.bottom.setdelegate(None)
        self.bottom = None
        self.redir.close()
        self.redir = None
        self.text = None

    def insert(self, index, chars, tags=None):
        # Could go away if inheriting from Delegator
        self.top.insert(index, chars, tags)

    def delete(self, index1, index2=None):
        # Could go away if inheriting from Delegator
        self.top.delete(index1, index2)

    def insertfilter(self, filter):
        # Perhaps rename to pushfilter()?
        assert isinstance(filter, Delegator)
        assert filter.delegate is None
        filter.setdelegate(self.top)
        self.top = filter

    def removefilter(self, filter):
        # XXX Perhaps should only support popfilter()?
        assert isinstance(filter, Delegator)
        assert filter.delegate is not None
        f = self.top
        if f is filter:
            self.top = filter.delegate
            filter.setdelegate(None)
        else:
            while f.delegate is not filter:
                assert f is not self.bottom
                f.resetcache()
                f = f.delegate
            f.setdelegate(filter.delegate)
            filter.setdelegate(None)
			
			
def any(name, alternates):
    "Return a named group pattern matching list of alternates."
    return "(?P<%s>" % name + "|".join(alternates) + ")"

def make_pat():
    kw = r"\b" + any("KEYWORD", keyword.kwlist) + r"\b"
    builtinlist = [str(name) for name in dir(builtins)
                                        if not name.startswith('_') and \
                                        name not in keyword.kwlist]
    # self.file = open("file") :
    # 1st 'file' colorized normal, 2nd as builtin, 3rd as string
    builtin = r"([^.'\"\\#]\b|^)" + any("BUILTIN", builtinlist) + r"\b"
    comment = any("COMMENT", [r"#[^\n]*"])
    stringprefix = r"(?i:\br|u|f|fr|rf|b|br|rb)?"
    sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    string = any("STRING", [sq3string, dq3string, sqstring, dqstring])
    return kw + "|" + builtin + "|" + comment + "|" + string +\
           "|" + any("SYNC", [r"\n"])

	# prog = re.compile(make_pat(), re.S)
	# idprog = re.compile(r"\s+(\w+)", re.S)

def color_config(text):  # Called from htest, Editor, and Turtle Demo.
    '''Set color opitons of Text widget.

    Should be called whenever ColorDelegator is called.
    '''
    # Not automatic because ColorDelegator does not know 'text'.
    theme = idleConf.CurrentTheme()
    normal_colors = idleConf.GetHighlight(theme, 'normal')
    cursor_color = idleConf.GetHighlight(theme, 'cursor', fgBg='fg')
    select_colors = idleConf.GetHighlight(theme, 'hilite')
    text.config(
        foreground=normal_colors['foreground'],
        background=normal_colors['background'],
        insertbackground=cursor_color,
        selectforeground=select_colors['foreground'],
        selectbackground=select_colors['background'],
        inactiveselectbackground=select_colors['background'],  # new in 8.5
    )

class ColorDelegator(Delegator):

    def __init__(self):
        Delegator.__init__(self)
        self.prog = prog
        self.idprog = idprog
        self.LoadTagDefs()

    def setdelegate(self, delegate):
        if self.delegate is not None:
            self.unbind("<<toggle-auto-coloring>>")
        Delegator.setdelegate(self, delegate)
        if delegate is not None:
            self.config_colors()
            self.bind("<<toggle-auto-coloring>>", self.toggle_colorize_event)
            self.notify_range("1.0", "end")
        else:
            # No delegate - stop any colorizing
            self.stop_colorizing = True
            self.allow_colorizing = False

    def config_colors(self):
        for tag, cnf in self.tagdefs.items():
            if cnf:
                self.tag_configure(tag, **cnf)
        self.tag_raise('sel')

    def LoadTagDefs(self):
        theme = idleConf.CurrentTheme()
        self.tagdefs = {
            "COMMENT": idleConf.GetHighlight(theme, "comment"),
            "KEYWORD": idleConf.GetHighlight(theme, "keyword"),
            "BUILTIN": idleConf.GetHighlight(theme, "builtin"),
            "STRING": idleConf.GetHighlight(theme, "string"),
            "DEFINITION": idleConf.GetHighlight(theme, "definition"),
            "SYNC": {'background':None,'foreground':None},
            "TODO": {'background':None,'foreground':None},
            "ERROR": idleConf.GetHighlight(theme, "error"),
            # The following is used by ReplaceDialog:
            "hit": idleConf.GetHighlight(theme, "hit"),
            }

        if DEBUG: print('tagdefs',self.tagdefs)

    def insert(self, index, chars, tags=None):
        index = self.index(index)
        self.delegate.insert(index, chars, tags)
        self.notify_range(index, index + "+%dc" % len(chars))

    def delete(self, index1, index2=None):
        index1 = self.index(index1)
        self.delegate.delete(index1, index2)
        self.notify_range(index1)

    after_id = None
    allow_colorizing = True
    colorizing = False

    def notify_range(self, index1, index2=None):
        self.tag_add("TODO", index1, index2)
        if self.after_id:
            if DEBUG: print("colorizing already scheduled")
            return
        if self.colorizing:
            self.stop_colorizing = True
            if DEBUG: print("stop colorizing")
        if self.allow_colorizing:
            if DEBUG: print("schedule colorizing")
            self.after_id = self.after(1, self.recolorize)

    close_when_done = None # Window to be closed when done colorizing

    def close(self, close_when_done=None):
        if self.after_id:
            after_id = self.after_id
            self.after_id = None
            if DEBUG: print("cancel scheduled recolorizer")
            self.after_cancel(after_id)
        self.allow_colorizing = False
        self.stop_colorizing = True
        if close_when_done:
            if not self.colorizing:
                close_when_done.destroy()
            else:
                self.close_when_done = close_when_done

    def toggle_colorize_event(self, event):
        if self.after_id:
            after_id = self.after_id
            self.after_id = None
            if DEBUG: print("cancel scheduled recolorizer")
            self.after_cancel(after_id)
        if self.allow_colorizing and self.colorizing:
            if DEBUG: print("stop colorizing")
            self.stop_colorizing = True
        self.allow_colorizing = not self.allow_colorizing
        if self.allow_colorizing and not self.colorizing:
            self.after_id = self.after(1, self.recolorize)
        if DEBUG:
            print("auto colorizing turned",\
                  self.allow_colorizing and "on" or "off")
        return "break"

    def recolorize(self):
        self.after_id = None
        if not self.delegate:
            if DEBUG: print("no delegate")
            return
        if not self.allow_colorizing:
            if DEBUG: print("auto colorizing is off")
            return
        if self.colorizing:
            if DEBUG: print("already colorizing")
            return
        try:
            self.stop_colorizing = False
            self.colorizing = True
            if DEBUG: print("colorizing...")
            t0 = time.perf_counter()
            self.recolorize_main()
            t1 = time.perf_counter()
            if DEBUG: print("%.3f seconds" % (t1-t0))
        finally:
            self.colorizing = False
        if self.allow_colorizing and self.tag_nextrange("TODO", "1.0"):
            if DEBUG: print("reschedule colorizing")
            self.after_id = self.after(1, self.recolorize)
        if self.close_when_done:
            top = self.close_when_done
            self.close_when_done = None
            top.destroy()

    def recolorize_main(self):
        next = "1.0"
        while True:
            item = self.tag_nextrange("TODO", next)
            if not item:
                break
            head, tail = item
            self.tag_remove("SYNC", head, tail)
            item = self.tag_prevrange("SYNC", head)
            if item:
                head = item[1]
            else:
                head = "1.0"

            chars = ""
            next = head
            lines_to_get = 1
            ok = False
            while not ok:
                mark = next
                next = self.index(mark + "+%d lines linestart" %
                                         lines_to_get)
                lines_to_get = min(lines_to_get * 2, 100)
                ok = "SYNC" in self.tag_names(next + "-1c")
                line = self.get(mark, next)
                ##print head, "get", mark, next, "->", repr(line)
                if not line:
                    return
                for tag in self.tagdefs:
                    self.tag_remove(tag, mark, next)
                chars = chars + line
                m = self.prog.search(chars)
                while m:
                    for key, value in m.groupdict().items():
                        if value:
                            a, b = m.span(key)
                            self.tag_add(key,
                                         head + "+%dc" % a,
                                         head + "+%dc" % b)
                            if value in ("def", "class"):
                                m1 = self.idprog.match(chars, b)
                                if m1:
                                    a, b = m1.span(1)
                                    self.tag_add("DEFINITION",
                                                 head + "+%dc" % a,
                                                 head + "+%dc" % b)
                    m = self.prog.search(chars, m.end())
                if "SYNC" in self.tag_names(next + "-1c"):
                    head = next
                    chars = ""
                else:
                    ok = False
                if not ok:
                    # We're in an inconsistent state, and the call to
                    # update may tell us to stop.  It may also change
                    # the correct value for "next" (since this is a
                    # line.col string, not a true mark).  So leave a
                    # crumb telling the next invocation to resume here
                    # in case update tells us to leave.
                    self.tag_add("TODO", next)
                self.update()
                if self.stop_colorizing:
                    if DEBUG: print("colorizing stopped")
                    return

    def removecolors(self):
        for tag in self.tagdefs:
            self.tag_remove(tag, "1.0", "end")

# --------------------------- Textcolor -----------------------------------


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

def conectftpFile():
	config = configparser.ConfigParser()
	config.sections()
	config.read('OpenSimAdmin.ini')
	ftpAdress = config['FTPSERVER']['ftpAdress']
	ftpuser = config['FTPSERVER']['ftpuser']
	ftppass = config['FTPSERVER']['ftppass']
	ftpdirectory = config['FTPSERVER']['ftpdirectory']
	ftp = FTP('ftpAdress')
	ftp.login(user='ftpuser', passwd = 'ftppass')
	
def conectftpDir(ftpdirectory):
	ftp.cwd('ftpdirectory')
	   
def downftpFile(filename):
    filename = 'example.txt'
	#filename = app.openBox(title=None, dirName=None, fileTypes=None, asFile=False, parent=None)
	#filename = app.saveBox(title=None, fileName=None, dirName=None, fileExt=None, fileTypes=None, asFile=None, parent=None)
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    ftp.quit()
    localfile.close()
	
def upftpFile(filename):
    filename = 'exampleFile.txt'
	#filename = app.openBox(title=None, dirName=None, fileTypes=None, asFile=False, parent=None)
	#filename = app.saveBox(title=None, fileName=None, dirName=None, fileExt=None, fileTypes=None, asFile=None, parent=None)
    ftp.storbinary('STOR '+filename, open(filename, 'rb'))
    ftp.quit()
	
# --------- ftp ---------------------------------

# -----------------------------   broadcast   ---------------------------------------------
def broadcastapp():

	# Button Auswertung
	def broadcastbutton(button):
		if button == "Ende":
			app.stop()
			return
		if button == "Hilfe":
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.\nDas Edit Fenster funktioniert wie eine Textverarbeitung.\nErst nach dem klick auf Senden wird die Nachricht abgesendet.\nMaximum an Zeichen: 254.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Bitte Ihre Server Daten in die OpenSimAdmin.ini eintragen.")
			return
		if button == "Senden":
			config = configparser.ConfigParser()
			config.sections()
			config.read('OpenSimAdmin.ini')
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
			app.infoBox("Hilfe", "Setzt Ihre Server Daten in die OpenSimAdmin.ini ein.")
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
			# Writing our configuration file to 'OpenSimAdmin.ini'
			with open('OpenSimAdmin.ini', 'w') as configfile:
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
			config.read('OpenSimAdmin.ini')
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

def help():
		win = tk.Tk()
		frame1 = tk.Frame(
			master = win,			
		)
		frame1.pack(fill='both', expand='yes')
		editArea = tkst.ScrolledText(
			master = frame1,
			wrap   = tk.WORD,
			width  = 150,
			height = 25
		)

		editArea.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
		editArea.insert(tk.INSERT,
		"""\
		Archivierung
		load iar [-m|--merge] <Vorname> <Nachname> <Inventar Pfad> <Passwort> [<Dateiname.iar>] - Lädt Benutzerarchiv (IAR). 
			Der Schrägstrich / bezeichnet hier das Hauptverzeichnis des Benutzers.
			Bitte verwenden sie die Englischen Inventar Verzeichnis Namen.
			Beispiel: load iar Max Mustermann / Passwort123 Dateiname.iar
		load oar [-m|--merge] [-s|--skip-assets] [--default-user "Benutzername"] [--force-terrain] [--force-parcels] [--no-objects] [--rotation Gradanzahl] [--bounding-origin "<x,y,z>"] [--bounding-size "<x,y,z>"] [--displacement "<x,y,z>"] [-d|--debug] [<Dateiname.oar>] - Lädt Daten einer Region aus einem OAR Archiv. 
			Vorher sollte mit change region die zu bearbeitende Region ausgewählt werden.
			Beispiel: load oar MeineGespeicherteRegion.oar
		load xml [<Dateiname.xml> [-newUID [<x> <y> <z>]]] - Lädt Daten einer Region aus dem XML Archiv. 
			Vorher sollte mit change region die zu bearbeitende Region ausgewählt werden.
			Beispiel: load xml MeineDaten.xml
		load xml2 [<Dateiname.xml2>] - Lädt Daten einer Region aus dem XML2 Archiv. 
			Vorher sollte mit change region die zu bearbeitende Region ausgewählt werden.
			Beispiel: load xml2 MeineDaten.xml2
		save iar [-h|--home=<url>] [--noassets] <Vorname> <Nachname> <Inventar Verzeichnis> <Passwort> [<Dateiname.iar>] [-c|--creators] [-e|--exclude=<name/uuid>] [-f|--excludefolder=<foldername/uuid>] [-v|--verbose] - Benutzerarchiv IAR speichern. 
			Der Schrägstrich / bezeichnet hier das Hauptverzeichnis des Benutzers.
			Bitte verwenden sie die Englischen Inventar Verzeichnis Namen.
			Beispiel: save iar Max Mustermann / Passwort123 Dateiname.iar
		save oar [-h|--home=<url>] [--noassets] [--publish] [--perm=<permissions>] [--all] [<Dateiname.oar>] - Speichert die Daten einer Region in ein OAR Archiv. 
			Vorher sollte mit change region die zu bearbeitende Region ausgewählt werden.
			Der Dateiname sollte auch das Datum beinhalten.
			Beispiel: save oar 01-01-2018-MeineRegion.oar
		save prims xml2 [<Prim Name> <Dateiname.xml2>] - Speichert den benannten Prim in eine XML2 Datei. 
			Vorher sollte mit change region die Region ausgewählt werden.
			Beispiel: Save prims xml2 Wuerfel Wuerfeldatei.xml2
		save xml [<Dateiname>] - Speichert die Daten einer Region im XML Format. 
		   Vorher sollte mit change region die Region ausgewählt werden.
		   Der Dateiname sollte auch das Datum beinhalten.
		   Beispiel: save xml 01-01-2018-MeineRegion.xml
		save xml2 [<Dateiname>] - Speichert die Daten einer Region im XML2 Format. 
		   Vorher sollte mit change region die Region ausgewählt werden.
		   Der Dateiname sollte auch das Datum beinhalten.
		   Beispiel: save xml2 01-01-2018-MeineRegion.xml2
		Assets Gegenstände Vermögenswerte
		dump asset <id> - Deponiere ein Gegenstand mit dem id Namen auf dem Datenträger. 
		fcache assets - Eine tiefe abfrage und Zwischenspeicherung aller Gegenstände in allen Szenen. 
		fcache clear [Datei] [Speicher] - Entfernt alle Objekte im Cache. Wenn Datei oder Speicher angegeben ist, wird nur dieser Cache gelöscht. 
		fcache expire <DatumZeit> - Zwischengespeicherte Ressourcen löschen, die älter als das angegebene Datum / die angegebene Uhrzeit sind. 
		fcache status - Zeigt den Cache Status an. 
		j2k decode <ID> - Dekodiert das Rastergrafikformat JPEG2000 eines Gegenstandes. 
		show asset <ID> - Zeigt Gegenstandinformationen. 
		Comms gemeinsames
		clear image queues <Vorname> <Nachname> - Löscht Bildwarteschlangen (Texturen, die über UDP heruntergeladen wurden) für einen bestimmten Client. 
		show caps list - Zeigt eine Liste der registrierten Funktionen für Benutzer an. 
		show caps stats by cap <cap-name> - Zeigt Statistiken über die Nutzung der Fähigkeiten nach Fähigkeiten an. 
		show caps stats by user <Vorname> <Nachname> - Zeigt Statistiken über die Nutzung der Fähigkeiten durch den Benutzer. 
		show circuits - Zeigt die Daten der Agent-Schaltung an. 
		show connections - Verbindungsdaten anzeigen. 
		show http-handlers - Zeige alle registrierten HTTP-Handler an. 
		show image queues <Vorname> <Nachname> - Zeigt die Bildwarteschlangen (Texturen, die über UDP heruntergeladen wurden) für einen bestimmten Client an. 
		show pending-objects - Zeigt # von Objekten in den ausstehenden Warteschlangen aller Szenebetrachter an. 
		show pqueues [full] - Zeigt die Daten der Prioritätswarteschlangen für jeden Client an. 
		show queues [full] - Zeigt Warteschlangendaten für jeden Client an. 
		show throttles [full] - Zeigt die Einstellungen für jeden Client und für den gesamten Server an. 
		Debuggen
		debug attachments log [0 | 1] - Aktiviert/Deaktiviert Debug Protokollierung 0=aus, 1=an. 
		debug attachments status - Zeigt den Debug Status der aktuellen Anhänge an. 
		debug attachments throttle <ms> - Aktivieren Sie die Beschränkung von Anhängen in Millisekunden. 
		debug eq [0 | 1 | 2] - Aktiviert das Debuggen der Ereigniswarteschlange. 
			0 - Deaktiviert die Protokollierung aller Ereigniswarteschlangen.
			1 - Aktiviert die Protokollierung ausgehender Ereignisse.
			2 - Aktiviert die Protokollierung ausgehender Ereignisse mit Benachrichtigung.
		debug groups messaging verbose <true | false> - Diese Einstellung aktiviert das Nachrichten Debugging sehr ausführlicher Gruppen. 
		debug groups verbose <true | false> - Diese Einstellung aktiviert das Debuggen sehr ausführlicher Gruppen. 
		debug http <in | out | all> [<level>] - Aktivieren Sie die HTTP-Anforderungsprotokollierung. 
		debug jobengine <start|stop|status|log> - Starten, stoppen, Status abrufen oder Protokollierungsstufe der Job Engine festlegen. 
		debug permissions <true / false> - Aktiviert das Debugging von Berechtigungen. 
		debug scene get - Listet aktuelle Szeneoptionen auf. 
		debug scene set <param> <value> - Aktiviert die Option zum Debuggen von Szenen. 
		debug scripts log <item-id> <log-level> - Zusätzliche Debug-Protokollierung für ein bestimmtes Skript. 
		debug threadpool level 0..3 - Aktiviert die Protokollierung von Aktivitäten im Hauptthread-Pool. 
		debug threadpool set worker|iocp min|max <n> - Legt die Threadpool Parameter fest. Für Debug Zwecke. 
		debug threadpool status - Zeigt die aktuellen Debug Threadpool Parameter an. 
		debug xengine log [<level>] - Aktiviert das detaillierte Xengine Debugging. 
		force gc - Die Garbage Collection der Laufzeit manuell aufrufen. Für Debugging-Zwecke. 
		show eq - Zeigt den Inhalt von Ereigniswarteschlangen für angemeldete Avatare an. Wird zum Debuggen verwendet. 
		show threadpool calls complete - Zeigt Details zu Threadpoolaufrufen an, die abgeschlossen wurden. 
		threads abort <thread-id> - Beendet einen verwalteten Thread. Verwenden Sie "show threads", um mögliche Threads zu finden. 
		Estates Immobilien
		estate create <Eigentümer UUID> <Name des Grundstücks> - Erstellt ein neues Grundstück mit dem angegebenen Namen und dem angegebene Benutzer. 
		estate link region <estate ID> <region ID> - Hängt die angegebene Region an die angegebene Immobilie an. 
		estate set name <estate-id> <Neuer Name> - Legt den Namen des angegebenen Immobilienvermögens auf den angegebenen Wert fest. 
		estate set owner <estate-id> [<UUID>|<Vorname><Nachname>] - Legt den Eigentümer des angegebenen Standorts auf die angegebene UUID oder den angegebenen Benutzer fest. 
		estate show - Zeigt alle Anwesen im Simulator an. 
		Freunde
		friends show [--cache] <Vorname> <Nachname> - Zeigt alle Freunde des Benutzer an. 
		Allgemeines
		change region <Regionsname> - Aktuelle Region ändern, Root sind alle Regionen. 
			Wenn ihr hier nicht aufpasst und auf Root zum Beispiel euer Terrain ändert, 
			wirkt sich das auf alle Regionen gleichzeitig aus.
		command-script <Skript> - Führt ein Befehlsskript aus einer Datei aus. 
		config get [<section>] [<key>] - Synonym für config show. 
		config save <Dateiname> - Speichert die aktuelle Konfiguration in eine Datei. 
		config set <section> <key> <value> - Setze eine Konfigurationsoption. 
			In den meisten Fällen ist dies nicht sinnvoll, da geänderte Parameter nicht dynamisch neu geladen werden. 
			Geänderte Parameter bleiben auch nicht erhalten - Sie müssen eine Konfigurationsdatei manuell ändern und neu starten.
		config show [<section>] [<key>] - Zeigt Konfigurationsinformationen an. 
		get log level - Ruft die aktuelle Protokollierungsstufe der Konsole ab. 
		monitor report - Gibt eine Vielzahl von Statistiken über die aktuelle Region und/oder den Simulator aus. 
		quit - Beendet den OpenSimulator. 
		set log level <level> - Legt die Protokollierungsstufe der Konsole für diese Sitzung fest. 
		show checks - Zeigt die für diesen Server konfigurierten Checks an. 
		show info - Zeigt allgemeine Informationen über den Server an. 
		show modules - Zeigt die Module an. 
		show stats [list|all|(<category>[.<container>])+ - Alias ​​für den Befehl 'stats show'. 
		show threads - Zeige den thread status. 
		show uptime - Serververfügbarkeit anzeigen. 
		show version - Serverversion anzeigen. 
		shutdown - Beenden den OpenSimulator. 
		stats record start|stop - Kontrollieren Sie, ob Statistiken regelmäßig in einer separaten Datei aufgezeichnet werden. 
		stats save <path> - Speichere den Snapshot in eine Datei. Wenn die Datei bereits existiert, wird der Bericht angehängt. 
		stats show [list|all|(<category>[.<container>])+ - Zeigt statistische Informationen für diesen Server an. 
		Hilfe
		help [<Name>] - Zeigt Hilfe zu einem bestimmten Befehl oder einer Liste von Befehlen in einer Kategorie an. 
			Beispiel: help Land
		Hypergrid
		link-mapping [<x> <y>] ​​- Stellt die lokale Koordinate so ein, dass HG-Regionen zugeordnet werden. 
		link-region <Xloc> <Yloc> <ServerURI> [<RemoteRegionName>] - Verknüpft eine HyperGrid Region. 
			Beispiele: <ServerURI>: http://grid.net:8002/ oder http://example.org/path/foo.php
		show hyperlinks - Listet die HG-Regionen auf. 
		unlink-region <local name> - Verknüpfung einer Hypergrid Region aufheben. 
		Land
		land clear - Löscht alle Pakete aus der Region. 
		land show [<local-land-id>] - Zeigt Informationen über die Parzellen in der Region an. 
		Objekte
		backup - Das momentan nicht gespeicherte Objekt beibehalten wird sofort gespeichert. 
		delete object creator <UUID> - Löschen von Objekten eines Erstellers. 
		delete object id <UUID-or-localID> - Löscht ein Objekt mit der UUID oder localID. 
		delete object name [--regex] <Name> - Löschen eines Objekts nach Name. 
		delete object outside - Löscht alle Szenenobjekte außerhalb von Bereichsgrenzen. 
		delete object owner <UUID> - Löschen von Objekten nach Eigentümer. 
		delete object pos <start x, start y, anfang z> <end x, end y, end z> - Löschen von Objekten innerhalb des angegebenen Raumes. 
		dump object id <UUID-oder-localID> - Dump die formatierte Serialisierung des angegebenen Objekts in die Datei <UUID> .xml. 
		edit scale <name> <x> <y> <z> - Ändere die Skalierung eines benannten Prims. 
		force update - Erzwinge die Aktualisierung aller Objekte auf Clients. 
		rotate scene <Grad> [CenterX, CenterY] - Dreht alle Szenenobjekte um CenterX, CenterY (Standard 128, 128). 
			bitte sichern Sie Ihre Region vor der Verwendung.
		scale scene <Faktor> - Skaliert die Szenenobjekte. 
			bitte sichern Sie Ihre Region vor der Verwendung.
		show object id [--full] <UUID-or-localID> - Zeigt Details eines Szenenobjekts mit der angegebenen UUID oder localID an 
		show object name [--full] [--regex] <Name> - Zeigt Details von Szenenobjekten mit dem angegebenen Namen an. 
		show object owner [--full] <OwnerID> - Zeigt Details von Szenenobjekten mit angegebenem Eigentümer an. 
		show object pos [--full] <Start x, Start y, Start z> <Ende x, Ende y, Ende z> - Zeigt Details von Szenenobjekten innerhalb der gegebenen Position an. 
		show part id <UUID-or-localID> - Zeigt Details eines Szenenobjektteils mit der angegebenen UUID oder localID an 
		show part name [--regex] <name> - Zeigt Details von Szenenobjektteilen mit dem angegebenen Namen an. 
		show part pos <anfang x, anfang y, anfang z> <end x, end y, end z> - Zeigt Details von Szenenobjektteilen innerhalb des angegebenen Volumens an. 
		translate scene xOffset yOffset zOffset - übersetzt die Szenenobjekte. 
			bitte sichern Sie Ihre Region vor der Verwendung.
		Regionen
		create region ["Regionsname"] <region_file.ini> - Erstellen Sie eine neue Region. 
		delete-region <Name> - Löscht eine Region von der Festplatte. 
		export-map [<Pfad>] - Speichert ein Bild der Weltkarte. 
		generate map - Erzeugt und speichert eine neue Maptile. 
		physics get [<param> | ALL] - Erhalte den Physik-Parameter der aktuell ausgewählten Region. 
		physics list - Listen Sie die einstellbaren physikalischen Parameter auf. 
		physics set <param> [<value> | TRUE | FALSE] [localID | ALL] - Stellt den Physikparameter der aktuell ausgewählten Region ein. 
		region get - Zeigt Steuerinformationen für die aktuell ausgewählte Region an (Hostname, maximale Größe des physischen Prims usw.). 
		region restart abort [<Nachricht>] - Bricht den Neustart einer Region ab 
		region restart bluebox <Nachricht> <Delta Sekunden> + - Planen Sie einen Neustart der Region. 
		region restart notice <Nachricht> <Delta Sekunden> + - Planen Sie einen Neustart der Region. 
		region set - Legen Sie die Steuerungsinformationen für die aktuell ausgewählte Region fest. 
		remove-region <Name> - Entfernt eine Region aus diesem Simulator. 
		restart - Starten Sie die aktuell ausgewählten Regionen in dieser Instanz neu. 
		set terrain heights <Ecke> <min> <max> [<x>] [<y>] - Legt die Höhen der Terrain-Texturen in der Ecke 
			<Ecke> auf <min> / <max> fest, wenn <x> oder <y > werden angegeben, 
			es wird nur auf Regionen mit einer übereinstimmenden Koordinate festgelegt. 
			Geben Sie -1 in <x> oder <y> an, um diese Koordinate als Platzhalter zu verwenden. 
			Ecke SW = 0, NW = 1, SE = 2, NE = 3, alle Ecken = -1.
		set terrain texture <number> <uuid> [<x>] [<y>] - Setzt das Terrain <number> auf <uuid>, wenn <x> oder <y> angegeben sind, wird es nur auf Regionen mit gesetzt eine übereinstimmende Koordinate. Geben Sie -1 in <x> oder <y> an, um diese Koordinate als Platzhalter zu verwenden. 
		set water height <Höhe> [<x>] [<y>] - Stellt die Wasserhöhe in Metern ein. Wenn <x> und <y> angegeben sind, wird es nur auf Regionen mit einer übereinstimmenden Koordinate gesetzt. Geben Sie -1 in <x> oder <y> an, um diese Koordinate als Platzhalter zu verwenden. 
		show neighbours - Zeigt die Nachbarn der lokalen Region an 
		show ratings - Bewertungsdaten anzeigen 
		show region - Zeigt Kontrollinformationen für die aktuell ausgewählte Region an (Hostname, maximale Größe des physischen Prims usw.). 
		show regions - Zeige Regionsdaten 
		show regionsinview - Zeigt Regionen an, die von einer Region aus gesehen werden können 
		show scene - Zeigt Live-Informationen für die aktuell ausgewählte Szene an (fps, Prims usw.). 
		Sonne
		sun current_time [<Wert>] - Zeit in Sekunden des Simulators 
		sun day_length [<Wert>] - Anzahl der Stunden pro Tag 
		sun day_night_offset [<Wert>] - bewirkt eine Verschiebung des Horizonts 
		sun day_time_sun_hour_scale [<Wert>] - skaliert Taglicht vs. Nachtstunden, um das Tag / Nacht-Verhältnis zu ändern 
		sun help - Liste Parameter, die geändert werden können 
		sun list - Liste Parameter, die geändert werden können 
		sun update_interval [<Wert>] - Wie oft wird die Position der Sonne in Frames aktualisiert? 
		sun year_length [<value>] - Anzahl der Tage bis zu einem Jahr 
		Wind
		wind base wind_update_rate [<value>] - Erhalte oder setze die Wind Update Rate. 
		Wind ConfigurableWind avgDirection [<Wert>] - durchschnittliche Windrichtung in Grad 
		Wind ConfigurableWind avgStrength [<Wert>] - durchschnittliche Windstärke 
		Wind ConfigurableWind rateChange [<Wert>] - Änderungsrate 
		Wind ConfigurableWind varDirection [<Wert>] - zulässige Abweichung in Windrichtung in +/- Grad 
		wind ConfigurableWind varStrength [<value>] - zulässige Abweichung der Windstärke 
		Wind SimpleRandomWind Stärke [<Wert>] - Windstärke 
		Skripte
		scripts resume [<script-item-uuid> +] - Setzt alle ausgesetzten Skripte fort. 
		scripts show [<script-item-uuid> +] - Skript-Informationen anzeigen. 
		scripts start [<script-item-uuid> +] - Startet alle gestoppten Skripte. 
		scripts stop [<script-item-uuid> +] - Stoppt alle laufenden Skripte. 
		scripts suspend [[script-item-uuid> +] - Unterbricht alle laufenden Skripte. 
		show script sensors - Zeigt Informationen zu Skriptsensoren an. 
		show script timers - Zeigt Informationen zu Skriptsensoren an. 
		show scripts [<script-item-uuid> +] - Skript-Informationen anzeigen. 
		xengine status - Zeigt Statusinformationen an. 
		Terrain
		Folgende Dateiformate werden unterstützt: 
			.r32 (RAW32) 
			.f32 (RAW32) 
			.ter (Terragen) 
			.raw (LL/SL RAW) 
			.jpg (JPEG) 
			.jpeg (JPEG) 
			.bmp (BMP) 
			.png (PNG) 
			.gif (GIF) 
			.tif (TIFF) 
			.tiff (TIFF)

		terrain load <Dateiname.xxx> - Lädt ein Terrain aus einer angegebenen Datei. 
			Beispiel: terrain load MeineRegionsdatei.png 
		terrain load-tile <Dateiname.xxx> - Lädt ein Terrain aus einem Abschnitt einer größeren Datei. 
		terrain save <Dateiname.xxx> - Speichert die aktuelle Heightmap in eine bestimmten Datei. 
		terrain save-tile <Dateiname.xxx> - Speichert die aktuelle Heightmap in der größeren Datei. 
		terrain fill <Wert> - Füllt die aktuelle Heightmap mit einem bestimmten Wert. 
			Beispiel: terrain fill 20.5 dies macht eine Terrain Oberfläche das genau 50 cm. über Wasser liegt.
		terrain elevate <Wert> - Erhöht die aktuelle Heightmap um den angegebenen Wert. 
		terrain lower <Wert> - Senkt die aktuelle Höhenmap um den angegebenen Wert. 
		terrain multiply <Wert> - Multipliziert die Heightmap mit dem angegebenen Wert. 
		terrain bake - Speichert das aktuelle Terrain in der Regions-Back-Map. 
		terrain revert - Lädt das gebackene Kartengelände in die Regions-Höhenmap. 
		terrain newbrushes - Aktiviert experimentelle Pinsel, die die Standard-Terrain-Pinsel ersetzen. 
			WARNUNG: Dies ist eine Debug-Einstellung und kann jederzeit entfernt werden.
		terrain show - Zeigt die Geländehöhe an einer bestimmten Koordinate an. 
		terrain stats - Zeigt Informationen über die Regions-Heightmap für Debugging-Zwecke an. 
		terrain effect - Führt einen angegebenen Plugin-Effekt aus. 
		terrain modify <operation> value [<mask>] [-taper=<value2>] - Erlaubt Flächeneffekt und Tapering mit Standard Heightmap Manipulationen. 
			Parameter 
			value: Basiswert, der beim Anwenden der Operation verwendet werden soll. 
			mask: 
			-rec=x1,y1,dx[,dy] rzeugt eine rechteckige Maske basierend auf x1,y1 
			-ell=x0,y0,rx[,ry] erzeugt eine elliptische Maske, die zentriert ist um x0,y0 
			taper: 
			Rechteckige Masken verjüngen sich zu Pyramiden.
			Elliptische Masken verjüngen sich wie Kegel.
		terrain manipulation (fill, min, max) 
			   Wert1 repräsentiert die Zielhöhe (in der Mitte der Entfernung)
			   Wert2 repräsentiert die Zielhöhe (an den Kanten der Entfernung)
		terrain movement (raise, lower, noise) 
			   Wert1 repräsentiert eine Delta-Menge (in der Mitte der Reichweite)
			   Wert2 repräsentiert eine Delta-Menge (an Kanten der Range)
		terrain smoothing (smooth) - Der Glättungsvorgang unterscheidet sich etwas von den anderen, da er sich nicht mit Höhenwerten, sondern mit Festigkeitswerten (im Bereich von 0,01 bis 0,99) befasst. 
		Der Algorithmus vereinfacht die Mittelung der Werte um einen Punkt herum und ist wie folgt implementiert: 
		   Der Parameter "strength" gibt an, wie viel des Ergebnisses vom ursprünglichen Wert ("Stärke" * map [x, y]) ist.
		   Der "Taper" -Parameter gibt an, wie viel von dem Rest von dem ersten Ring ist, der den Punkt umgibt (1,0 - "Stärke") * "Taper". 
		   Es gibt 8 Elemente im ersten Ring.
		   Der verbleibende Beitrag wird von dem zweiten Ring geleistet, der den Punkt umgibt. Im zweiten Ring befinden sich 16 Elemente.
		   z.B.
		   terrain modify smooth 0.5 -taper=0.6 
		   das ursprüngliche Element wird 0,5 * map [x0, y0] beitragen
		   jedes Element 1m vom Punkt wird dazu beitragen ((1-0.5) * 0.6) / 8 * map [x1, y1]
		   jedes Element 2m vom Punkt wird dazu beitragen ((1-0.5) * 0.4) / 16 * map [x2, y2]
		Anmerkungen: 
		   Der "Taper" -Wert muss möglicherweise aufgrund der in Maps verwendeten Integer-Mathematik übertrieben werden.
		   z.B. So erstellen Sie eine 512x512 Var-Insel:
		   terrain modify min 30 -ell=256,256,240 -taper=-29 
		terrain flip - Flippt das aktuelle Gelände um die X- oder Y-Achse. 
		terrain rescale - Skaliert das aktuelle Terrain so, dass es zwischen die angegebenen Min- und Max-Höhen passt. 
		terrain min <Wert> - Legt die minimale Geländehöhe auf den angegebenen Wert fest. 
		terrain max <Wert> - Legt die maximale Geländehöhe auf den angegebenen Wert fest. 
		Bäume
		tree active - Aktivitätsstatus für das Baummodul ändern. 
		tree freeze - Freeze / Unfreeze Aktivität für ein definierten Wald. 
		tree load - Lädt Definitionen für den Baum aus einer XML-Datei. 
			 Wird kein Baum definiert dann wird ein Standartbaum genutzt.
		tree plant - Wald erstellen. 
		tree rate - Setzt die Baumaktualisierungsrate in Millisekunden. 
		tree reload - Bäumen neu laden. 
		tree remove - Entfernt alle Bäume. 
		tree statistics - Statistik über die Bäume auf der aktiven Region. 
		Benutzer
		alert <Nachricht> - Senden Sie eine Nachricht an alle. 
		alert-user <Vorname> <Nachname> <Nachricht> - Senden Sie eine Nachricht an einen Benutzer. 
		appearance find <Uuid-oder-Start-von-Uuid> - Finden Sie heraus, welcher Avatar das gegebene Asset als gebackene Textur verwendet, falls vorhanden. 
		appearance rebake <Vorname> <Nachname> - Nachricht an den Viewer: Avatar neu laden. 
		appearance send [<Vorname> <Nachname>] - Sende die Aussehensdaten für jeden Avatar im Simulator an andere Zuschauer. 
		appearance show [<Vorname> <Nachname>] - Zeigt Informationen über das Aussehen des Avatar. 
		attachments show [<Vorname> <Nachname>] - Zeige Anhanginformationen für Avatare in diesem Simulator. 
		bypass permissions <true / false> - Berechtigungsüberprüfungen umgehen. 
		force permissions <true / false> - Erzwinge Berechtigungen an oder aus. 
		kick user <Vorname> <Nachname> [--force] [message] - Kickt einen User vom Simulator. 
		login disable - Simulator Logins deaktivieren. 
		login enable - Aktiviere Simulator Logins. 
		login status - Anmelde-Status anzeigen. 
		reset user cache - Benutzer-Cache zurücksetzen, damit geänderte Einstellungen angewendet werden können. 
		show animations [<Vorname> <Nachname>] - Zeige Animationsinformationen für Avatare in diesem Simulator. 
		show appearance [<vorname> <nachname>] - Synonym für 'appearance show'. 
		show name <uuid> - Zeigt die Bindungen zwischen einer einzelnen Benutzer-UUID und einem Benutzernamen an. 
		show names - Zeigt die Bindungen zwischen Benutzer-UUIDs und Benutzernamen an. 
		show users [full] - Zeigt Benutzerdaten für Benutzer an, die sich derzeit in der Region befinden. 
		sit user name [--regex] <Vorname> <Nachname> - Setze den benannten Benutzer auf ein nicht besetztes Objekt mit einem Sitzziel. 
		stand user name [--regex] <Vorname> <Nachname> - Stehe den benannten Benutzer. 
		teleport user <Vorname> <Nachname> <Ziel> - Teleportieren Sie einen Benutzer in diesem Simulator zum angegebenen Ziel. 
		wearables check <Vorname> <Nachname> - Prüfe, ob die Wearables eines bestimmten Avatars in der Szene gültig sind. 
		wearables show [<Vorname> <Nachname>] - Zeigt Informationen über Wearables für Avatare an. 
		Vivox
		vivox debug <on>|<off> - Stellt vivox debugging an/aus. 
		Windlicht
		windlight load - Lädt Windlight Profil aus der Datenbank und sendet es. 
		windlight enable - Aktivieren Sie das Windlight Plugin. 
		windlight disable - Deaktiviere das Windlight Plugin. 
		""")
		win.mainloop()
		return

# -----------------------------   help  ENDE   --------------------------------------
   
root = Tk()
#root.title("OpenSimulator RemoteAdmin")
#root = tk.Toplevel(root)


# --------------------------   Menu start
menubar = Menu(root)
configmenu = Menu(menubar, tearoff = 0)
configmenu.add_command(label = "Open", command = opn)
#configmenu.add_command(label = "Save", command = save)
configmenu.add_command(label = "Save as...", command = save)
configmenu.add_command(label = "Close", command = clearall)
configmenu.add_separator()
configmenu.add_command(label="Update ini", command = updateini)
configmenu.add_separator()
configmenu.add_command(label = "Exit", command = root.quit)
menubar.add_cascade(label = "File", menu = configmenu)

modmenu = Menu(menubar, tearoff=0)
modmenu.add_command(label="copy", command = copy)
modmenu.add_command(label="paste", command=paste)
modmenu.add_separator()
modmenu.add_command(label = "clear", command = clear)
modmenu.add_command(label = "clearall", command = clearall)
menubar.add_cascade(label = "Edit", menu = modmenu)

insmenu = Menu(menubar, tearoff=0)
insmenu.add_command(label="date",command=date)
insmenu.add_command(label="line",command=line)
menubar.add_cascade(label = "Insert", menu = insmenu)

formatmenu = Menu(menubar, tearoff=0)
formatmenu.add_cascade(label="font...", command = font)
formatmenu.add_separator()
formatmenu.add_radiobutton(label='normal',command=normal)
formatmenu.add_radiobutton(label='bold',command=bold)
formatmenu.add_radiobutton(label='underline',command=underline)
formatmenu.add_radiobutton(label='italic',command=italic)
menubar.add_cascade(label="Format",menu = formatmenu)

agentmenu = Menu(menubar, tearoff=0)
agentmenu.add_command(label = "teleport agent", command = teleportagent)
#agentmenu.add_command(label = "get agents", command = getagents)
menubar.add_cascade(label = "Agent", menu = agentmenu)
#accountmenu = Menu(menubar, tearoff=0)
#accountmenu.add_command(label = "create user", command = createuser)
#accountmenu.add_command(label = "create user_email", command = createuser)
#accountmenu.add_command(label = "exists user", command = existsuser)
#accountmenu.add_command(label = "update user", command = updateuser)
#accountmenu.add_command(label = "authenticate user", command = authenticateuser)
#menubar.add_cascade(label = "Account", menu = accountmenu)

regionmenu = Menu(menubar, tearoff=0)
regionmenu.add_command(label = "broadcast", command = broadcastapp)
regionmenu.add_command(label = "close region", command = closeregion)
#regionmenu.add_command(label = "create region", command = createregion)
regionmenu.add_command(label = "delete region", command = deleteregion)
regionmenu.add_command(label = "modify region", command = modifyregion)
#regionmenu.add_command(label = "region query", command = regionquery)
#regionmenu.add_command(label = "region restart", command = regionrestart)
regionmenu.add_command(label = "shutdown", command = adminshutdown)
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
estatemenu.add_command(label = "estate reload", command = estatereload)
menubar.add_cascade(label = "Estate", menu = estatemenu)

adminmenu = Menu(menubar, tearoff=0)
adminmenu.add_command(label = "console command", command = consolecommand)
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
persomenu.add_command(label="background...", command=background)
menubar.add_cascade(label = "Config", menu = persomenu)

texturemenu = Menu(menubar, tearoff=0)
texturemenu.add_command(label = "Texture", command = showTexture)
menubar.add_cascade(label = "Texture", menu = texturemenu)

ftpmenu = Menu(menubar, tearoff=0)
ftpmenu.add_command(label = "Upload", command = donothing)
ftpmenu.add_command(label = "Download", command = donothing)
menubar.add_cascade(label = "FTP", menu = ftpmenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label = "Help Index", command = help)
helpmenu.add_command(label = "About...", command = about)
menubar.add_cascade(label = "Help", menu = helpmenu)
# -------------------   Menu Ende

root.title("OpenSimulator RemoteAdmin")
x, y = map(int, root.geometry().split('+')[1:])
root.geometry("+%d+%d" % (x, y + 175))
text = tk.Text(root)
p = Percolator(text)
pin = p.insertfilter
pout = p.removefilter


text = Text(root, height=45, width=140, font = ("Arial", 10))
scroll = Scrollbar(root, command=text.yview)
scroll.config(command=text.yview)                  
text.config(yscrollcommand=scroll.set)           
scroll.pack(side=RIGHT, fill=Y)
text.pack()

root.config(menu = menubar)
#root.resizable(0,0)
root.mainloop()