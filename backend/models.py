from database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc)


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    links = relationship("Link", back_populates="owner")


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), unique=True, nullable=False)
    note = Column(Text, nullable=True)
    name = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("Users", back_populates="links")