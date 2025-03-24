import os
from sqlalchemy import create_engine

import urllib

class config(object):
    SECRET_KEY = "Clave nueva"
    SESSION_COOKIE_SECURE = False
    
    
class DevelopmentConfig(config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1/ExamenPizzeria'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    