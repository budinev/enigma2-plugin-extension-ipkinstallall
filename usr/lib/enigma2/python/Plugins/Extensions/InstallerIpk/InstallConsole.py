from __future__ import absolute_import
from . import _
from Screens.Screen import Screen
from Components.Pixmap import Pixmap, MultiPixmap
from Components.Button import Button
from Components.ActionMap import ActionMap
from enigma import getDesktop
from Components.ScrollLabel import ScrollLabel
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Components.ConfigList import ConfigList, ConfigListScreen
from Screens.Standby import TryQuitMainloop
from os import path as os_path, system as os_system


class myConsole(Console):
	if getDesktop(0).size().width() > 720:
		skin = """<screen position="90,90" size="1100,570" title="Command execution..." >
				<ePixmap position="150,45" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/red.png" alphatest="blend" />
				<widget name="red" position="150,0" zPosition="2" size="200,40" font="Regular; 18" halign="center" valign="center" backgroundColor="background" foregroundColor="white" transparent="1" />
				<ePixmap position="350,45" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/green.png" alphatest="blend" />
				<widget name="green" position="350,0" zPosition="2" size="200,40" font="Regular; 18" halign="center" valign="center" backgroundColor="background" foregroundColor="white" transparent="1" />
				<ePixmap position="550,45" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/yellow.png" alphatest="blend" />
				<widget name="yellow" position="550,0" zPosition="2" size="200,40" font="Regular; 18" halign="center" valign="center" backgroundColor="background" foregroundColor="white" transparent="1" />
				<ePixmap position="750,45" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/blue.png" alphatest="blend" />
				<widget name="blue" position="750,0" zPosition="2" size="200,40" font="Regular; 18" halign="center" valign="center" backgroundColor="background" foregroundColor="white" transparent="1" />		
				<widget name="text" position="10,50" size="1060,510" font="Regular;20" />
			</screen>"""
	else:
		skin = """<screen position="center,center" size="560,430" title="Command execution...">
				<ePixmap name="red" position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
				<ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
				<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
				<ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 
				<widget name="red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
				<widget name="green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
				<widget name="yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
				<widget name="blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" />		
				<widget name="text" position="10,45" size="540,420" font="Regular;22" />
			</screen>"""
		
	def __init__(self, session, dir=None,  title =_("Command execution..."), cmdlist=None, manual=False):
		self.dir = dir
		Console.__init__(self, session, title, cmdlist)
		self["red"] = Button(_("Close"))
		self["green"] = Button(_("Restart GUI"))
		self["yellow"] = Button(_("Umount device"))
		self["blue"] = Button(_("Save log"))
		self["myConsoleActions"] = ActionMap(["ColorActions"], 
		{
			"red":		self.keyRed,
			"green":	self.keyGreen,
			"yellow":	self.keyYellow,
			"blue":		self.keyBlue,
		}, -1)

		self.cmdlist = cmdlist
		self.manual = manual
		self.run = 0

	def keyRed(self):
		try:
			self.cancel()
		except:
			pass

	def keyBlue(self):
		try:
			if self.run == len(self.cmdlist):
				if not self.dir is None:
					log_file = "%s/install_ipk.log" % (self.dir)
					try:
						log_text = self["text"].getText()
						if os_path.exists(log_file):
							os_system("date >> %s" % (log_file))
							os_system("echo '%s' >> %s" % (log_text, log_file))
						else:
							os_system("date > %s" % (log_file))
							os_system("echo '%s' >> %s" % (log_text, log_file))
					except:
						self.session.open(MessageBox, _("Failed to write log"), MessageBox.TYPE_ERROR, timeout = 5)
					else:
						if os_path.exists(log_file):
							self.session.open(MessageBox, _("Write to %s") % (log_file), MessageBox.TYPE_INFO, timeout = 15)
						else:
							self.session.open(MessageBox, _("Failed to write %s") % (log_file), MessageBox.TYPE_ERROR, timeout = 5)
		except:
			self.session.open(MessageBox, _("Error to write log"), MessageBox.TYPE_ERROR)

	def keyGreen(self):
		if self.run == len(self.cmdlist):
			self.session.openWithCallback(self.restartGui, MessageBox, _("Restart the GUI now?"), MessageBox.TYPE_YESNO)

	def restartGui(self, answer):
		if answer:
			self.session.open(TryQuitMainloop, 3)

	def keyYellow(self):
		#if self.manual:
		#	self.container.appClosed.remove(self.runFinished)
		#	self.container.dataAvail.remove(self.dataAvail)
		#	self.container.kill()
		#	self.close()
		if self.run == len(self.cmdlist):
			from .Umount import UmountDevice
			self.session.open(UmountDevice, cur_dir=self.dir)
