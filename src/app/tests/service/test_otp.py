import pyotp

from src.app.config import settings
from src.app.service.otp import gen_otp, verifi_otp

base32 = pyotp.random_base32()

async def test_gen_otp():
    code, base32 = gen_otp()
    
    totp = pyotp.TOTP(base32, digits=settings.LEN_OTP_CODE, interval=settings.LIFE_OTP_CODE)
    
    assert totp.verify(code)

async def test_verify_otp():
    totp = pyotp.TOTP(base32, digits=settings.LEN_OTP_CODE, interval=settings.LIFE_OTP_CODE)
    code = totp.now()
    
    assert verifi_otp(code, base32)