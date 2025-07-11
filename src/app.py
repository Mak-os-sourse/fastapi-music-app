import uvicorn
from fastapi import *

from src.users.dependencies import auth_user
from src.users.routers import router as users_routers
from src.music.__init__ import router as music_router

app = FastAPI()

app.include_router(users_routers)
app.include_router(music_router)

@app.get("/")
async def index(user = Depends(auth_user)):
    if user is None:
        return HTTPException(status_code=401, detail="Unauthorized")
    return user

if __name__ == "__main__":
    uvicorn.run(app, host="127.3.0.1")