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

#=============================JYASK=============================================||
from ..util import capitalize, collapse, getYAML, thingify
from .. import methods
#============================Pheonix Modules====================================||
from pheonix.elements.config import config#										||
#============================Common Globals=====================================||
here = join(dirname(__file__),'')#												||
there = abspath(join('../../..'))#												||set path at pheonix level
version = '0.0.0.0.0.0'#														||
#===============================================================================||
cfg = config.instruct(join(here, '../config.yaml')).load().dikt#												||Load Site Configuration File
site = [x for x in cfg['modules'].keys() if cfg['modules'][x]['active'] == 1]#	||Set Active Modules
def buildCSSs():
	'''Build properly formatted CSS files from yaml tree'''
	for module in site:
		path = join(here, '../modules/{0}/'.format(module)
		css = '{0}css{1}.yaml'.format(path, capitalize(module,1))
		cfg = config.instruct(css).load().dikt
		if not cfg == None:
			for key in cfg.keys():
				if isinstance(cfg[key], dict):
					pass#css += key + cfg[key]
def buildTMPLTs():
	'''Build page templates from yaml tree'''
	for module in site:
		path = join(here, '../modules/{0}/'.format(module)
		tmplts = '{0}tmplt{1}.yaml'.format(path, capitalize(module,1))
		cfg = config.instruct(tmplts).load().dikt
		if not cfg == None:
			for f in cfg.keys():
				pathf = '{0}templates/{1}'.format(path, f)
				if cfg[f] == None or cfg[f]['document'] == None:
					continue
				if 'jinja' in cfg[f]['document'].keys():
					data = formatHTMLEndPoint(cfg[f]['document']['jinja'])
				elif 'json' in cfg[f]['document'].keys():
					data = formatJSONEndPoint(cfg[f]['document']['json'])
				try:
					with open(pathf, 'w') as doc:
						doc.write(data)
				except:
					pass
def createCSS():
	''' '''
def createHTMLEndPoint():
	''' '''
def createJSONEndPoint():
	''' '''
def createModel(name):
	''' '''
def createModule(name):
	''' '''
	for module in cfg.keys():
		path = '{0}modules/{1}'.format(here, name)
		stubs = ['css', 'frm', 'gric', 'mdl', 'tmplt', 'vw']
		for stub in stubs:
			pathf = '{0}{1}{2}.yaml'.format(path, stub, capitalize(name))
			with yonql.doc(pathf) as wrtr:
				wrtr.write(pathf)
def createView(name):
	''' '''
def deleteModel(name):
	''' '''
def deleteModule(name):
	''' '''
def deleteView(name):
	''' '''
def installModule(pathf):
	'''
	unzip module
	copy to modules directory
	add to config.yaml modules available and set active to 0

	'''
def formatHTMLEndPoint(page):
	'''format text page into a servable html end point '''
	return page
def formatJSONEndPoint(page):
	'''format yaml tree into json formated api end point '''
	return page
def buildPageTemplates(cfg):
	''' '''
	for page in cfg.keys():
		if 'yaml' == cfg[page]['document']:
			storePage(buildYamlPage(cfg[page]['document']['yaml']), page)
		elif 'jinja' == cfg[page]['document']:
			storePage(buildJinjaPage(cfg[page]['document']['jinja']), page)
	return done
def buildYamlPage(template):
	''' '''
def buildJinjaPage(template):
	''' '''
def storePage(content, page):
	''' '''
#===============================================================================||
buildCSSs()
buildTMPLTs()



#load html and css files from each module and build the static files and templates
