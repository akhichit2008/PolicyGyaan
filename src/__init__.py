import os
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from google import genai
from flask_login import LoginManager
import sys


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class AppConfig:
    def __init__(self):
        load_dotenv()
        UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'UPLOAD_FOLDER')
        SECRET_KEY = os.getenv("SECRET_KEY")
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
        self.app_name = "PolicyGyaan-V2"
        self.instance_id = os.getenv("APP_INSTANCE_ID")
        self.port = os.getenv("APPLICATION_PORT")
        self.host = os.getenv("APPLICATION_HOST")
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        

        app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    def get_llm_client(self):
        return self.client 

    def run(self):
        print(f"Application Running : {self.app_name} @ {self.instance_id}")
        if len(sys.argv) == 1:
            debug = False
        else:
            if sys.argv[1].lower() == "debug":
                debug = True
        app.run(host=self.host,port=self.port,debug=debug)