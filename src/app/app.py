import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqladmin import Admin

from src.app.api.v1.admin.admin import UserAdmin
from src.app.lifespan import lifespan
from src.app.depends.auth import auth_user
from src.app.api.v1 import router
from src.app.db import db

app = FastAPI(lifespan=lifespan)
admin = Admin(app, db.engine)

admin.add_view(UserAdmin)

app.include_router(router)

@app.get("/")
async def index(user = Depends(auth_user)):
    if user is None:
        return HTTPException(status_code=401, detail="Unauthorized")
    return user

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1")