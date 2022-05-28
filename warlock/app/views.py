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
#=================================Core Modules==================================||
from importlib import import_module#											||
import sys, inspect#															||
from os.path import abspath, dirname, join#										||
#===============================================================================||
from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import BaseView, ModelView, ModelRestApi, expose, has_access
#===============================================================================||
from . import appbuilder, db#													||
from .util import getYAML, thingify#											||
from .config import siteConfig
#===============================================================================||
from condor import condor#										||
#========================Common Globals=========================================||
here = join(dirname(__file__),'')#												||
log = True
#===============================================================================||
'''Load active modules from yellow prints'''#									||
pxcfg = join(abspath(here), '_data_/views.yaml')
cfg = condor.instruct(pxcfg).load().dikt#	||load views config
site = siteConfig()

def buildViews():#																||
	'''Load Configuration File with Views for Application then run them through#||
		a view factory'''#														||
	for yp in cfg['modelViews'].keys():#										||
		if not isinstance(cfg['modelViews'][yp], dict) or yp not in site:#		||
			continue#															||
		for view, vwcfg in cfg['modelViews'][yp].items():#						||
			baseVIEW = thingify(vwcfg['viewtype'])#								||
			vclass = ViewFactory(view, vwcfg, baseVIEW)#						||
			if vclass == None:#													||
				continue#														||
			globals()[view] = vclass#											||

def ViewFactory(name, cfg, BaseClass):#											||
	'''Generate View from yaml configuration '''#								||
	if cfg['viewtype'] == 'flask_appbuilder.BaseView':#							||
		kwargs = {}#															||
		cnt = 0#																||
		if cfg['methods'] != None:
			for method in cfg['methods']:#										||
				kwargs[method] = FxFactory(name, cfg['methods'][method])#		||
				if cnt == 0:#													||
					kwargs['default_view'] = method#							||
				cnt += 1#														||
				def method(self, cfg):#											||
					for var in cfg.keys():#										||
						locals()[var] = cfg[var]#								||
					self.update_redirect()#										||
					return self.render(template(tmplt), **kwargs)#				||
		newclass = type(name, (BaseClass, ), {**kwargs})#						||
	elif cfg['viewtype'] == 'flask_appbuilder.ModelView':#						||Create Model View
		def __init__(self):#													||
			BaseClass.__init__(self)#											||
		datamodel = setModelViewVars(cfg['self'])['datamodel']#										||
		if datamodel == None:#													||
			return None#														||
		kwargs = {}
		if 'attrs' in cfg.keys() and cfg['attrs'] != None:
			kwargs = setModelViewVars(cfg['attrs'])
		newclass = type(name, (BaseClass,),{"__init__": __init__,#				||
											'datamodel': datamodel, **kwargs})#	||
	elif cfg['viewtype'] == 'flask_appbuilder.charts.views.DirectByChartView':#	||Create Chart View
		datamodel = setModelViewVars(cfg)['datamodel']
		chart_title = cfg['chart_title']#										||
		definitions = cfg['definitions']#										||
	elif cfg['viewtype'] == 'flask_appbuilder.charts.views.GroupByChartView':#	||Create Chart View Group
		chart_title = cfg['chart_title']#										||
		definitions = cfg['definitions']#										||
	else:#																		||
		print(cfg['viewtype'], 'Not Valid')#									||
	return newclass#															||

def render_yellow_template():#													||
	'''integrate yellow print templates'''
	return tmplt

def FxFactory(cls, cfg):#														||
	'''Dynamically add methods to class views '''
	args = []
#	args, kwargs = cfg['args'], cfg['kwargs']#									||
#	@expose(cfg['decorators']['expose'])#										||
	def function_template(args, kwargs):#										||
		for arg in args:#														||
			pass#																||
	return function_template#													||

def linkFactory(name, params):
	''' '''
	getattr(appbuilder, 'add_link')(name, **params)
	return

def setModelViewVars(kwargs):#													||
	'''Define base model attributes'''#											||
	try:#																		||
		interface = thingify(kwargs['datamodel']['interface'])#					||
		model = thingify(kwargs['datamodel']['model'])#							||
		kwargs['datamodel'] = interface(model)#									||
	except:#																	||
		pass#																	||
	for k in kwargs.keys():
		if 'widget' in k:
			try:
				kwargs[k] = thingify(kwargs[k])
			except Exception as e:
				print('Error', e)
	if kwargs == None:
		kwargs = {}
	return kwargs#																||

@appbuilder.app.errorhandler(404)#												||
def page_not_found(e):#															||
	'''Supply a 404 page'''
	return render_template('404.html', base_template=appbuilder.base_template,#	||
													appbuilder=appbuilder), 404#||

def ViewRegistrationFactory(cfg, viewType):#									||
	for bp, views in cfg.items():#												||
		if not isinstance(views, dict) or bp not in site:#						||
			continue#															||
		for view, params in views.items():#										||
			if view == 'SimpleView0':#											||
				continue#														||
			rvcfg = params['registration']#										||
			if viewType == 'ModelView':#										||
				try:#															||
					args = [thingify(rvcfg['class']), rvcfg['title']]
					appbuilder.add_view(*args, **rvcfg['kwargs'])#				||
				except:#														||
					continue#													||
			elif viewType == 'PageView':
				try:#															||
					args = [thingify(rvcfg['class']), rvcfg['title']]
					appbuilder.add_view(*args, **rvcfg['kwargs'])#	||
					appbuilder.add_link(thingify())
				except:#														||
					continue#													||

db.create_all()#																||
buildViews()#																	||
ViewRegistrationFactory(cfg['modelViews'], 'ModelView')#						||

class pyAutodExcel(BaseView):
	default_view = 'index'
	@expose('/', methods=['GET',])
#	@has_access
	def index(self):
		''' '''
		return self.render_template("testPage.html")#				||
	@expose('/<seq>', methods=['GET',])
#	@has_access
	def Seq000(self, seq):
		''' '''
		return self.render_template("testPage.html", param1=seq)#				||
	@expose('/seq001', methods=['GET',])
#	@has_access
	def Seq001(self):
		''' '''
		return self.render_template("testPage.html")#							||
	@expose('/seq002', methods=['GET',])
	def Seq002(self):
		''' '''
		return self.render_template("tabs.html")
	def dbview(self):
		''' '''
		buckets = get_buckets_list()
		return render_template('template.html',
				base_template=appbuilder.base_template, appbuilder=appbuilder,#	||
				buckets=buckets)#												||
appbuilder.add_view(pyAutodExcel, "index", category='Software',
							category_icon='fa-envelope', icon='fa-envelope',
							label='Guides')
appbuilder.add_link("Seq000", href='/pyautodexcel/seq000', category='Software',
										icon='fa-envelope', label='Lessons')
appbuilder.add_link("Seq001", href='/pyautodexcel/seq001', category='Software',
										icon='fa-envelope', label='Lessons1')
appbuilder.add_link("Seq002", href='/pyautodexcel/seq002', category='Software',
										icon='fa-envelope', label='Lessons2')
class cal(BaseView):
	default_view = 'index'
	@expose('/', methods=['GET',])
	def index(self):
		return self.render_template('calendar.calendar.html')
appbuilder.add_view(cal, "index", category='Calendar',
						category_icon='fa-envelope', icon='fa-envelope',
						label='Month')


# @appbuilder.route('/doesthiswork')
# def doesthiswork():
# 	return jsonify('hello, world!')






















#create a pull down listing the lessons?
