from . import _
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Screens.Screen import Screen
from Components.Label import Label
from Tools.Directories import fileExists
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os

class DownFeed(Screen):
	skin = """
		<screen name="feedlist" position="center,110" size="850,520" title="2boom's feed downloader">
		<widget source="menu" render="Listbox" position="15,10" size="820,455" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{"template": [
					MultiContentEntryText(pos = (70, 2), size = (700, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
					MultiContentEntryText(pos = (80, 29), size = (700, 18), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
					MultiContentEntryPixmapAlphaTest(pos = (5, 5), size = (50, 40), png = 2), # index 4 is the pixmap
					],
					"fonts": [gFont("Regular", 23),gFont("Regular", 16)],
					"itemHeight": 50
				}
			</convert>
		</widget>
		<ePixmap name="red" position="20,518" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green" position="190,518" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/InstallerIpk/images/green.png" transparent="1" alphatest="on" />
		<widget name="key_red" position="20,488" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
		<widget name="key_green" position="190,488" zPosition="2" size="170,30" valign="center" halign="center" font="Regular;22" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("2boom's feed downloader"))
		self.session = session
		self.list = []
		self["menu"] = List(self.list)
		self.feedlist()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.down,
				"red": self.cancel,
			},-1)
		self.list = [ ]
		self["key_red"] = Label(_("Close"))
		self["key_green"] = Label(_("Download"))

	def feedlist(self):
		self.list = []
		if fileExists("/var/lib/opkg/status"):
			os.system("mv /var/lib/opkg/status /var/lib/opkg/status.tmp")
		os.system("opkg update")
		camdlist = os.popen("opkg list")
		softpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/InstallerIpk/images/feedmini.png"))
		for line in camdlist.readlines():
			try:
				if line.find("plugin-systemplugins") > -1 or line.find("plugin-extensions") > -1 or line.find("plugin-softcams") > -1 or line.find("plugin-skin") > -1:
					if line.find("-dev ") == -1:
						self.list.append(("%s %s" % (line.split(' - ')[0], line.split(' - ')[1]), line.split(' - ')[-1], softpng))
			except:
				self.list.append((_("Error download plugin list"), _("Check your internet connection"), softpng))
		camdlist.close()
		self["menu"].setList(self.list)

	def ok(self):
		self.down()

	def down(self):
		cur = self["menu"].getCurrent()[0]
		if cur and cur != _("Error download plugin list"):
			os.system("cd /tmp && opkg install --force-reinstall --nodeps --download-only %s" % cur)
			if fileExists("/tmp/%s" % cur):
				self.mbox = self.session.open(MessageBox, _("%s is downloaded") % cur, MessageBox.TYPE_INFO, timeout=5)
			else:
				self.mbox = self.session.open(MessageBox, _("Error download plugin list"), MessageBox.TYPE_INFO, timeout=5)

	def cancel(self):
		if fileExists("/var/lib/opkg/status.tmp"):
			os.system("mv /var/lib/opkg/status.tmp /var/lib/opkg/status")
			os.chmod("/var/lib/opkg/status", 0o644)
		self.close()
