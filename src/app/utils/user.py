def del_security(*data: list[dict]) -> list[dict]:
    for value in data:
        value.pop("otp_enable")
        value.pop("password")
        value.pop("email")
    return list(data)