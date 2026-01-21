from unittest.mock import patch
from smtplib  import SMTP

from src.app.tests.fake import fake

from src.app.service.email import email

async def test_create_mail():
    text, subject, user_email = fake.text(), fake.text(30), fake.email()

    result = email.create_mail(text, type_text="plain", subject=subject, user_email=user_email)

    assert result["To"] == user_email
    assert result["Subject"] == subject
    assert result.get_payload()[0].get_payload() == text

@patch(f"{SMTP.__module__}.{SMTP.__name__}.{SMTP.login.__name__}")
@patch(f"{SMTP.__module__}.{SMTP.__name__}.{SMTP.sendmail.__name__}")
async def test_send_mail(login_mock, sendmail_mock):
    login_mock.return_value = None
    sendmail_mock.return_value = None
    
    user_email = fake.email(domain="gmail.com")
    
    await email.send_mail(user_email, fake.text())