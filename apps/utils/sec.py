from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from typing import Dict, Set
import os
import secrets

SECRET_KEY = 'secret123'
SECURITY_PASSWORD_SALT = '#salt123'

VALID_API_TOKENS: Dict[str, Set] = {}

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, self=SECURITY_PASSWORD_SALT)

def confirm_token(token, exp=3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt=SECURITY_PASSWORD_SALT, max_age=exp)
    except:
        return False
    return email

def generate_api_token():
    return secrets.token_hex(32)

def store_api_token(user_id, token):
    VALID_API_TOKENS[user_id].add(token)

def authenticate_api_token(user_id, token):
    return token in VALID_API_TOKENS[user_id]
