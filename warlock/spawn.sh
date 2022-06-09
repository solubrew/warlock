source /home/solubrew/ENVs/flaskAPP/bin/activate
export PYTHONPATH="${PYTHONPATH}:/home/solubrew/OPs/3_Work/opENGRg/3_Work/jobElfSys/actvPython/tskWarlock/1_DELTA/warlock/warlock"
rm app.db
flask fab create-admin << EOF
solubrew
solu
brew
dev@solutionsbrewer.com
EOF
python run.py
