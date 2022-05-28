#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''  #																			||
---  #																			||
<(META)>:  #																	||
	DOCid:   #								||
	name:   #														||
	description: >  #															||
		#														||
	expirary: <[expiration]>  #													||
	version: <[version]>  #														||
	path: <[LEXIvrs]>  #														||
	outline: <[outline]>  #														||
	authority: document|this  #													||
	security: sec|lvl2  #														||
	<(WT)>: -32  #																||
''' #																			||
# -*- coding: utf-8 -*-#														||
#===============================Core Modules====================================||
from os.path import abspath, dirname, join#										||
import sys
#===============================================================================||
from flask_appbuilder import Model
from flask_appbuilder.widgets import FormVerticalWidget, ShowWidget
#from flask_appbuilder.base.mixins.filemanager import ImageManager

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
#=============================modules=============================================||
from app.util import collapse, getYAML, thingify
from app import methods
#============================Pheonix Modules====================================||
from condor import condor#										||
#============================Common Globals=====================================||
here = join(dirname(__file__),'')#												||
there = abspath(join('../../..'))#												||set path at pheonix level
version = '0.0.0.0.0.0'#														||
log = True
#===============================================================================||
cfg = condor.instruct(join(abspath(here), '_data_/config.yaml')).load().dikt#				||Load Site Configuration File
site = [x for x in cfg['modules'].keys() if cfg['modules'][x]['active'] == 1]#	||Set Active Modules
def buildWidgets():#																||
	''' '''
	path = ''
	cfg = condor.instruct(path).load().dikt
	for yp in cfg['widgets'].keys():
		if not cfg['widgets'][yp] == None:
			for widget, wdgtcfg in cfg['widgets'][yp].items():
				globals()[widget] = WidgetFactory(widget, wdgtcfg, Widget)#		||

def WidgetFactory():
	'''Create each widget object from its configurations'''#					||
	def __repr__(self):#														||
		return self.name#														||
	kwargs = setWidgetVars(kwargs)
	newclass = type(name, (BaseClass,), {'__repr__': __repr__}, **kwargs)
	return newclass#															||

def setWidgetVars(kwargs):#															||
	'''Dynamically Set Variables on the Widget'''#								||
	return kwargs#																||

#build these dynamically
class LessonShowWidget(ShowWidget):
	''' '''
	template = 'widgets/lesson_show.html'
class BlogShowWidget(ShowWidget):
	''' '''
	template = 'widgets/blog_show.html'
