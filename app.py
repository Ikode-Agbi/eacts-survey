from flask import Flask
from flask_mail import Mail
import os
from database import db
from config import Config
from data_tables.answer import Answer
from data_tables.question import Question
from data_tables.response import Response
from data_tables.survey import Survey 
from data_tables.section import Section
from routes.admin import admin_bp
from routes.take_survey import survey_bp 

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'dev-secret-key-change-in-production'

# Initialize Flask-Mail
mail = Mail(app)

# connect database to app
db.init_app(app)

# register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(survey_bp)

#create database for folder if it doesnt exist
database_folder = os.path.join(os.path.dirname(__file__), 'database')
uploads_folder = app.config['UPLOAD_FOLDER']

for folder in [database_folder, uploads_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# home route
@app.route('/')
def home():
    return """
    <h1>EACTS Survey System</h1>
    <p>System is running!</p>
    <a href='/admin'>Go to Admin Dashboard</a>
    """

# create database tables when app starts
with app.app_context():
    db.create_all()
    print("database tables created")

if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=False)