"""
Loads plugin settings in Expedient environment.

@date: Feb 20, 2013
@author: CarolinaFernandez, lbergesio
"""

import os
import sys
config = __import__('django.conf')
settings = config.conf.settings

#print sys.path
#print os.environ['DJANGO_SETTINGS_MODULE']

#XXX lbergesio:This is ugly and prints before say sys.path and environment are right.
#XXX Try to remove this lines.

# Enable imports under this folder
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
# Import Django environment variables to be used inside PluginLoader class
os.environ['DJANGO_SETTINGS_MODULE'] = "expedient.clearinghouse.settings"


# Set path for plugins (set at 'expedient/common/utils/plugins/pluginloader.py')
PLUGINS_PATH = os.path.join(settings.SRC_DIR,"python","plugins")
#sys.path.append(PLUGIN_LOADER.plugins_path)
sys.path.append(os.path.join(PLUGINS_PATH))

# Ugly hack to add "INSTALLED_APPS" to the settings
# even when OCF is loaded via manage.py (remember that
# setting will only load now when urls.py is loaded)

import ast
import ConfigParser

confparser = ConfigParser.RawConfigParser()
setting = "installed_apps"

for plugin_name in os.listdir(PLUGINS_PATH):
    if os.path.isdir(os.path.join(PLUGINS_PATH, plugin_name)):
        confparser.readfp(open(os.path.join(PLUGINS_PATH, plugin_name, "settings.conf")))
        if confparser.has_section("general"):
            conf_setting = list()
            if hasattr(settings, setting.upper()):
                conf_setting = getattr(settings, setting.upper()) or conf_setting
            try:
                plugin_setting = ast.literal_eval(confparser.get("general", "installed_apps"))
                # Users may set one app only and not wrap this into a list. Wrap it here
                if not isinstance(plugin_setting, list):
                    plugin_setting = [ '%s' % str(plugin_setting) ]
                # If no setting for plugins has been set in INSTALLED_APPS, add these now
                if [ p for p in plugin_setting if p not in conf_setting ]:
                    setattr(settings, setting.upper(), conf_setting + plugin_setting)
            except:
                pass


#from common.utils.plugins.pluginloader import PluginLoader as PLUGIN_LOADER
#from common.utils.plugins.topologygenerator import TopologyGenerator as TOPOLOGY_GENERATOR
#
#PLUGIN_LOADER.set_plugins_path(os.path.join(os.path.dirname(__file__), "../../../plugins/"))
#PLUGIN_SETTINGS = PLUGIN_LOADER.load_settings()
#
#"""
#Assumes that plugin_settings follows the structure
#{
#    'plugin_name': {
#        'section_name': {
#            'attribute_name': 'attribute_value',
#            ...
#        },
#        ...
#    },
#    ...
#}
#"""
## Iterate over loaded settings to add them to the locals() namespace
#for (plugin, plugin_settings) in PLUGIN_SETTINGS.iteritems():
#    for (section, section_settings) in plugin_settings.iteritems():
#        for (setting, setting_value) in section_settings.iteritems():
#            try:
#                conf_setting = getattr(settings, setting.upper())
#            except Exception as e:
#                setattr(settings, setting.upper(), list()) 
#                conf_setting = getattr(settings, setting.upper())
#            try:
#                if not isinstance(setting_value, list):
#                    setting_value = [setting_value]
#                conf_setting += setting_value
#            except Exception as e:
#                print "[WARNING] Problem loading setting '%s' inside plugin.py. Details: %s" % (setting.upper(), str(e))

