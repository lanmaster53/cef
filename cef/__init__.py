from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from queue import Queue
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
DEBUG = True
SECRET_KEY = 'dosentmatter'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'cef.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
CREDS_PATH = '/Users/lanmaster/Desktop/cors-exploit/creds.txt'

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

# streaming setup

attack_queue = Queue()
result_queue = Queue()

import cef.views

# manage

'''
import cef
cef.drop_db()
cef.init_db()
cef.pop_db()
'''

def init_db():
    db.create_all()
    print('Database initialized.')

def pop_db():
    from cef.models import Attack
    a = Attack(
        method='POST',
        url='https://cody-juiceshop.herokuapp.com/rest/user/login',
        payload_exp="json.dumps({'email':u,'password':p})",
        content_type='application/json',
        success='"token":',
        fail='Invalid email or password.',
    )
    db.session.add(a)
    db.session.commit()
    print('Database populated.')

def drop_db():
    db.drop_all()
    print('Database dropped.')
