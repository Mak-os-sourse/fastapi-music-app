import bcrypt, random, uuid, jwt, redis
from datetime import datetime, timezone, timedelta

def hash_pw(password: str) -> str:
    hash_str = str(bcrypt.hashpw(password.encode(), bcrypt.gensalt()))
    hash_str = hash_str.replace("b", "", 1).replace("'", "", -1)
    return hash_str


def create_tokens(username, password, secret_key) -> dict:
    refresh = jwt.encode({"jti": str(uuid.uuid4()),
                          "exp": datetime.now(timezone.utc) + timedelta(days=30),
                          "username": username,
                          "password": password},
                         secret_key, algorithm="HS256")
    access = jwt.encode({"jti": str(uuid.uuid4()),
                         "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
                         "username": username,
                         "password": password},
                        secret_key, algorithm="HS256")

    return {"access": access, "refresh": refresh}

def decode_token(token: str, secret_key):
    try:
        data = jwt.decode(token, secret_key, algorithms="HS256")

        return data
    except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return None

def gen_totp(length: int):
    totp = ""

    for i in range(length):
        totp += str(random.randint(0, 9))

    return totp