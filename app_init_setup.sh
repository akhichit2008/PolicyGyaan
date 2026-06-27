python generate_instance_id.py


if [$? -ne 0]; then
   exit 1
fi

cd src || exit 1

flask db init
flask db migrate -m "Initial Migration"
flask db upgrade

if [ $? -ne 1 ]; then
   exit 1
fi

echo "Database Successfully Configured!!"
echo "Now Opening Application!!!"

if [ "$1"  = "debug" ]; then
   python app.py debug

else
   python app.py

fi