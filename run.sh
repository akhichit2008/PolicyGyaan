pip install -r requirements.txt
cd src/
python -m flask db init
python -m flask db migrate
python -m flask db upgrade
python app.py