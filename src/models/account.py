from .mixin import Base
from core.database import db

class Users(Base):
    __tablename__ = "account_users"
    username = db.Column(db.String(125), nullable=False, unique=True)
    email = db.Column(db.String(125), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, **kwargs) -> None:
        super(Users, self).__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<User {self.username}>"
    