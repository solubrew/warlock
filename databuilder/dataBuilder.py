#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''  #																			||
---  #																			||
<(META)>:  #																	||
	DOCid:   #								||
	name:   #														||
	description: >  #															||
		build initilzation data and insert into database
		leverage matrix and looping from subtrix module

		combine config into subtrix? globally?
		recreate a yaml openenr in subtrix and leverage this in config
		confine config to more session and bear based integration  #			||
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
from os.path import abspath, dirname, join#										||
#===============================================================================||
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
#===============================================================================||
from fxsquirl.orgnql import fonql, yonql
#========================Common Globals=========================================||
here = join(dirname(__file__),'')#												||
there = abspath(join('../../..'))#												||set path at pheonix level
where = abspath(join(''))#														||set path at pheonix level
version = '0.0.0.0.0.0'#														||
#===============================================================================||
def addDATA():
	'''Leverage SQLAlchemy to create entries into the app database to
		initiliaze datasets
		3-5 entries for dev
		50-100 entries for testing
		a prepopulation production route
		leverage datavein as well
		'''
	path = f'{where}/z-data_'
	rdr = fonql.doc(path).read()
	db = 'sqlite:///home/solubrew/Design/creAppSys/3_Work/1_DELTA/base_jyask_app/test.db'
	engine = create_engine(db)
	meta = MetaData()
	while True:
		data = next(rdr, None)
		if data == None:
			break
		for path in data.paths:
			fdata = next(yonql.doc(path).read()).dikt
			if fdata == None:
				continue
			for model in fdata.keys():
				cols = []
				columns = list(fdata[model].keys())
				dtype = ''
				for col in columns:
					cols.append(Column(col, dtype, primary_key=True))
				table = Table(name, meta, *cols)
				meta.create_all(engine)
				if not isintance(data.dikt[model][columns[0]], list):
					data.dikt[model][columns[0]] = [data.dikt[model][columns[0]]]
				records = []
				cnt = 0
				for v in data.dikt[model][columns[0]]:
					cnt += 1
					record = {columns[0]: v}
					for col in columns[1:]:
						record[col] = columns[col][cnt]
					records.append(record)
				conn = engine.connect()
				result = conn.execute(table.insert(), records)
if __name__ == '__main__':
	addDATA()
