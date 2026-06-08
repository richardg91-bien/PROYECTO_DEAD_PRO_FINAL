from flask import Flask
import sqlite3
import os

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'clave_secreta'
    app.config['DATABASE'] = os.path.join('instance', 'database.db')

    from .routes import main
    app.register_blueprint(main)

    return app