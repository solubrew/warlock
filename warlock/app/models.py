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
def buildModels():#																||
	'''Build Each Model Configured or Included in Models.yaml '''#				||
	path = join(abspath(here), '_data_/models.yaml')
	cfg = condor.instruct(path).load().dikt#									||
	for yp in cfg['models'].keys():#											||
		if log: print(f'Yellow Print Model {yp}')
#		if not isinstance(cfg['models'][yp], dict) or yp not in site:#			||
#			continue#															||
		if not cfg['models'][yp] == None:#										||
			for model, mdlcfg in cfg['models'][yp].items():#					||
				globals()[model] = ModelFactory(model, mdlcfg, Model)#			||

def ModelFactory(name, cfg, BaseClass=Model):#									||
	'''Create each model object from its configurations'''#						||
	def __repr__(self):#														||
		return self.name#														||
	columns = setModelVars(cfg['columns'])#										||
	newclass = type(name, (BaseClass,), {'__repr__': __repr__, **columns,})#		||
	return newclass#															||

def setModelMethods(cls, cfg):#													||
	'''Dynamically Set Methods on Model'''#										||
	addMethods = {}#										||
	if not cfg == None:
		for method in cfg:#														||
			if method in methods.__dir__():#										||
				addMethods[method] = method(cls)#									||
	return addMethods#															||

def setModelRelations(cfg):#													||
	'''Dynamically Set Relationships on the Model'''#							||
	kwargs = {}#																||
	if not cfg == None:#										||
		for relation in cfg:#									||
			kwargs[relation] = relationship(cfg[relation])#	||
	return kwargs#																||

def setModelVars(cfg):#															||
	'''Dynamically Set Variables on the Model'''#								||
	kwargs = {}#																||
	for col in cfg.keys():#														||
		params = collapse(cfg[col])#											||
		if params == None:
			continue
		if 'ForeignKey' in params.keys():#										||
			value = Column(col, thingify(params['type']),#						||
											ForeignKey(params['ForeignKey']))#	||
		if params['size'] == None:#												||
			value = Column(thingify(params['type']), **params['kwargs'])#		||
		else:#																	||
			value = Column(thingify(params['type'])(int(params['size'])),#		||
															**params['kwargs'])#||
		kwargs[col] = value#													||
	return kwargs#																||

buildModels()#																	||
#===============================================================================||
'''
'''
#===============================================================================||

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
