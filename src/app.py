from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import re
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json

# Internal (Application) Modules
from utils import load_default_policy,allowed_file,policy_filter
from __init__ import *
from auth import *
from prompt_manager import PromptManager


app_config = AppConfig()
client = app_config.get_llm_client()
prompt_manager = PromptManager(client,model="gemini-2.5-flash")

@app.route('/policy_redirect/<string:policy_title>',methods=['POST','GET'])
@login_required
# current_user = [profession,gender,age,state]
def policy_redirect(policy_title:str):
    user = [current_user.profession,current_user.gender,current_user.age,current_user.state]
    res = prompt_manager.policy_redirect_prompt(policy_title,user)
    policy_overview,impact_on_you,history,key_benefits,challenges = policy_filter(res)

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
    user = [current_user.profession,current_user.gender,current_user.age,current_user.state]
    pol = prompt_manager.load_dashboard_prompt(policies,user)

    return render_template('home.html', policies=pol)

@app.route('/index')
def index():
	return render_template("index.html")

@app.route('/about')
def about():
	return render_template('about.html')

if __name__=="__main__":
	app_config.run()