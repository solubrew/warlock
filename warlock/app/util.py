#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Flask@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''  #																	||
---  #																	||
<|(META)|>:  #															||
	DOCid:   #						||
	name: TIGR   #					||
	description: >  #													||
		Get Data from SQL Tables and Write to Local Store  #	||
	expirary: <[expiration]>  #											||
	version: <[version]>  #												||
	path: <[LEXIvrs]>  #												||
	outline: <[outline]>  #												||
	authority: document|this  #											||
	security: sec|lvl2  #												||
	<|(WT)|>: -32  #													||
''' #																	||
# -*- coding: utf-8 -*-#												||
#===========================Core Modules========================================||
from os.path import abspath, dirname, join
import operator, inspect
#===========================3rd Party Modules===================================||
from importlib import import_module#									||
from yaml import load as yload, dump as ydump#							||
try:#																	||
	from yaml import CLoader as Loader, CDumper as Dumper#				||
except:#																||
	from yaml import Loader, Dumper#									||
#============================Pheonix Modules====================================||

#============================Common Globals=====================================||
here = join(dirname(__file__),'')#												||
there = abspath(join('../../..'))#												||set path at pheonix level
version = '0.0.0.0.0.0'#														||
#===============================================================================||
def capitalize(term, pos):
	''' '''
	term = term[:1].upper()+term[1:]
	if log: print('TERM', term)
	return term
def collapse(params):#															||probably needs to go to util document
	'''Collapse Parameters from Default and Optional Arguments to a single tree#||
	'''#																		||
	p = params['dargs']#														||
	if params['oargs'] == None or params['oargs'] == '':#						||
		return p#																||
	for key in params['oargs'].keys():#											||
		p[key] = params['oargs'][key]#											||
	return p#																	||
def getYAML(path):
	with open(path, 'r') as doc:#										||
		dikt = yload(doc.read().replace('\t','  '), Loader=Loader)#		||
	return dikt
def funcify(thing):
	method_name = thing # set by the command line options
	possibles = globals().copy()
	possibles.update(locals())
	method = possibles.get(method_name)
	if not method:
		raise NotImplementedError("Method %s not implemented" % method_name)
	return method
def printClasses():
	'''Output Visible sturcture of each model'''
	for name, obj in inspect.getmembers(sys.modules[__name__]):
		if inspect.isclass(obj):
			if log: print(obj)
			if log: print(vars(obj))
def thingify(thing):
	'Import dotted path text and return the attribute/class'#		||
	if '.' in thing:#											||
		try:#														||
			module_path, class_name = thing.rsplit('.', 1)#	||
		except Exception as e:#									||
			m = 'Config.Modulize'
			d = thing
			if log: print(e,m,d)
	module = import_module(module_path)#							||
	try:#															||
		obj = getattr(module, class_name)#						||
	except AttributeError as e:#									||
		if log: print('Thingify Error',e)#												||
	return obj#													||


class IncludeLoader(Loader):
	"""	yaml.Loader subclass handles "!include path/to/foo.yml" directives in config
	files.  When constructed with a file object, the root path for includes
	defaults to the directory containing the file, otherwise to the current
	working directory. In either case, the root path can be overridden by the
	`root` keyword argument.
	When an included file F contain its own !include directive, the path is
	relative to F's location.
	Example:
		YAML file /home/frodo/one-ring.yml:
			---
			Name: The One Ring
			Specials:
				- resize-to-wearer
			Effects:
				- !include path/to/invisibility.yml

		YAML file /home/frodo/path/to/invisibility.yml:
			---
			Name: invisibility
			Message: Suddenly you disappear!
		Loading:
			data = IncludeLoader(open('/home/frodo/one-ring.yml', 'r')).get_data()
		Result:
			{'Effects': [{'Message': 'Suddenly you disappear!', 'Name':
				'invisibility'}], 'Name': 'The One Ring', 'Specials':
				['resize-to-wearer']}	"""
	def __init__(self, *args, **kwargs):
		super(IncludeLoader, self).__init__(*args, **kwargs)
		self.add_constructor('!include', self._include)
		if 'root' in kwargs:
			self.root = kwargs['root']
		elif isinstance(self.stream, file):
			self.root = os.path.dirname(self.stream.name)
		else:
			self.root = os.path.curdir
	def _include(self, loader, node):
		oldRoot = self.root
		filename = os.path.join(self.root, loader.construct_scalar(node))
		self.root = os.path.dirname(filename)
		data = yaml.load(open(filename, 'r'))
		self.root = oldRoot
		return data
class PermissonBuilder():
	def __init__(self):
		'''build out permissions based on configs override standard configs

		'''
