from src.app.models.user import UserModel
from src.app.depends.auth import auth_user
from src.app.app import app

def overrides_user_auth(user: UserModel):
    app.dependency_overrides[auth_user] = lambda: user