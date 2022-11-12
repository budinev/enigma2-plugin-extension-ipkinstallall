from __future__ import absolute_import
from . import _
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from Components.Scanner import Scanner, ScanPath, scanDevice
from Screens.ChoiceBox import ChoiceBox
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, getConfigListEntry
from Components.Label import Label
from Components.Harddisk import harddiskmanager
from Components.MenuList import MenuList
from .ipkSelectionList import SelectionList
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Tools.BoundFunction import boundFunction
from Tools.Directories import fileExists
from .InstallConsole import myConsole
from Screens.InfoBar import InfoBar
from Screens.VirtualKeyBoard import VirtualKeyBoard
from enigma import getDesktop
from .Umount import UmountDevice
from .FeedDownloader import DownFeed
import os

global_session = None
current_dir = None

def execute(option):
	if option == None:
		return

	(_, scanner, files, session) = option
	scanner.open(files, session)

def runCmd(cmd=""):
	if cmd and global_session:
		global_session.open(myConsole, '/tmp', cmd, [cmd], manual=True)

def mountpoint_choosen(option, manual=False):
	if option == None:
		return
	(description, mountpoint, session) = option
	if option[0] == _("Open setup"):
		session.open(SetupInstallerScreen)
		return
	if option[0] == _("Feed downloader"):
		session.open(DownFeed)
		return
	if option[0] == _("Umount device"):
		session.open(UmountDevice)
		return
	if option[0] == _("Execute shell command"):
		session.openWithCallback(runCmd, VirtualKeyBoard, title=_("Please enter shell command:"))
		return
	res = scanDevice(mountpoint)
	_list = [ (r.description, r, res[r], session) for r in res ]
	if not _list:
		if os.access(mountpoint, os.F_OK|os.R_OK) and (manual or config.plugins.InstallerIpk.autodetect_message.value):
			session.open(MessageBox, _("No displayable files on this medium found!"), MessageBox.TYPE_INFO, timeout = 5)
		return
	lst = [ ]
	for x in _list:
		if x[0] == _("Install package ipk"):
			lst.append(x)
			global current_dir
			current_dir = mountpoint
	if manual:
		if config.plugins.InstallerIpk.manualdetect_type.value == "1":
			dlg = session.openWithCallback(execute, ChoiceBox, title = _("The following files were found..."), list = _list)
			dlg.setTitle(_("Auto scan"))
		else:
			if len(lst) > 0:
				execute(lst[0])
	else:
		dlg = session.openWithCallback(execute, ChoiceBox, title = _("The following files were found..."), list = _list)
		dlg.setTitle(_("Auto scan"))

def scan(session):
	try:
		parts = [ (r.tabbedDescription(), r.mountpoint, session) for r in harddiskmanager.getMountedPartitions(onlyhotplug = False) if os.access(r.mountpoint, os.F_OK|os.R_OK) ]
	except:
		parts = [ (r.description, r.mountpoint, session) for r in harddiskmanager.getMountedPartitions(onlyhotplug = False) if os.access(r.mountpoint, os.F_OK|os.R_OK) ]
	parts.append( (_("Memory") + "\t/tmp", "/tmp", session) )
	parts.append( (_("Open setup"), None, session) )
	#parts.append( (_("Feed downloader"), None, session) )
	parts.append( (_("Execute shell command"), None, session) )
	parts.append( (_("Umount device"), None, session) )
	dlg = session.openWithCallback(boundFunction(mountpoint_choosen, manual=True), ChoiceBox, title = _("Please select dir to be scanned, open setup or umount device"), list = parts)
	dlg.setTitle(_("Select action"))

def main(session, **kwargs):
	scan(session)

def setup_menu(menuid, **kwargs):
	if menuid == "setup" and config.plugins.InstallerIpk.menu_setup.value:
		return [(_("Installer ipk"), main, "install_ipk", None)]
	else:
		return []

def partListChanged(action, device):
	global current_dir
	mediascanner = True
	if not os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/MediaScanner/plugin.pyo"):
		mediascanner = False
	if InfoBar and InfoBar.instance:
		if InfoBar.instance.execing or mediascanner:
			try:
				if action == 'add' and device.is_hotplug:
					current_dir = device.mountpoint
					if not mediascanner and InfoBar.instance.execing:
						mountpoint_choosen((device.description, device.mountpoint, global_session))
			except:
				pass

def sessionstart(reason, session):
	global global_session
	if session:
		global_session = session

def autostart(reason, **kwargs):
	global global_session
	if reason == 0:
		try:
			from Components.Harddisk import harddiskmanager
			harddiskmanager.on_partition_list_change.append(partListChanged)
		except:
			pass
	elif reason == 1:
		try:
			from Components.Harddisk import harddiskmanager
			harddiskmanager.on_partition_list_change.remove(partListChanged)
		except:
			pass
		global_session = None

def filescan_open(list, session, **kwargs):
	filelist = [x.path for x in list]
	session.open(OpkgInstaller, filelist)

def filescan(**kwargs):
	return \
		Scanner(mimetypes = ["application/x-debian-package"],
			paths_to_scan =
				[
					ScanPath(path = "ipk", with_subdirs = True),
					ScanPath(path = "", with_subdirs = False),
				],
			name = "Ipk Install",
			description = _("Install package ipk"),
			openfnc = filescan_open, )

class SetupInstallerScreen(Screen, ConfigListScreen):
	skin = """
		<screen position="center,center" size="580,160" >
		<widget name="config" position="0,60" size="580,100" />
		<ePixmap position="60,30" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/red.png" alphatest="blend" />
		<widget name="cancel" position="60,0" zPosition="2" size="200,25" font="Regular; 21" halign="center" valign="center" backgroundColor="background" foregroundColor="white" transparent="1" />
		<ePixmap position="320,30" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/green.png" alphatest="blend" />
		<widget name="ok" position="320,0" zPosition="2" size="200,25" font="Regular; 21" halign="center" valign="center" backgroundColor="background" foregroundColor="white" transparent="1" />
	</screen>"""

	def __init__(self, session, args = None):
		self.skin = SetupInstallerScreen.skin
		self.setup_title = _("Setup Installer ipk")
		Screen.__init__(self, session)
		self["ok"] = Button(_("OK"))
		self["cancel"] = Button(_("Cancel"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions"], 
		{
			"ok": self.keyOk,
			"save": self.keyGreen,
			"cancel": self.keyRed,
		}, -2)
		ConfigListScreen.__init__(self, [])
		self.initConfig()
		self.createSetup()
		self.onClose.append(self.__closed)
		self.onLayoutFinish.append(self.__layoutFinished)

	def __closed(self):
		pass

	def __layoutFinished(self):
		self.setTitle(self.setup_title)

	def initConfig(self):
		def getPrevValues(section):
			res = { }
			for (key,val) in section.content.items.items():
				if isinstance(val, ConfigSubsection):
					res[key] = getPrevValues(val)
				else:
					res[key] = val.value
			return res
		self.IPK = config.plugins.InstallerIpk
		self.prev_values = getPrevValues(self.IPK)
		self.cfg_menu = getConfigListEntry(_("Show plugin in setup menu"), self.IPK.menu_setup)
		self.cfg_message = getConfigListEntry(_("Show popup if no files found in automount"), self.IPK.autodetect_message)
		self.cfg_type = getConfigListEntry(_("Select the type of manual scan"), self.IPK.manualdetect_type)

	def createSetup(self):
		_list = [ self.cfg_menu ]
		_list.append(self.cfg_type)
		if not fileExists("/usr/lib/enigma2/python/Plugins/Extensions/MediaScanner/plugin.pyo"):
			_list.append(self.cfg_message)
		self["config"].list = _list
		self["config"].l.setList(_list)

	def keyOk(self):
		self.keyGreen()

	def keyRed(self):
		def setPrevValues(section, values):
			for (key,val) in section.content.items.items():
				value = values.get(key, None)
				if value != None:
					if isinstance(val, ConfigSubsection):
						setPrevValues(val, value)
					else:
						val.value = value
		setPrevValues(self.IPK, self.prev_values)
		self.keyGreen()

	def keyGreen(self):
		self.IPK.save()
		self.close()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

class OpkgInstaller(Screen):
	if getDesktop(0).size().width() > 720:
		skin = """<screen name="OpkgInstaller" position="center,center" size="800,570" title="Install package ipk in console" >
				<ePixmap position="0,45" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/red.png" alphatest="blend" />
				<widget source="key_red" render="Label" position="0,0" zPosition="2" size="200,40" font="Regular; 18" halign="center" valign="center" backgroundColor="background" foregroundColor="white" transparent="1" />
				<ePixmap position="200,45" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/green.png" alphatest="blend" />
				<widget source="key_green" render="Label" position="200,0" zPosition="2" size="200,40" font="Regular; 18" halign="center" valign="center" backgroundColor="background" foregroundColor="white" transparent="1" />
				<ePixmap position="400,45" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/yellow.png" alphatest="blend" />
				<widget source="key_yellow" render="Label" position="400,0" zPosition="2" size="200,40" font="Regular; 18" halign="center" valign="center" backgroundColor="background" foregroundColor="white" transparent="1" />
				<ePixmap position="600,45" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/blue.png" alphatest="blend" />
				<widget source="key_blue" render="Label" position="600,0" zPosition="2" size="200,40" font="Regular; 18" halign="center" valign="center" backgroundColor="background" foregroundColor="white" transparent="1" />
				<widget name="list" position="10,80" size="780,430" />
				<ePixmap pixmap="skin_default/div-h.png" position="0,520" zPosition="10" size="800,2" transparent="1" alphatest="on" />
				<widget source="introduction" render="Label" position="0,530" zPosition="10" size="800,25" halign="center" valign="center" font="Regular;21" backgroundColor="background" foregroundColor="white" transparent="1" />
			</screen>"""
	else:
		skin = """
			<screen name="OpkgInstaller" position="center,center" size="550,450" title="Install package ipk in console" >
				<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
				<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
				<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
				<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
				<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
				<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
				<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
				<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
				<widget name="list" position="5,50" size="540,360" />
				<ePixmap pixmap="skin_default/div-h.png" position="0,410" zPosition="10" size="560,2" transparent="1" alphatest="on" />
				<widget source="introduction" render="Label" position="5,420" zPosition="10" size="550,30" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
			</screen>"""

	def __init__(self, session, filelist):
		Screen.__init__(self, session)
		self.list = SelectionList()
		self["list"] = self.list
		for listindex in range(len(filelist)):
			self.list.addSelection(filelist[listindex], filelist[listindex], listindex, False)

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		self["key_yellow"] = StaticText(_("Forced install"))
		self["key_blue"] = StaticText(_("Select all"))
		self["introduction"] = StaticText(_("Press OK to toggle the selection"))

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.list.toggleSelection,
			"cancel": self.cansel,
			"red": self.cansel,
			"yellow": self.preforce,
			"green": self.install,
			"blue": self.list.toggleAllSelection
		}, -1)
		self.setup_title = _("Install package ipk in console")
		self.setCustomTitle()

	def setCustomTitle(self):
		self.setTitle(self.setup_title)

	def forceInstall(self):
		global current_dir
		_list = self.list.getSelectionsList()
		if _list and len(_list) > 0:
			dir = current_dir
			cmd = "opkg install --force-reinstall --force-overwrite --force-downgrade "
			for item in _list:
				cmd += "%s " % item[1]
			self.session.open(myConsole, dir, _("Command execution forced install ipk"),[cmd])

	def preforce(self):
		_list = self.list.getSelectionsList()
		if _list and len(_list) > 0:
			self.session.openWithCallback(self.runAnswer, MessageBox, _("This installation option only for exceptional cases!\nDo you really want to use it?"), MessageBox.TYPE_YESNO, default = False)

	def runAnswer(self, answer):
		if answer:
			self.forceInstall()

	def cansel(self):
		global current_dir
		current_dir = None
		self.close()

	def install(self):
		global current_dir
		_list = self.list.getSelectionsList()
		if _list and len(_list) > 0:
			dir = current_dir
			cmd = "opkg install "
			for item in _list:
				cmd += "%s " % item[1]
			self.session.open(myConsole, dir, _("Command execution install ipk"),[cmd])

def Plugins(path, **kwargs):
	return [PluginDescriptor(name=_("Installer ipk"), description=_("Install package ipk in console"), where = PluginDescriptor.WHERE_MENU, fnc = setup_menu),
		PluginDescriptor(name=_("Installer ipk"), description=_("Install package ipk in console"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main),
		PluginDescriptor(name=_("Ipk Install"), where = PluginDescriptor.WHERE_FILESCAN, fnc = filescan),
		PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart),
		PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc = autostart)
		]

