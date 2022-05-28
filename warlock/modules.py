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
#============================Common Globals=====================================||
here = join(dirname(__file__),'')#												||
there = abspath(join('../../..'))#												||set path at pheonix level
version = '0.0.0.0.0.0'#														||
log = True
#===============================================================================||
pxcfg = join(abspath(here), 'modules.yaml')
def newModule(name):
	''' '''
	path = join(abspath(here, f'app/modules/{name}')
	cfg = config.instruct(pxcfg).load().dikt
	params = {'model': model, 'view': view, 'module_name': name}
	files = subtix.instruct(cfg['files'], params).run()[0]
	for f in cfg.keys():
		template = cfg[f]['template']
		pathf = f'{path}/{f}'
		with yonql.doc(pathf) as doc:
			doc.write(data)
