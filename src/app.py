from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import requests
import json
import os
from google import genai
import re
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json

# Internal (Application) Modules
from utils import process_indices, load_default_policy, policy_filter
from __init__ import *
from models import User
from prompt_manager import PromptManager


app_config = AppConfig()
client = app_config.get_llm_client()
prompt_manager = PromptManager(client,model="gemini-2.5-flash")

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/policy_redirect/<string:policy_title>',methods=['POST','GET'])
@login_required
# current_user = [profession,gender,age,state]
def policy_redirect(policy_title):
    user = [current_user.profession,current_user.gender,current_user.age,current_user.state]
    res = prompt_manager.policy_redirect_prompt(policy_title,user)
    print(res)
    policy_overview,impact_on_you,history,key_benefits,challenges = policy_filter(res)
    print("Policy Overview: ",policy_overview)
    print("Impact: ",impact_on_you)
    return render_template(
        "policy.html",
        policy_title=policy_title,
        policy_overview=policy_overview,
        impact_on_you=impact_on_you,
        history=history,
        key_benefits=key_benefits,
        challenges=challenges
    )

@app.route('/profile')
@login_required
def profile():
	return render_template("profile.html",user=current_user)


@app.route('/')
@login_required
def home():
    policies = load_default_policy()
    prompt = f"""From this using the user's info as given :- {current_user.profession}, {current_user.state} {current_user.gender}, {current_user.age} just suggest me the indices from this policy list that I can display to this user :- {policies}. Dont return anything else only return a single line with indices thats all"""
    res = response = response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
	)
    res = res.text
    print(res)
    policy_indices = process_indices(res)
    pol = []
    for i in policy_indices:
        pol.append(policies[i])
    return render_template('home.html', policies=pol)


@app.route('/index')
def index():
	return render_template("index.html")

def allowed_file(filename):
	ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/about')
def about():
	return render_template('about.html')


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


if __name__=="__main__":
	app_config.run()