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
from werkzeug.utils import secure_filename
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'policygyaanissecure'
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'UPLOAD_FOLDER')
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = SQLAlchemy(app)
migrate = Migrate(app, db)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

llm = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(200), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	profession = db.Column(db.String(100), nullable=False)
	age = db.Column(db.Integer, nullable=False)
	gender = db.Column(db.String(10), nullable=False)
	state = db.Column(db.String(100), nullable=False)
	profile_image = db.Column(db.String(200), nullable=True, default="default.jpg")

	def __repr__(self):
		return f'<User {self.name}>'


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

@app.route('/profile')
@login_required
def profile():
	return render_template("profile.html",user=current_user)


@app.route('/')
@login_required
def home():
	policies = [
        {
            "id": 1,
            "title": "PM Internship Scheme",
            "description": "Launched to provide young professionals with opportunities to work with various government departments, enhancing their skills and understanding of public administration. This initiative aims to bridge the gap between academic learning and practical experience for emerging professionals."
        },
        {
            "id": 2,
            "title": "BioE3 Policy",
            "description": "Introduced to promote the biotechnology sector, this policy offers incentives and support to professionals in the biotech industry, encouraging innovation and research. It aims to position India as a global leader in biotechnology by fostering a conducive environment for professionals in this field."
        },
        {
            "id": 3,
            "title": "New Income Tax Bill 2025",
            "description": "Introduced to replace the six-decade-old income tax law, this bill aims to simplify tax regulations and reduce litigation. Notably, it proposes granting tax authorities extensive powers to access taxpayers' electronic records, including emails and social media accounts, during investigations."
        },
        {
            "id": 4,
            "title": "Nuclear Energy Expansion Initiative",
            "description": "A strategic plan to significantly boost India's nuclear power capacity, with a goal of installing 100 gigawatts by 2047. This initiative includes over $2 billion in research funding and amendments to existing laws to attract investment, aiming to reduce emissions and provide consistent energy to millions of households."
        },
        {
            "id": 5,
            "title": "Labour Code Implementation and Social Security for Informal Workers",
            "description": "A policy focused on the swift enactment of labour reforms, emphasizing social security provisions for informal workers, including those in gig and platform sectors. The objective is to empower the workforce and stimulate economic growth through transformative measures."
        },
        {
            "id": 6,
            "title": "Union Budget 2025-2026",
            "description": "The annual financial statement outlining the government's economic policies and priorities for the fiscal year. Key highlights include tax reforms, infrastructure development plans, and various schemes aimed at boosting different sectors of the economy."
        },
        {
            "id": 7,
            "title": "Industrial Policy Reforms 2025",
            "description": "A comprehensive policy aimed at revitalizing India's manufacturing sector. It includes measures to attract foreign investment, enhance competitiveness, and create employment opportunities, aligning with the goal of making India a global manufacturing hub."
        },
        {
            "id": 8,
            "title": "Green Hydrogen Mission",
            "description": "Aimed at making India a global hub for green hydrogen production, this policy focuses on promoting renewable energy sources and reducing dependency on fossil fuels. The government has allocated significant funding to encourage R&D and industry participation."
        },
        {
            "id": 9,
            "title": "Digital India 2.0",
            "description": "An advanced phase of the Digital India initiative, this policy focuses on AI integration, digital literacy, and cybersecurity improvements to strengthen India's digital economy and governance framework."
        },
        {
            "id": 10,
            "title": "Agricultural Export Policy 2025",
            "description": "Designed to boost India's agricultural exports by providing incentives and removing trade barriers, this policy aims to make India a leading exporter of agri-products while ensuring food security."
        },
        {
            "id": 11,
            "title": "National Education Policy 2020",
            "description": "A comprehensive reform in the education sector, focusing on skill development, multidisciplinary learning, and integrating technology to make education more holistic and accessible."
        },
        {
            "id": 12,
            "title": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana",
            "description": "The world's largest government-funded healthcare program providing health insurance coverage up to ₹5 lakh per family per year for secondary and tertiary care hospitalization."
        },
        {
            "id": 13,
            "title": "Make in India 2.0",
            "description": "A renewed push to strengthen manufacturing, attract FDI, and generate employment in key sectors like defense, electronics, and renewable energy."
        },
        {
            "id": 14,
            "title": "Startup India Seed Fund Scheme",
            "description": "Aimed at supporting early-stage startups by providing financial assistance for proof of concept, prototype development, product trials, and market entry."
        },
        {
            "id": 15,
            "title": "Pradhan Mantri Fasal Bima Yojana",
            "description": "An agricultural insurance scheme designed to provide financial support to farmers in case of crop failure due to natural calamities, pests, or diseases."
        },
        {
            "id": 16,
            "title": "Smart Cities Mission",
            "description": "An urban renewal initiative to develop 100 smart cities across India, focusing on sustainable infrastructure, digital services, and improved quality of life."
        },
        {
            "id": 17,
            "title": "Beti Bachao Beti Padhao",
            "description": "A flagship program aimed at addressing the declining child sex ratio and promoting education and empowerment of the girl child in India."
        }
    ]

	prompt = f"""From this using the user's info as given :- {current_user.profession}, {current_user.state} {current_user.gender}, {current_user.age} just suggest me the indices from this policy list that I can display to this user :- {policies}. Dont return anything else only return a single line with indices thats all"""
	res = llm.generate_content(prompt)
	res = res.text
	print(res)
	res = json.loads(res)
	pol = []
	for i in res:
		pol.append(policies[i])
	return render_template('home.html', policies=pol)


@app.route('/policy/<string:policy_title>/<string:policy_description>')
@login_required
def policy_details(policy_title,policy_description):
	prompt = f"For the policy {policy_title}, (description : {policy_description}), provide responses in the following format:\
	Policy Overview: Details of policy {policy_title},\
	Impact on You: Impact of {policy_title} on {current_user.profession},\
	History: History of policy {policy_title},\
	Key Benefits: Key benefits of policy {policy_title},\
	Challenges: Challenges of policy {policy_title}\
	(remeber to address as 'you' instead of he, him or any other pronouns)"
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

def allowed_file(filename):
	ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/about')
def about():
	return render_template('about.html')


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
		profile_picture = request.files['profile_picture']
		filename = "default.jpg"  # Default profile picture
		if profile_picture and allowed_file(profile_picture.filename):
			filename = secure_filename(f"user_{email}.jpg")  # Unique filename
			file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			profile_picture.save(file_path)
		else:
			filename = "default.jpg"  # Default profile image
		new_user = User(name=name, email=email, password=password, profession=profession, age=age, gender=gender, state=state,profile_image=filename)
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
	app.run(host="127.0.0.1",port=8000,debug=True)
