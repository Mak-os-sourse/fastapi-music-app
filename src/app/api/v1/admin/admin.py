from sqladmin import ModelView

from src.app.models.user import User

class UserAdmin(ModelView, model=User):
    column_list = [key.key for key in User.__table__.columns]
