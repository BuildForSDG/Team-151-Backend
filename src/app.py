import json
import logging
import sys

import bcrypt
from flask import Flask, jsonify, request
from flask_jwt import JWTError
from flask_restful import Api
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from security import authenticate, identity
from src import google_auth
from src.models.user import UserModel
from src.models.role import RoleModel

from src.resources.permission import PermissionRegister, PermissionGet
from src.resources.role import RoleRegister, RoleGet
from src.resources.role_permission import RolePermissionRegister, RolePermissionGet
from src.resources.user import UserRegister, UserGet
from src.google_auth import logout
from src.facebook_oauth import facebook_login, facebook_callback
from src.google_auth import google_auth_redirect
from src.resources.user_role import UserRoleRegister, UserRoleGet
import os

import flask
import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from flask import jsonify

app = Flask(__name__)

# local
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Masaki2017$$@localhost/okoa_farmer_db'

# server
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://b2b1802e9376f5:91ac6855@us-cdbr-east-06.cleardb.net/okoa_farmer_db?charset=utf8mb4'
#server
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://b2b1802e9376f5:91ac6855@us-cdbr-east-06.cleardb.net/heroku_e9e0456b7084334?charset=utf8mb4'

# travis
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/okoa_farmer_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JWT_SECRET_KEY'] = '#^#%^%&#BgdvttkkgyDDT&*%$'  # to encode cookies
api = Api(app)

#log system errors
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

jwt = JWTManager(app)
# jwt = JWT(app, authenticate, identity)


@app.errorhandler(JWTError)
def auth_error_handler(err):
    return jsonify({'message': 'Could not authorize. Did you include a valid Authorization header?'}), 401


# Routes
api.add_resource(UserRegister, '/register')
api.add_resource(UserGet, '/register/get')
api.add_resource(PermissionRegister, '/permissions')
api.add_resource(PermissionGet, '/permissions/get')
api.add_resource(RoleRegister, '/roles')
api.add_resource(RoleGet, '/roles/get')
api.add_resource(UserRoleRegister, '/user/roles')
api.add_resource(UserRoleGet, '/user/roles/get')
api.add_resource(RolePermissionRegister, '/role/permissions')
api.add_resource(RolePermissionGet, '/role/permissions/get')


@app.route("/")
def index():
    return """
    <a href="/fb-login">Login with Facebook</a>
    <a href="/google/login">Login with Google</a>
    """


@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username:
            return 'Missing Username', 400
        if not password:
            return 'Missing password', 400

        user = UserModel.query.filter_by(username=username).first()
        if not user:
            return 'User Not Found!', 404

        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # access_token = create_access_token(identity={"username": username})
            access_token = create_access_token(identity={"username": username, "password": password})
            return {"access_token": access_token}, 200
        else:
            return 'Invalid Login Info!', 400
    except AttributeError:
        return 'Provide a Username and Password in JSON format in the request body', 400


@app.route('/google/login')
def google_login():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        return jsonify({'user_info': json.dumps(user_info, indent=4), 'message': 'You have logged in successfully'})

    return jsonify({'message': 'You are not currently logged in.'})


@app.route('/google/auth')
def goog_redirect():
    google_auth_redirect()


@app.route('/google/logout')
def signOutUser():
    if google_auth.is_logged_in():
        logout()
    return jsonify({'message': 'You are not currently logged in.'})


@app.route("/kujuana", methods=['GET'])
@jwt_required
def testing_things():
    return "Testing tings!!!!!!"


#############################################START OF FACEBOOK OAUTH #################################################

# Your ngrok url, obtained after running "ngrok http 5000"
URL = "https://okoafarmer.herokuapp.com"
# URL = "https://8b335cb8a43d.ngrok.io"

FB_CLIENT_ID = os.environ.get("FB_CLIENT_ID")
FB_CLIENT_SECRET = os.environ.get("FB_CLIENT_SECRET")

FB_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

FB_SCOPE = ["email"]

# This allows us to use a plain HTTP callback
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


# app = flask.Flask(__name__)

@app.route("/fb-login")
def facebook_login():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, redirect_uri=URL + "/fb-callback", scope=FB_SCOPE
    )
    authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)
    print('apa kwa login')
    return flask.redirect(authorization_url)
    # return jsonify(authorization_url)


@app.route("/fb-callback")
def facebook_callback():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, scope=FB_SCOPE, redirect_uri=URL + "/fb-callback"
    )

    # we need to apply a fix for Facebook here
    facebook = facebook_compliance_fix(facebook)

    facebook.fetch_token(
        FB_TOKEN_URL,
        client_secret=FB_CLIENT_SECRET,
        authorization_response=flask.request.url,
    )

    # Fetch a protected resource, i.e. user profile, via Graph API
    facebook_user_data = facebook.get(
        "https://graph.facebook.com/me?fields=id,name,email,picture{url}"
    ).json()

    email = facebook_user_data["email"]
    name = facebook_user_data["name"]
    picture_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")

    return jsonify({'name': name, 'email': email, 'img': picture_url, 'message': 'You have logged in successfully'})


#############################################END OF FACEBOOK OAUTH #################################################


if __name__ == "__main__":
    from src.models.Model import db

    db.init_app(app)

    app.run(host='0.0.0.0', port=5000, debug=True)
