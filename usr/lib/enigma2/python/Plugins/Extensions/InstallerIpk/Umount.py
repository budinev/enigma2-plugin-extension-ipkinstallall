from . import _
from Screens.Screen import Screen
from Components.Console import Console
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
import os
from Components.config import KEY_LEFT, KEY_RIGHT, config
from Components.ConfigList import ConfigList, ConfigListScreen


class UmountDevice(Screen):
	skin = """
		<screen position="center,center" size="680,460" title="Umount device">
			<widget name="wdg_label_instruction" position="10,10" size="660,45" halign="center" font="Regular;20" />
			<widget name="wdg_label_legend_1" position="10,60" size="130,30" font="Regular;20" />
			<widget name="wdg_label_legend_2" position="140,60" size="180,30" font="Regular;20" />
			<widget name="wdg_label_legend_3" position="320,60" size="180,30" font="Regular;20" />
			<widget name="wdg_label_legend_4" position="500,60" size="150,30" font="Regular;20" />
			<widget name="wdg_menulist_device" position="10,90" size="660,300" />
			<widget name="wdg_config" position="10,430" size="660,25" />
			<widget source="wdg_dir" render="Label" position="10,400" size="600,25" font="Regular;20" />
		</screen>"""
	def __init__(self, session, cur_dir=None):
		self.cur_dir = cur_dir
		Screen.__init__(self, session)
		self.session = session
		self["actions"] = ActionMap( ["OkCancelActions", "DirectionActions"],
						{
						"cancel": self.exitPlugin,
						"ok": self.umountDevice,
						"left": self.keyLeft,
						"right": self.keyRight
						},
					 -1 )
		self["wdg_label_instruction"] = Label( _("Select device and press OK to umount or EXIT to quit") )
		self["wdg_label_legend_1"] = Label( _("DEVICE") )
		self["wdg_label_legend_2"] = Label( _("MOUNTED ON") )
		self["wdg_label_legend_3"] = Label( _("TYPE") )
		self["wdg_label_legend_4"] = Label( _("SIZE") )
		self["wdg_dir"] =  StaticText()
		if self.cur_dir is not None:
			dir = _("The current directory: %s") % self.cur_dir
			self["wdg_dir"].setText(dir)
		self.wdg_list_dev = []
		self.list_dev = []
		self.noDeviceError = True
		self["wdg_menulist_device"] = MenuList( self.wdg_list_dev )
		self.getDevicesList()
		self.configList = []
		self["wdg_config"] = ConfigList(self.configList, session = self.session)
		self.configList.append(( _("Show only removable devices"), config.plugins.InstallerIpk.only_removable))
		self["wdg_config"].setList(self.configList)
		self.setup_title = _("Umount device")
		self.setCustomTitle()

	def setCustomTitle(self):
		self.setTitle(self.setup_title)

	def keyLeft(self):
			self["wdg_config"].handleKey(KEY_LEFT)
			for x in self["wdg_config"].list:
				x[1].save()
			self.getDevicesList()

	def keyRight(self):
			self["wdg_config"].handleKey(KEY_RIGHT)
			for x in self["wdg_config"].list:
				x[1].save()
			self.getDevicesList()

	def exitPlugin(self):
		self.close()

	def umountDeviceConfirm(self, result):
		if result == True :
			Console().ePopen('umount -f %s 2>&1' % (self.list_dev[self.selectedDevice]), self.umountDeviceDone)

	def umountDeviceDone(self, result, retval, extra_args):
		if retval != 0:
			errmsg = '\n\n' + _("umount return code") + ": %s\n%s" % (retval,result)
			self.session.open(MessageBox, text = _("Cannot umount device") + " " + self.list_dev[self.selectedDevice] + errmsg, type = MessageBox.TYPE_ERROR, timeout = 10)
		self.getDevicesList()

	def umountDevice(self):
		if self.noDeviceError == False :
			self.selectedDevice = self["wdg_menulist_device"].getSelectedIndex()
			self.session.openWithCallback(self.umountDeviceConfirm, MessageBox, text = _("Really umount device") + " " + self.list_dev[self.selectedDevice] + " ?", type = MessageBox.TYPE_YESNO, timeout = 10, default = False )

	def getDevicesList(self):
		global config
		self.wdg_list_dev = []
		self.list_dev = []
		self.noDeviceError = False
		file_mounts = '/proc/mounts'
		if os.path.exists(file_mounts) :
			fd = open(file_mounts,'r')
			lines_mount = fd.readlines()
			fd.close()
			for line in lines_mount :
				l = line.split(' ')
				if l[0][:7] == '/dev/sd' :
					device = l[0][5:8]
					partition = l[0][5:9]
					size = '????'
					file_size = '/sys/block/%s/%s/size' % (device,partition)
					if os.path.exists(file_size) :
						fd = open(file_size,'r')
						size = fd.read()
						fd.close()
						size = size.strip('\n\r\t ')
						size = int(size) / 2048
					removable = '0'
					file_removable = '/sys/block/%s/removable' % (device)
					if os.path.exists(file_removable) :
						fd = open(file_removable, 'r')
						removable = fd.read()
						fd.close()
						removable = removable.strip('\n\r\t ')
					if config.plugins.InstallerIpk.only_removable.value == 0 or removable == '1' :
						self.list_dev.append(l[0])
						self.wdg_list_dev.append( "%-10s %-14s %-11s %8sMB" % (l[0], l[1], l[2]+','+l[3][:2], size) )
		if len(self.list_dev) == 0:
			self.noDeviceError = True
		self["wdg_menulist_device"].setList(self.wdg_list_dev)
