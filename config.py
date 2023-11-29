import os
from dotenv import load_dotenv

basedur = os.path.abspath(os.path.dirname(__file__))

class Config:
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True

    SECRET_KEY = os.getenv('SECRET_KEY', default='test1234')

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', default='')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', default='')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME', default='')
    MAIL_SUPPRESS_SEND = False

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    RESULT_BACKEND = os.getenv('RESULT_BACKEND')

    MONGO_URI = os.getenv("MONGO_URI","mongodb+srv://dangerankur56:Hackgodrs10@cluster007.vhrjaqp.mongodb.net/?retryWrites=true&w=majority")
    MONGO_DBNAME = os.getenv("MONGO_DBNAME","deltafunctions")

    OAUTH2_PROVIDERS = os.getenv('OAUTH2_PROVIDERS', {
        # GitHub OAuth 2.0 documentation:
        # https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
        'github': {
            'client_id': '0ad9e1a6c62771c2b7c2',
            'client_secret': 'cebc7652fe1016beeda7b821ee653f2f62087e2c',
            'authorize_url': 'https://github.com/login/oauth/authorize',
            'token_url': 'https://github.com/login/oauth/access_token',
            'userinfo': {
                'url': 'https://api.github.com/user',
                'email': 'https://api.github.com/user/emails',
            },
            'scopes': ['user:email,repo,deployment,read:user'],
        },
    })

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True

class ProductionConfig(Config):
    FLASK_ENV = 'production'