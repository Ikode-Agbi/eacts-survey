import os 

"""
for all the settings for flask stored in one place such as seceret key,
upload limits, folder to store upload

"""

class Config: 

    SECRETE_KEY = 'dev-secrete-key-change-later'

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'eacts_survey.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # upload seetings 

    UPLOAD_FOLDER = 'upload'
    MAX_FILE_SIZE = 16 * 1024 * 1024 #16MB Max
    ALLOWED_FILE_TYPES = ['xlsx', 'xls']

    # email configuration 
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Your email
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Your app password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')