from __future__ import absolute_import, unicode_literals

import os
import smtplib
import ssl
from celery import Celery, current_app
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from utils.sec import generate_confirmation_token


# Celery config
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_BACKEND_URL = 'redis://localhost:6379/0'

mail_server_config = {}
mail_server_config['MAIL_SERVER'] = os.environ.get('SMTP_SERVER')
mail_server_config['MAIL_PORT'] = os.environ.get('SMTP_PORT', '587')
mail_server_config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
mail_server_config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail_server_config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_SENDER')


# Initialize extensions
app = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL, include=['tasks'])
app.conf.update(mail_server_config)

@app.task
def send_email(recv_email, sub, plaintext, html):
    mail_server_config = current_app.conf.mail_server_config
    with smtplib.SMTP(mail_server_config.get('MAIL_SERVER'), mail_server_config.get('MAIL_PORT')) as mail_server:
        message = MIMEMultipart('alternative')
        message["Subject"] = sub
        message["From"] = mail_server_config.get('MAIL_DEFAULT_SENDER')
        message["To"] = recv_email

        part1 = MIMEText(plaintext, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        context = ssl.create_default_context()

        # Try to login to the server and send email
        try:
            mail_server.ehlo()
            mail_server.starttls(context=context)
            mail_server.ehlo()
            mail_server.login(
                mail_server_config.get('MAIL_USERNAME'),
                mail_server_config.get('MAIL_PASSWORD')
            )
            mail_server.send_message(message)
        except Exception as ex:
            print(ex)
            return False
    
@app.task
def send_registration_email(user):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    subject = "Registration successful - Please verify your email address."
    plaintext = f"Welcome {user.display_name()}.\nPlease verify your email address by following this link:\n\n{confirm_url}"
    html = render_template('verification_email.html',confirm_url=confirm_url, user=user)
    send_email(user.email, subject, plaintext, html)

    