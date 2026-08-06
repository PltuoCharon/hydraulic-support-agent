def ok(data=None, msg="success"):
    return {"code": 0, "data": data, "msg": msg}

def fail(msg, code=1):
    return {"code": code, "data": None, "msg": msg}
