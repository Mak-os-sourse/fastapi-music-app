import aiosmtplib

from src.app.config import settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Email():
    def create_mail(self, text: str, type_text: str, subject: str = "", user_email: str = ""):
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = settings.SENDER
        msg["To"] = user_email

        body = MIMEText(text, type_text)
        msg.attach(body)

        return msg

    async def send_mail(self, user: str, text: str):
        smtp = aiosmtplib.SMTP(hostname=f"smtp.{user.split('@', -1)[1]}", port=587)
        await smtp.connect()
        await smtp.login(settings.SENDER, settings.PASSWORD)
        await smtp.sendmail(settings.SENDER, [user], text)
        await smtp.quit()

email = Email()