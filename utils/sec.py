from itsdangerous import URLSafeTimedSerializer
import os

SECRET_KEY = os.environ.get('SECRET_KEY')
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')


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