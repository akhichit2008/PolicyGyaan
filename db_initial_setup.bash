cd src/
flask db init
flask db migrate -m "Initial Migration"
flask db upgrade
echo "Database Successfully Configured!!"
echo "Now Opening Application!!!"
python app.py