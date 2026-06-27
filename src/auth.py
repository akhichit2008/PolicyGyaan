from __init__ import app,db,login_manager
from models import User
from flask import request,redirect,url_for,render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from utils import allowed_file

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		password = request.form['password']
		profession = request.form['profession']
		age = request.form['age']
		gender = request.form['gender']
		state = request.form['state']
		profile_picture = request.files['profile_picture']
		filename = "default.jpg"
		if profile_picture and allowed_file(profile_picture.filename):
			filename = secure_filename(f"user_{email}.jpg")
			file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			profile_picture.save(file_path)
		else:
			filename = "default.jpg"
		new_user = User(name=name, email=email, password=password, profession=profession, age=age, gender=gender, state=state,profile_image=filename)
		db.session.add(new_user)
		db.session.commit()
		login_user(new_user)

		return redirect(url_for('home')) 
	return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		user = User.query.filter_by(email=email).first()

		if user and user.password == password:
			login_user(user)
			return redirect(url_for('home'))
		else:
			return "Invalid email or password", 401

	return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))
