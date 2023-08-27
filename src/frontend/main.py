# Standard imports
import random
import os, sys
import socket 
from datetime import timedelta
from threading import Thread
import urllib.request


# Flask related imports
from flask import Flask, session, request, render_template, url_for, redirect
from flask_qrcode import QRcode
from flask_session import Session
from flask_socketio import SocketIO
import flask_monitoringdashboard as dashboard




def get_session_id():
    return session.get("session-id", None)

def healthcheck():
    while True:
        try:
            urllib.request.urlopen("https://hc-ping.com/" + config.HEALTHCHECK_UUID_FRONTEND, timeout=10)
        except socket.error as e:
            print("Healthcheck ping failed: %s" % e)
        time.sleep(10)




# Add project root folder to PATH
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.frontend import config


# The app object
app = Flask(__name__)

# Session related configuration
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=30)

# Make app object available in other files
app.app_context().push()

# Flask Extensions
# - QR-code generation
QRcode(app)
# - Sessions (based on cookies mmm..)
Session(app)
# - Async socket io
socketio = SocketIO(app)
# - Dashboard
dashboard.config.init_from(file='./config.cfg')
dashboard.config.group_by = get_session_id
dashboard.bind(app)

# Import routes
from routes.index_routes import *
from routes.qr_routes import *
from routes.movie_tinder_routes import *
from routes.result_routes import *

# Register blueprints
app.register_blueprint(index_blueprint)
app.register_blueprint(qr_blueprint)
app.register_blueprint(movie_tinder_blueprint)
app.register_blueprint(result_blueprint)

t = Thread(target=healthcheck)
t.start()










    
