import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from app import models, security
from datetime import datetime

# Basic script to add test data to database


def add_data_to_db(db):  # pragma: no cover
    db.add(
        models.User(
            email="admin@admin.com",
            username="admin",
            hashed_password=security.get_hashed_password("admin"),
            admin=True,
        )
    )
    db.add(
        models.User(
            email="user@user.com",
            username="John_Doe",
            hashed_password=security.get_hashed_password("test321"),
            admin=False,
        )
    )

    db.add(models.Room(name="Room 431"))
    db.add(models.Room(name="Inspiration Station"))
    db.add(models.Room(name="The Hive"))

    for desk_number in range(0, 25):
        db.add(models.Desk(number=desk_number, room_id=1))
    for desk_number in range(5, 110, 5):
        db.add(models.Desk(number=desk_number, room_id=2))
    for desk_number in range(2, 8, 2):
        db.add(models.Desk(number=desk_number, room_id=3))

    db.add(
        models.Booking(
            user_id=2,
            desk_id=5,
            date=datetime.today().strftime("%Y-%m-%d"),
            approved_status=True,
        )
    )

    db.commit()


# Inital database setup


SQLALCHEMY_DATABASE_URL = os.environ.get(
    "SQLALCHEMY_DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/desk_booking_db",
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()
# Create the database and add data if it doesn't exist
if not database_exists(SQLALCHEMY_DATABASE_URL):
    create_database(SQLALCHEMY_DATABASE_URL)
    models.Base.metadata.create_all(bind=engine)
    add_data_to_db(db)
else:
    # Always attempt to create tables in case database exists with no tables
    models.Base.metadata.create_all(bind=engine)


Base = declarative_base()
