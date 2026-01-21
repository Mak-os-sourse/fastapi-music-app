from fastapi import APIRouter

from src.app.api.v1.user_2fa import router as user_2fa
from src.app.api.v1.user import router as user
from src.app.api.v1.music import router as music
from src.app.api.v1.playlist import router as playlist

router = APIRouter()
router.include_router(user)
router.include_router(user_2fa)
router.include_router(music)
router.include_router(playlist)