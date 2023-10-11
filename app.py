#!/usr/bin/env python3

from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from database import Database

load_dotenv()

app = Flask(__name__)
jwt = JWTManager(app)

app.config["MONGO_URI"] = os.getenv("MONGODB_URI")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

Database().setup(app)


@app.route('/')
def index():
    return "Nada que ver aquí. Circulando, por favor"


import routes.users  # nopep8
import routes.todos  # nopep8


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
