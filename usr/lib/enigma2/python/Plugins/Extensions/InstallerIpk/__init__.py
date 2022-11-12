# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from os import environ
import gettext
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelection

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("InstallerIpk", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/InstallerIpk/locale/"))

def _(txt):
	t = gettext.dgettext("InstallerIpk", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

config.plugins.InstallerIpk = ConfigSubsection()
config.plugins.InstallerIpk.only_removable = ConfigYesNo(default = True)
config.plugins.InstallerIpk.autodetect_message = ConfigYesNo(default = True)
config.plugins.InstallerIpk.manualdetect_type = ConfigSelection([("0", _("only ipk")),("1", _("all types"))], default="0")
config.plugins.InstallerIpk.menu_setup = ConfigYesNo(default = False)