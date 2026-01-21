import pyotp

from src.app.config import settings

def gen_otp() -> tuple[str, str]:
    base32 = pyotp.random_base32()
    return pyotp.TOTP(base32, digits=settings.LEN_OTP_CODE, interval=settings.LIFE_OTP_CODE).now(), base32

def verifi_otp(code: str, base32: str):
    totp = pyotp.TOTP(base32, digits=settings.LEN_OTP_CODE, interval=settings.LIFE_OTP_CODE)

    if totp.verify(code):
        return True
    else:
        return False
