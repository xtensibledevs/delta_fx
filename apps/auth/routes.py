from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import bcrypt
import jwt
from functools import wraps
from datetime import datetime, timedelta
from celery import Celery
from apps.auth.models.user import User
from auth.forms import RegisterForm, LoginForm
from utils.email import send_registration_email
from utils.sec import confirm_token, generate_api_token, generate_confirmation_token, store_api_token
from utils.url import is_safe_url

from app import db

blueprint = Blueprint('auth', __name__)


@blueprint.route('/users', methods=['POST'])
def register_user():
    login_form = RegisterForm(request.form)
    if 'register' in request.form:
        # extract the data
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        email = request.form['email'].strip()
        password = request.form['pass'].strip()

        # check if users exists
        existing_user = db.users.find_one({'email': email}, {'_id': 0})

        if existing_user is None:
            # logout the existing user
            logout_user()
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            new_user = User(first_name, last_name, email)
            user_data_to_save = new_user.dict()
            user_data_to_save['password'] = hashpass

            if db.users.insert_one(user_data_to_save):
                login_user(new_user)
                send_registration_email(new_user)
                return jsonify({'message': 'User created successfully and logged in'}), 201
            else:
                return jsonify({'message': 'Failed to create user'}), 500
            
        return 
    
    return jsonify({'message': 'Invalid request'}), 400

@blueprint.route('/cmd/login', methods=['GET'])
def cmd_login():
    mongodb = current_app.extensions['MONGO_CLIENT'].get_database('deltafunctions')
    if request.methods == 'GET':
        email = request.json['email'].strip()
        password = request.json['pass'].strip()
        try:
            user_data = mongodb.users.find_one({'email': email})
            if user_data and bcrypt.checkpw(user_data['password'], password):
                payload = {'exp': datetime.utcnow() + timedelta(weeks=4),'iat': datetime.utcnow(), 'sub': user_data['id']}
                jwt_token = jwt.encode(payload, current_app.secret_key, algorithm='HS256')
                return jsonify({
                    'status': 'success',
                    'message': 'success',
                    'token': jwt_token
                }), 200
            else:
                return jsonify({'status': 'fail', 'message': 'User does not exist'}), 404
        except Exception as ex:
            return jsonify({'status': 'fail', 'message': str(ex)}), 500


@blueprint.route('/login', methods=['GET'])
def login():
    mongodb = current_app.extensions['MONGO_CLIENT'].get_database('deltafunctions')
    if request.method == 'GET':
        email = request.form['email'].strip()
        password = request.form['pass'].strip()

        if current_user.is_authenticated:
            return jsonify({'message': 'A user is already logged in, logout first.'}), 400
    
        # Get the user from the database
        user_data = mongodb.users.find_one({'email': email}, {'_id': 0})
        # compare passwords
        if user_data and bcrypt.checkpw(user_data['password'], password):
            # Create the user object to login (password is not stored in the session)
            user = User.make_from_dict(user_data)
            login_user(user)

            next_url = request.args.get('redirect_to')
            if next_url:
                if not is_safe_url(next_url):
                    return jsonify({'message': 'redirect_to provided is not safe'}), 400
                # redirect to the next url
                return redirect(next_url)
            
            return jsonify({'message': 'User logged in successfully'}), 200
    
    return jsonify({'message': 'Invalid request'}), 400

@app.task
def send_registration_email(user):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    subject = "Registration successful - Please verify your email address."
    plaintext = f"Welcome {user.display_name()}.\nPlease verify your email address by following this link:\n\n{confirm_url}"
    html = render_template('verification_email.html',confirm_url=confirm_url, user=user)
    send_email(user.email, subject, plaintext, html)

@blueprint.route('/config/<token>', methods=['GET'])
def confirm_email(token):
    mongodb = current_app.extensions['MONGO_CLIENT'].get_database('deltafunctions')
    logout_user()
    try:
        email = confirm_token(token)
        if email:
            if mongodb.users.update_one({"email": email}, {"$set": {"verified": True}}):
                return render_template('confirm.html', success=True)
    except:
        return render_template('confirm.html', success=False)
    else:
        return render_template('confirm.html', sucess=False)
    
# Verification email
@blueprint.route('/verify', methods=['POST'])
@login_required
def send_verification_email():
    if current_user.verifed == False:
        send_registration_email(current_user)
        return "Verification email send"
    else:
        return "Your email address is already verified"
    
@blueprint.route('/profile', methods=['GET'])
@login_required
def profile():
    mongodb = current_app.extensions['MONGO_CLIENT'].get_database('deltafunctions').get_database('deltafunctions')
    projects = mongodb.projects.find({"user_id": current_user.id, "deleted": False}).sort("timestamp", -1)
    deployments = {}
    for project in projects:
        deployments[project] = mongodb.deployments.find({"project_id": project.id, "retired": False}).sort("timestamp", -1)

    return render_template('profile.html', projects=projects, deployments=deployments, username=current_user.username, display_name=current_user.display_name())


@blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@blueprint.route('/generate-client-token', methods=['POST'])
@login_required
def generate_token():
    new_token = generate_api_token()
    store_api_token(current_user.id, new_token)
    return jsonify({'token': new_token})