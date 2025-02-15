from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import requests
import json
import os
import google.generativeai as genai
import re
from dotenv import load_dotenv

# Initialize Flask App and Database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'policygyaanissecure'

# Initialize database and migrations
db = SQLAlchemy(app)
migrate = Migrate(app, db)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

llm = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login if user is not authenticated

# User Model (Database model for storing user information)
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(200), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	profession = db.Column(db.String(100), nullable=False)
	age = db.Column(db.Integer, nullable=False)
	gender = db.Column(db.String(10), nullable=False)
	state = db.Column(db.String(100), nullable=False)

	def __repr__(self):
		return f'<User {self.name}>'

# Load user from session
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/policy_redirect/<string:policy_title>',methods=['POST','GET'])
@login_required
def policy_redirect(policy_title):
	prompt = f"For the policy {policy_title}, provide responses in the following format:\
	Policy Overview: Details of policy {policy_title},\
	Impact on You: Impact of {policy_title} on {current_user.profession},{current_user.gender},{current_user.age},{current_user.state}\
	History: History of policy {policy_title},\
	Key Benefits: Key benefits of policy {policy_title},\
	Challenges: Challenges of policy {policy_title}"
	print(prompt)
	response = llm.generate_content(prompt)
	res = response.text
	print(res)
	policy_overview = re.search(r"(?i)\*\*.*?Overview.*?\*\*\s*(.*?)(?=\n\s*\*\*|\Z)", res, re.DOTALL)
	impact_on_you = re.search(r"(?i)\*\*.*?Impact.*?\*\*\s*(.*?)(?=\n\s*\*\*|\Z)", res, re.DOTALL)
	history = re.search(r"(?i)\*\*.*?History.*?\*\*\s*(.*?)(?=\n\s*\*\*|\Z)", res, re.DOTALL)
	key_benefits = re.search(r"(?i)\*\*.*?Benefits.*?\*\*\s*(.*?)(?=\n\s*\*\*|\Z)", res, re.DOTALL)
	challenges = re.search(r"(?i)\*\*.*?Challenges.*?\*\*\s*(.*)", res, re.DOTALL)  # Last section
	policy_overview = policy_overview.group(1).strip() if policy_overview else "Not available"
	impact_on_you = impact_on_you.group(1).strip() if impact_on_you else "Not available"
	history = history.group(1).strip() if history else "Not available"
	key_benefits = key_benefits.group(1).strip() if key_benefits else "Not available"
	challenges = challenges.group(1).strip() if challenges else "Not available"
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
# Home page - Displays policies (mock data here for the example)
@app.route('/')
@login_required
def home():
	policies = [
		{"id": 1, "title": "PM Internship Scheme", "description": "Launched to provide young professionals with opportunities to work with various government departments, enhancing their skills and understanding of public administration. This initiative aims to bridge the gap between academic learning and practical experience for emerging professionals"},
		{"id": 2, "title": "BioE3 Policy", "description": "Introduced to promote the biotechnology sector, this policy offers incentives and support to professionals in the biotech industry, encouraging innovation and research. It aims to position India as a global leader in biotechnology by fostering a conducive environment for professionals in this field"},
		{"id": 3, "title": "Unified Pension Scheme", "description": "Expanded to include a broader range of professionals, this scheme ensures financial security for individuals across various sectors upon retirement. It addresses the diverse needs of professionals by providing a standardized pension system, promoting financial stability for retirees. "}
	]
	return render_template('home.html', policies=policies)

# Policy details page - Personalized impact based on current user
@app.route('/policy/<string:policy_title>')
@login_required
def policy_details(policy_title):
	prompt = f"For the policy {policy_title}, provide responses in the following format:\
	Policy Overview: Details of policy {policy_title},\
	Impact on You: Impact of {policy_title} on {current_user.profession},\
	History: History of policy {policy_title},\
	Key Benefits: Key benefits of policy {policy_title},\
	Challenges: Challenges of policy {policy_title}"
	print(prompt)
	response = llm.generate_content(prompt)
	res = response.text
	print(res)

@app.route('/internship',methods=['GET','POST'])
@login_required
def internship():
	return render_template("internship.html")

@app.route('/bioe3',methods=['GET','POST'])
@login_required
def bioe3():
	return render_template("bioe3.html")

@app.route('/index')
def index():
	return render_template("index.html")

# Registration Page - Users can register
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		# Get form data
		name = request.form['name']
		email = request.form['email']
		password = request.form['password']
		profession = request.form['profession']
		age = request.form['age']
		gender = request.form['gender']
		state = request.form['state']

		# Create a new user and add to the database
		new_user = User(name=name, email=email, password=password, profession=profession, age=age, gender=gender, state=state)
		db.session.add(new_user)
		db.session.commit()

		# Log the user in after successful registration
		login_user(new_user)

		return redirect(url_for('home'))  # Redirect to home after successful registration
	return render_template('register.html')

# Login Page - Users can log in
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		user = User.query.filter_by(email=email).first()

		if user and user.password == password:  # Simple password check, use hashed passwords in real apps!
			login_user(user)
			return redirect(url_for('home'))
		else:
			return "Invalid email or password", 401

	return render_template('login.html')

# Logout functionality
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(debug=True)
