from flask_mail import Message
from app import mail
from flask import render_template
from flask import current_app


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients, html=html_body)
    msg.html = html_body
    print("Message:", msg)
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        '[ComeCeCeMe] Reset Your Password',
        sender='reset_password@comececeme.com',
        recipients=[user.email],
        html_body=render_template('admin/email/reset_password.html', user=user, token=token)
        )