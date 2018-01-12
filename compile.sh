#/bin/sh
pip install --editable .
export FLASK_APP=shelfy.py
cd shelfy
flask run

