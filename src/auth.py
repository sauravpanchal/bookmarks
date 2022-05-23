import json
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity

from src.consts.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from src.database import User, db

auth = Blueprint("auth", 
                __name__, 
                url_prefix = "/api/v1/auth")

@auth.post("/register")
def register():
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    if len(password) < 10:
        return jsonify({"error": "Password is less than 10 characters"}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({"error": "Username is less than 3 characters"}), HTTP_400_BAD_REQUEST
    
    if not username.isalnum() or " " in username:
        return jsonify({"error": "Username should be alphanumeric with no spaces"}), HTTP_400_BAD_REQUEST
    
    if User.query.filter_by(username = username).first() is not None:
        return jsonify({"error": "Username is already registered !"}), HTTP_409_CONFLICT

    if not validators.email(email):
        return jsonify({"error": "Email is not  valid"}), HTTP_400_BAD_REQUEST
    
    if User.query.filter_by(email = email).first() is not None:
        return jsonify({"error": "Email is already registered !"}), HTTP_409_CONFLICT

    pswd_hash = generate_password_hash(password)
    user = User(username = username, password = pswd_hash, email = email)
    db.session.add(user)
    db.session.commit()

    return jsonify({
                    "message": "User created !",
                    "user": {
                                "username": username,
                                "email": email,
                            }
                    }), HTTP_201_CREATED

@auth.post("/login")
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    user = User.query.filter_by(email = email).first()

    if user:
        correct = check_password_hash(user.password, password)

        if correct:
            refresh = create_refresh_token(identity = user.id)
            access = create_access_token(identity = user.id)

            return jsonify({
                            "user": {
                                        "refresh": refresh,
                                        "access": access,
                                        "username": user.username,
                                        "email": user.email,
                                    }
                          }), HTTP_200_OK
    return jsonify({"error": "Incorrect credentials"}), HTTP_401_UNAUTHORIZED

@auth.get("/me")
@jwt_required() # it requires authorization token header or else will throw missing authorization header
def me():
    # import pdb
    # pdb.set_trace()   => get_jwt_identity() gives what identity was encoded for the user 
    user_id = get_jwt_identity()
    user = User.query.filter_by(id = user_id).first()

    return jsonify({
                    "username": user.username,
                    "email": user.email
                  }), HTTP_200_OK
    # return {"user": "me"}