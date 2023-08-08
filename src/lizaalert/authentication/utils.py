import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText


def send_new_password(email, message):
    sender = os.getenv("EMAIL")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(message, "plain", "utf-8")
    msg["From"] = sender
    msg["To"] = email
    msg["Subject"] = Header("Восстановление пароля", "utf-8")

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        server.login(sender, password)
        server.send_message(msg)
        return "The message was sent successfully!"
    except Exception as ex:
        return f"{ex}\nCheck your email login or password please!"
