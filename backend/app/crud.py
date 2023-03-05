import logging
from typing import Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound

import datetime

from app import models, schemas, security

from datetime import datetime

logger = logging.getLogger(__name__)

# Generic Functions
# No data encryption is required apart from on passwords since no sensitive information is stored


def get_all_entities(
    current_uuid: UUID,
    db: Session,
    range: Union[list[int], None],
    sort: Union[list[str], None],
    model: Union[models.User, models.Room, models.Desk, models.Booking],
):
    """
    Retrives either all entites (from a model) or a range of entities from a database based on an ID
    with the option to sort them by any property ascending or decending, and returns a list of the retrived entities

    Parameters:
            db (Session): A session of a database
            range (List[int] or None): A defined range, made up of an offset and limit. If none all entities are retrived.
            sort (List[str] or None): Defines the sort, made up of a property and ascending/decending. If none, entities are sorted by ID acsending.
            model (models): The table, represented as a model, to retrive from

    Returns:
        model (List[models.x] or None): A list of the retrived entity or None if not found
    """
    logger.debug(f"{current_uuid} - Entered get all entities function")
    if sort == None:
        users_id = getattr(model, "id").asc()
    else:
        users_id = (
            getattr(model, sort[0]).asc()
            if sort[1].upper() == "ASC"
            else getattr(model, sort[0]).desc()
        )
    if range == None:
        result = db.query(model).order_by(users_id).all()
    else:
        result = (
            db.query(model).order_by(users_id).offset(range[0]).limit(range[1]).all()
        )
    logger.info(
        f"{current_uuid} - Successfully retrived all entities for MODEL(MODEL={model})"
    )
    logger.debug(f"{current_uuid} - Exiting get all entities function")
    return result


def get_entity(
    current_uuid: UUID,
    db: Session,
    id: int,
    model: Union[models.User, models.Room, models.Desk, models.Booking],
):
    """
    Retrives an entity from a database based on an ID and returns that entity

    Parameters:
            db (Session): A session of a database
            id (int): An integer representing an enitys ID in the database
            model (models): The table, represented as a model, to retrive from

    Returns:
            model (models.x or None): SQLAlchemy representation of the retrived entity or None if not found
    """
    logger.debug(f"{current_uuid} - Running get entity function")
    return db.query(model).filter(model.id == id).first()


def update_entity(
    current_uuid: UUID,
    db: Session,
    entity_to_update: Union[models.User, models.Room, models.Desk, models.Booking],
    updates: Union[
        schemas.UserUpdate,
        schemas.RoomUpdate,
        schemas.DeskUpdate,
        schemas.BookingUpdate,
    ],
    model: Union[models.User, models.Room, models.Desk, models.Booking],
):
    """
    Updated an entity in the database based on an ID and returns the updated entity

    Parameters:
            db (Session): A session of a database
            entity_to_update (models): The actual item to update
            id (int): An integer representing an enitys ID in the database
            model (models): The table, represented as a model, to retrive from

    Returns:
            model (models.x or None): SQLAlchemy representation of the retrived entity or None if not found
    """
    logger.debug(f"{current_uuid} - Entered update entity function")
    update_data = updates.dict(exclude_unset=True)
    logger.debug(f"{current_uuid} - Looping through object to update attributes")
    for key, value in update_data.items():
        setattr(entity_to_update, key, value)
    db.commit()
    updated_entity = get_entity(
        current_uuid=current_uuid, db=db, id=model.id, model=model
    )
    logger.info(
        f"{current_uuid} - Successfully updated MODEL(ID={model.id} MODEL={model})"
    )
    logger.debug(f"{current_uuid} - Exiting update entity function")
    return updated_entity


def delete_entity(
    current_uuid: UUID,
    db: Session,
    id: int,
    model: Union[models.User, models.Room, models.Desk, models.Booking],
):
    """
    Delete an entity in the database based on an ID

    Parameters:
            db (Session): A session of a database
            id (int): An integer representing an enitys ID in the database
            model (models): The table, represented as a model, to retrive from
    """
    logger.debug(f"{current_uuid} - Entered delete entity function")
    db.query(model).filter(model.id == id).delete()
    db.commit()
    logger.info(
        f"{current_uuid} - Successfully deleted MODEL(ID={model.id} MODEL={model})"
    )
    logger.debug(f"{current_uuid} - Exiting delete entity function")


# Users Functions


def get_user_by_username(current_uuid: UUID, db: Session, username: str):
    """
    Retrives a user from a database based on their username and returns that user

    Parameters:
            db (Session): A session of a database
            username (str): The username of a user

    Returns:
            user (models.user or None): SQLAlchemy representation of a user or None if not found
    """
    logger.debug(f"{current_uuid} - Running get user by username function")
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(current_uuid: UUID, db: Session, user: schemas.UserCreate):
    """
    Creates a user entry in the database based on the values passed in

    Parameters:
            db (Session): A session of a database
            user (schemas.UserCreate): An object with the properties required to make a user

    Returns:
            user (models.user or None): The created user
    """
    logger.debug(f"{current_uuid} - Entered create user function")
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=security.get_hashed_password(user.password),
        admin=user.admin,
    )
    logger.debug(f"{current_uuid} - Created user model")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(
        f"{current_uuid} - USER(ID={db_user.id}, USERNAME={db_user.username}) successfully created"
    )
    logger.debug(f"{current_uuid} - Exiting create user function")
    return db_user


# Room Functions


def get_room_by_name(current_uuid: UUID, db: Session, room_name: str):
    """
    Finds a room based on its name

    Parameters:
            db (Session): A session of a database
            room_name (int): The name of the room

    Returns:
            bookings (models.room or None): The retrived room or None if not found
    """
    logger.debug(f"{current_uuid} - Running get room by name function")
    return db.query(models.Room).filter(models.Room.name == room_name).first()


def create_room(current_uuid: UUID, db: Session, room: schemas.RoomCreate):
    """
    Creates a room entry in the database based on the values passed in

    Parameters:
            db (Session): A session of a database
            room (schemas.RoomCreate): An object with the properties required to make a room

    Returns:
            room (models.user or None): The created room
    """
    logger.debug(f"{current_uuid} - Entered create room function")
    db_room = models.Room(name=room.name)
    logger.debug(f"{current_uuid} - Created room model")
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    logger.info(
        f"{current_uuid} - ROOM(ID={db_room.id}, NAME={db_room.name}) successfully created"
    )
    logger.debug(f"{current_uuid} - Exiting create room function")
    return db_room


# Desk Functions


def get_desk_by_room_and_number(
    current_uuid: UUID, db: Session, desk_number: int, room_id: int
):
    """
    Finds a desk based on the number of the desk and the room it is in

    Parameters:
            db (Session): A session of a database
            desk_number (int): The number of the desk
            room_id (int): An integer representing an users ID in the database

    Returns:
            bookings (models.Desk or None): The retrived desk or None if not found
    """
    logger.debug(f"{current_uuid} - Running get desk by room and number function")
    return (
        db.query(models.Desk)
        .filter(and_(models.Desk.room_id == room_id, models.Desk.number == desk_number))
        .first()
    )


def get_desks_in_room(
    current_uuid: UUID,
    db: Session,
    room_id: int,
    range: Union[list[int], None],
    sort: Union[list[str], None],
):
    """
    Retrives either all or a range of the desks in a defined room from a database based on the rooms ID
    with the option to sort them by any property ascending or decending, and returns a list of the retrived entities

    Parameters:
            db (Session): A session of a database
            room_id (int): An integer representing an users ID in the database
            range (List[int] or None): A defined range, made up of an offset and limit. If none all entities are retrived.
            sort (List[str] or None): Defines the sort, made up of a property and ascending/decending. If none, entities are sorted by ID acsending.

    Returns:
        model (List[models.desk] or None): A list of the retrived entity or None if not found
    """
    logger.debug(f"{current_uuid} - Entered get desks in room function")
    if sort == None:
        desks_order = getattr(models.Desk, "id").asc()
    else:
        desks_order = (
            getattr(models.Desk, sort[0]).asc()
            if sort[1].upper() == "ASC"
            else getattr(models.Desk, sort[0]).desc()
        )
    if range == None:
        result = (
            db.query(models.Desk)
            .filter(models.Desk.room_id == room_id)
            .order_by(desks_order)
            .all()
        )
    else:
        result = (
            db.query(models.Desk)
            .filter(models.Desk.room_id == room_id)
            .order_by(desks_order)
            .offset(range[0])
            .limit(range[1])
            .all()
        )
    logger.info(f"{current_uuid} - Successfully retrived all DESK(ROOM_ID={room_id})")
    logger.debug(f"{current_uuid} - Exiting get desks in room function")
    return result


def create_desk(current_uuid: UUID, db: Session, desk: schemas.DeskCreate):
    """
    Creates a desk entry in the database based on the values passed in

    Parameters:
            db (Session): A session of a database
            desk (schemas.DeskCreate): An object with the properties required to make a desk

    Returns:
            user (models.user or None): The created desk
    """
    logger.debug(f"{current_uuid} - Entered create user function")
    db_desk = models.Desk(number=desk.number, room_id=desk.room_id)
    logger.debug(f"{current_uuid} - Created user model")
    db.add(db_desk)
    db.commit()
    db.refresh(db_desk)
    logger.info(
        f"{current_uuid} - DESK(ID={db_desk.id}, NUMBER={db_desk.number} ROOM_ID={db_desk.room_id}) successfully created"
    )
    logger.debug(f"{current_uuid} - Exiting create user function")
    return db_desk


# Booking Functions


def get_booking_by_desk_and_date(
    current_uuid: UUID, db: Session, desk_id: int, date: datetime.date
):
    """
    Gets a booking for a desk on specified date if one exists

    Parameters:
            db (Session): A session of a database
            desk_id (int): An integer representing the desks ID in the database
            date (datetime.date): The date of the booking

    Returns:
            bookings (models.booking or None): The retrived booking or None if not found
    """
    logger.debug(f"{current_uuid} - Running get booking by desk and date function")
    try:
        return (
            db.query(models.Booking)
            .filter(
                and_(models.Booking.desk_id == desk_id, models.Booking.date == date)
            )
            .first()
        )
    except NoResultFound:
        return None


def get_bookings_by_room(
    current_uuid: UUID, db: Session, room_id: int, date: datetime.date
):
    """
    Gets all the the bookings that have been made in a specific room

    Parameters:
            db (Session): A session of a database
            room_id (int): An integer representing an users ID in the database
            date (datetime.date): The date of requested bookings

    Returns:
            bookings (List[models.booking] or None): A list of the retrived bookings or None if not found
    """
    logger.debug(f"{current_uuid} - Running get booking by room function")
    try:
        return (
            db.query(models.Booking)
            .join(models.Desk)
            .filter(
                and_(
                    models.Desk.room_id == room_id,
                    models.Booking.date == date.isoformat(),
                )
            )
            .all()
        )
    except NoResultFound:
        return None


def create_booking(current_uuid: UUID, db: Session, booking: schemas.BookingCreate):
    """
    Creates a booking in the database based on the values passed in

    Parameters:
            db (Session): A session of a database
            booking (schemas.BookingCreate): An object with the properties required to make a booking

    Returns:
            user (models.user or None): The created booking
    """
    logger.debug(f"{current_uuid} - Entered create booking function")
    db_booking = models.Booking(
        user_id=booking.user_id,
        desk_id=booking.desk_id,
        date=booking.date,
        approved_status=booking.approved_status,
    )
    logger.debug(f"{current_uuid} - Created booking model")
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    logger.info(
        f"{current_uuid} - BOOKING(ID={db_booking.id}, USER_ID={db_booking.user_id}) successfully created"
    )
    logger.debug(f"{current_uuid} - Exiting create room function")
    return db_booking


def get_users_bookings(current_uuid: UUID, db: Session, user_id: int):
    """
    Gets all the bookings of a user, using their user id

    Parameters:
            db (Session): A session of a database
            user_id (int): An integer representing an users ID in the database

    Returns:
            bookings (List[models.booking] or None): A list of the retrived bookings or None if not found
    """
    logger.debug(f"{current_uuid} - Running get users bookings function")
    bookings_order = getattr(models.Booking, "date").desc()
    return (
        db.query(models.Booking)
        .filter(models.Booking.user_id == user_id)
        .order_by(bookings_order)
        .all()
    )
