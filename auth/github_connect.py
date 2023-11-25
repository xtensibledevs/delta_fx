import os
import secrets
import requests
from urllib.parse import urlencode
from flask import Blueprint, abort, flash, request, jsonify, redirect, url_for, render_template, current_app, session
from flask_login import current_user, login_user
from auth.models.user import User

blueprint = Blueprint('ghconnect', __name__)


@blueprint.route('/authorize/github')
def oauth2_authorize():
    provider = 'github'
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # generate a random string for the state param
    session['oauth2_state'] = secrets.token_urlsafe(16)

    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_url': url_for('ghconnect.oauth2_callback', provider=provider, _external=True),
        'response_type': 'code',
        'scope': ''.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    return redirect(provider_data['authorize_url'] + '?' + qs)


@blueprint.route('/callback/github')
def oauth2_callback():
    mongo = current_app.extensions['MONGO_CLIENT']
    provider='github'
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # if there was an auth error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
            return redirect(url_for('index'))
    
    # make sure that the state paramater matches the one we created in auth request
    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    # make sure that the auth code is present
    if 'code' not in request.args:
        abort(401)

    # exchange the authorization code for an access token
    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_url': url_for('ghconnect.oauth2_callback', provider=provider, _external=True),
    }, headers={'Accept': 'application/json'})

    if response.status_code != 200:
        abort(401)

    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    # use the access token to get the user's email address
    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })

    if response.status_code != 200:
        abort(401)

    email = provider_data['userinfo']['email'](response.json())
    username = provider_data['userinfo']['username'](response.json())

    # find or create the user in the database
    user = mongo.db.users.find_one({"email": email})
    if user is None:
        user = User(email=email, username=username, verified=True)
        mongo.db.users.insert_one(user.dict())

    # login the user
    login_user(user)
    return redirect(url_for('index'))
