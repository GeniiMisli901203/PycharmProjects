from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import VARCHAR, ARRAY
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Float,
    Boolean,
    JSON,
    ForeignKey,
    DateTime,
)


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, unique=True, nullable=False, primary_key=True)
    username = Column(VARCHAR, unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(VARCHAR, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(VARCHAR)
    country = Column(VARCHAR, nullable=False)
    currency = Column(VARCHAR, nullable=False)
    bio = Column(VARCHAR)
    trips = relationship("Trip", back_populates="user")
    notes = relationship("Note", back_populates="user")
    expenses = relationship("Expense", back_populates="user")

    def __str__(self) -> str:
        return f"<User: {self.id}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    username = Column(
        ForeignKey(User.username, ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(VARCHAR, nullable=False)
    description = Column(VARCHAR)
    locations = Column(ARRAY(JSON), default=[])
    friends = Column(ARRAY(VARCHAR), default=[])
    user = relationship("User", back_populates="trips")
    notes = relationship("Note", back_populates="trip")
    expenses = relationship("Expense", back_populates="trip")

    def __str__(self) -> str:
        return f"<Trip: {self.id}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    user_id = Column(
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
    )
    trip_id = Column(
        ForeignKey(Trip.id, ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(VARCHAR, nullable=False)
    path = Column(VARCHAR, nullable=False)
    file_type = Column(VARCHAR, nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    is_private = Column(Boolean)
    user = relationship("User", back_populates="notes")
    trip = relationship("Trip", back_populates="notes")

    def __str__(self) -> str:
        return f"<Note: {self.id}, Trip: {self.trip_id}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    username = Column(
        ForeignKey(User.username, ondelete="CASCADE"),
        nullable=False,
    )
    trip_id = Column(ForeignKey(Trip.id, ondelete="CASCADE"), nullable=False)
    name = Column(VARCHAR, nullable=False)
    cost = Column(Float, nullable=False)
    currency = Column(VARCHAR, nullable=False)
    date = Column(DateTime, server_default=func.now())
    debtors = Column(ARRAY(VARCHAR), default=[])
    user = relationship("User", back_populates="expenses")
    trip = relationship("Trip", back_populates="expenses")

    def __str__(self) -> str:
        return f"<Expense: {self.id}, Trip: {self.trip_id}>"

    def columns_to_dict(self) -> dict:
        d = {key: getattr(self, key) for key in self.__mapper__.c.keys()}
        return d
