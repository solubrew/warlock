#@@@@@@@@@@@@@@@@@@@@@@@ Dynamic Model Builder @@@@@@@@@@@@@@@@@@@@@@@@@||
'''  #																	||
---  #																	||
<(META)>:  #															||
	DOCid:   #						||
	name:   #							||
	description: >  #													||
		create website using framework built under warlock
			flask - is a flask app and superset framework configured to
					build from yaml configuration documents
			nikola - is a nikola static site configured to build from yaml
					configuration documents
		leverage distributor and ctrlr to deploy and configure a website using
		one of the available frameworks
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
import os, urllib#																||
#===============================================================================||
from condor import condor
from fxsquirl import collector
from worldbridger import worldbridger
from eras.dsm import databaseTLs
#=======================================================================||
here = os.path.join(os.path.dirname(__file__),'')#						||
there = os.path.abspath(os.path.join('../../..'))#						||set path at pheonix level
#=======================================================================||
class spawn(worldbridger.stone):
	'''Spawn, build and deploy websites to location using frameworks
		create local setup location, create EDN for deploy interally,
		externally or public'''
	def __init__(self, name, cfg={}):
		''' '''
		pxcfg = f'{here}z-data_/warlock.yaml'
		self.config = condor.instruct(pxcfg).override(cfg)
		worldbridger.stone.__init__(self)
		self.workingdir = self.config.wdir
		self.name = name
	def build(self, framework='flask'):
		'''build configurations and integrate custom modules and blueprints'''
		frm = self.config.dikt['framework']
		fs = fonql.doc(self.to).read()
		while True:
			fd = next(fs, None)
			if fd == None:
				break
			for f in fd.dikt.philes:
				doc = txtonql.doc(f).read()
				ndoc = subtrix.mechanism(doc, self.config).run()[0]
				txtonql.doc(f).write(ndoc)
		return self
	def config(self):
		'''Configure Services needed to run the website '''
		if self.framework == 'flask':
			self.db = setupDatabase(self.config.db)
		return self
	def deploy(self):
		'''Copy Locally Tested Site to Deployment location and conduct all data
			updates needed on production systems'''

		return self
	def down(self, where='internal'):
		'''Take Site down'''
		if where == 'internal':
			databaseTLs.backupDB()
			databaseTLs.deleteDB()
		elif where == 'public':
			databaseTLs.backupDB()# take a backup of the public database
			databaseTLs.createDB()# create a database local for the public site
			databaseTLs.restoreDB()# restore the image to ensure public restoration is possible
			databaseTLs.deleteDB()#now delete the public site database
	def generate(self):
		''' '''
		return self
	def name(self, name):
		'''Set name of new site '''

		return self
	def spawn(self, to, framework='flask'):
		'''Create a New Site using the given frame work at the given location
		'''
		self.to = to
		path = f'{here}{framework}'
		fsonql.doc(path).copy(f'{to}{self.name}')
		self.build()
		return self
	def run(self):
		''' '''

	def up(self):
		'''Run setup scripts and connect to services'''
		if where == 'internal':
			self.down(where)
			createDatabase()
			restoreDatabase()
		elif where == 'public':
			self.down(where)
			createDB(where)
			backupDB(where)#get most recent live data backup
			restoreDB(where)
			testDB(where)
			self.down(where)
