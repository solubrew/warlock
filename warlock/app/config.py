#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''  																			||
---  																			||
<(META)>:  																		||
	docid:   																	||
	name:   														||
	description: >  															||
	expirary: <[expiration]>  													||
	version: <[version]>  														||
	path: <[LEXIvrs]>  															||
	outline: <[outline]>  														||
	authority: document|this  													||
	security: sec|lvl2  														||
	<(WT)>: -32  																||
''' #																			||
# -*- coding: utf-8 -*-#														||
#=================================Core Modules==================================||
from os.path import abspath, dirname, join#										||
from importlib import import_module#											||
#===============================================================================||
from condor import condor#										||
#============================Common Globals=====================================||
here = join(dirname(__file__),'')#												||
there = abspath(join('../../..'))#												||set path at pheonix level
version = '0.0.0.0.0.0'#														||
log = True
#===============================================================================||
pxcfg = join(abspath(here), '_data_/config.yaml')
modelscfg = join(abspath(here), '_data_/models.yaml')

def siteConfig():
	cfg = condor.instruct(pxcfg).select('modules').dikt#						||load main config
	site = [x for x in cfg.keys() if cfg[x]['active'] == 1]#					||select active site modules
	yps = condor.instruct(modelscfg).select('models').dikt#						||load blueprint models
	for yp in yps.keys():#														||
		if log: print(f'Yellow Print View {yp} {yps[yp]}')
		if not isinstance(yps[yp], dict) or yp not in site:#					||
			continue#															||
		for model in yps[yp]:#													||
			module = import_module('app.models')#								||
			try:#																||
				globals()[model] = getattr(module, model)#						||
			except:#															||
				pass#															||
	return site
