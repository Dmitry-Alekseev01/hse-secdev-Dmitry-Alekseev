from sqlalchemy import Column, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=True)

    def __init__(self, username: str = None, email: str = None, password: str = None):
        self.username = username
        self.email = email
        self.password = password
