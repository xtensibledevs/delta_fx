import os
from flask import url_for, render_template
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from utils.sec import generate_confirmation_token


def send_email(recv_email, sub, plaintext, html):
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    PORT = os.environ.get('EMAIL_PORT')
    SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
    PASSWORD = os.environ.get('EMAIL_PASSWORD')

    message = MIMEMultipart('alternative')
    message["Subject"] = sub
    message["From"] = SENDER_EMAIL
    message["To"] = recv_email

    part1 = MIMEText(plaintext, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()

    # Try to login to the server and send email
    try:
        server = smtplib.SMTP(SMTP_SERVER, PORT)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(SENDER_EMAIL, PASSWORD)
        server.send_message(message)
    except Exception as ex:
        print(ex)
        return False
    finally:
        server.quit()
        return True
    

def send_registration_email(user):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    subject = "Registration successful - Please verify your email address."
    plaintext = f"Welcome {user.display_name()}.\nPlease verify your email address by following this link:\n\n{confirm_url}"
    html = render_template('verification_email.html',confirm_url=confirm_url, user=user)
    send_email(user.email, subject, plaintext, html)

    