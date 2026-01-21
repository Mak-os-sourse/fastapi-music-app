def jsonable_encoder(obj: object) -> dict:
    data = {}
    for key, value in obj.__dict__.items():
        if "_" == key[0] or "__" in key:
            continue
        else:
            data[key] = value
    return data