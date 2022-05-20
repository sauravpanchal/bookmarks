# Everytime this file will be imported automatcally when src module is loaded (i.e main entry point)

# by default flask assumes app is running in development server. Hence we will change it to development to debug it.
# cmd `set FLASK_ENV=development`
# cmd `set FLASK_APP=app`

from flask import Flask
import os

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config = True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY = os.environ.get("SECRET_KEy"),
        )
    else:
        app.config.from_mapping(test_config)
    
    @app.get("/")
    def index():
        return "Hello World !"

    @app.get("/hello")
    def get_hello():
        return {"Message": "Hello World!"}

    return app