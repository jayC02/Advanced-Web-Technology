import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-wont-ever-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 10
    UPLOAD_FOLDER = '/app/static/profile_pics'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    ADMINS = ['jayveercha17@gmail.com']
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'jayveerchall17@gmail.com'
    MAIL_PASSWORD = '4h7gbvjfrf8'
