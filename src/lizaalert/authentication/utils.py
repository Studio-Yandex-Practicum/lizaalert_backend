import logging
import os
import random
import smtplib
import string
from email.header import Header
from email.mime.text import MIMEText


def get_new_password() -> str:
    """Generate new password for changin."""
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))


def send_new_password(email: str, message: str):
    """Send new password to client mail.

    Keywords arguments:
    email -- client mail
    message -- message text
    """
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
        logging.info(f"Temp password was sent to {email}")
        return True
    except smtplib.SMTPException as ex:
        logging.error(f"Can't send temp password to {email} - exception {str(ex)}")
        return False
