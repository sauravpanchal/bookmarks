# Everytime this file will be imported automatcally when src module is loaded (i.e main entry point)

# by default flask assumes app is running in development server. Hence we will change it to development to debug it.
# cmd `set FLASK_ENV=development`
# cmd `set FLASK_APP=app` or for this file to run 

from flask import Flask, redirect, jsonify
import os
from src.auth import auth
from src.bookmarks import bookmarks
from src.consts.status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.database import db, Bookmarks
from flask_jwt_extended import JWTManager

from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config = True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY = os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS = False,
            JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY"),

            SWAGGER = {
                        "title": "Bookmarks API",
                        "UI Version": 3,

                      }
        )
    else:
        app.config.from_mapping(test_config)
    
    db.app = app
    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    Swagger(app, config = swagger_config, template = template)

    # generate `bookmarks.db` by cmd `db.create_all()`
    # to delete db use `bookmars.db`

    # param should be <placeholder> not explicit parameter
    @app.get("/<short_url>")
    @swag_from("./docs/short_url.yaml") 
    def short_url_to_url(short_url):
        bookmark = Bookmarks.query.filter_by(short_url = short_url).first_or_404()

        if bookmark:
            bookmark.visits += 1
            db.session.commit()

            return redirect(bookmark.url) 

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({"error": "Not found !"}), HTTP_404_NOT_FOUND
    
    # to check server side error handling change flask environment to production
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({"error": "It's not you, It's us ... & we are working on this issue !"}), HTTP_500_INTERNAL_SERVER_ERROR

    return app