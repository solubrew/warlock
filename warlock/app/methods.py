#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''  																			||
---  																			||
<(META)>:  																		||
	DOCid:   																	||
	name: Warlock Methods  														||
	description: >  															||
		General methods to be added to classes selected by a configuration  	||
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
#===============================================================================||
#from flask_appbuilder import ImageManager
#============================Common Globals=====================================||
here = join(dirname(__file__),'')#												||
there = abspath(join('../../..'))#												||set path at pheonix level
version = '0.0.0.0.0.0'#														||
log = True
#===============================================================================||
def __repr__(self):
	return self.name

def photo_img(self, g000, g001):#												||
	im = ImageManager()#														||
	if g001:#																	||
		data = {'url': url_for(url, pk=str(g000)), 'src': im.get_url(g001)}#	||
	else:#																		||
		data = {'url': url_for(url, pk=str(g000)), 'src': '//:0'}#				||
	markup = subtrix.mechanism(pxcfg['link_image']['text'],data).run()[0]#		||
	return Markup(markup)#														||

def photo_img_thumbnail(self, url, g000, g001):#								||
	im = ImageManager()#														||
	if g001:#																	||
		data = {'url': url_for(url, pk=str(g000)),#								||
											'src': im.get_url_thumbnail(g001)}#	||
	else:#																		||
		data = {'url': url_for(url, pk=str(g000)), 'src': '//:0'}#				||
	markup = subtrix.mechanism(pxcfg['link_image']['text'],data).run()[0]#		||
	return Markup(markup)#														||

def percentage(self, g000, g001):#												||
	''
	numerator = g000
	denominator = g001
	if denominator != 0:
		return (numerator*100)/denominator
	else:
		return 0.0

def month_year(self, g000):
	date = g000
	return datetime.datetime(date.year, date.month, 1)

def year(self, g000):
	date = g000
	return datetime.datetime(date.year, 1, 1)

def label(self):
	''
	pxcfg['strong']['text']
