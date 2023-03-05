import logging
import uuid
import time

from typing import Union
from urllib.parse import urlencode
from fastapi import Depends, FastAPI, HTTPException, status, Response, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import datetime

from app import crud, security, schemas, auth, models
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["35/minute"])

app = FastAPI(
    title="Desk Booking API",
    swagger_ui_parameters={"operationsSorter": "method"},
    version=1.0,
    root_path="/",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Allowing for CORS, so frontend can call on API endpoints

origins = ["http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Dependency for retriving database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.middleware("http")
def flatten_query_string_lists(request: Request, call_next):
    """
    Middleware to convert query strings into the correct format for fastAPI.
    Correctly formatted strings will be unaffected.
    Example input: http://localhost:8000/users?&range=[0,9]&sort=["id","ASC"]
    Converted to : http://localhost:8000/users?&range=0&range=9&sort=id&sort=ASC

    Parameters:
            request (Request):
            call_next (function):

    Returns:
        callback_func (function or None):
    """

    flattened = []

    for key, value in request.query_params.multi_items():
        value = value.strip("[]")
        for entry in value.split(","):
            entry = entry.strip('""')
            if entry.isdigit():
                flattened.append((key, int(entry)))
            else:
                flattened.append((key, entry))
    request.scope["query_string"] = urlencode(flattened, doseq=True).encode("utf-8")

    return call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    generated_uuid = str(uuid.uuid4())
    logger.info(
        f"{generated_uuid} - Start of {request.method} request to path {request.url.path[1:]}"
    )
    start_time = time.time()
    request.state.uuid = generated_uuid

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    logger.info(
        f"{generated_uuid} - Response sent, completed in {formatted_process_time}ms with status code {response.status_code}"
    )

    return response


# Start of request mapping, majority of functions only perform a call to crud.py with some error handling
# More complex functions are commented on. All crud.py functions are commented to help with understanding here.

# Redirect to swagger documentation when accessing the "/" route


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
def docs(request: Request):
    current_uuid = request.state.uuid
    logger.info(f"{current_uuid} - Redirecting request to /docs")
    return RedirectResponse(url="/docs")


# User Endpoints
# With the use of pydantic and fastAPI each endpoint has an allowlist (the params of the functions), to validate inputs (prevent injection)


@app.post("/login", response_model=schemas.Token)
def login_and_get_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Checks if a user exists using the authenticate user function. If they don't they are unautherised.
    If they do exist a JWT is generated using authentication functions and returned.

    Parameters:
            db (Session): A session of a database (from dependancy)
            form_data (OAuth2PasswordRequestForm): Contains data for registering a user

    Returns:
        JWT (dictionary): A dictionary containing the JWTs access and refresh token as well as the token type
    """
    current_uuid = request.state.uuid
    logger.debug(f"{current_uuid} - Entered login and get token function")
    user = auth.authenticate_user(
        current_uuid, db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(
        minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_expires = datetime.timedelta(
        minutes=security.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    logger.info(f"{current_uuid} - Generated JWTs")
    logger.debug(f"{current_uuid} - Exiting login and get token function")

    return {
        "access_token": auth.generic_token_creation(
            current_uuid=current_uuid,
            data={"sub": user.username},
            expires_delta=access_token_expires,
            token_type="access",
        ),
        "refresh_token": auth.generic_token_creation(
            current_uuid=current_uuid,
            data={"sub": user.username},
            expires_delta=refresh_token_expires,
            token_type="refresh",
        ),
        "token_type": "bearer",
    }


# Registers both endpoints to keep to REST standards


@app.post("/register", response_model=schemas.User)
@app.post("/users", response_model=schemas.User)
def create_user(
    request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)
):
    current_uuid = request.state.uuid
    logger.debug(f"{current_uuid} - Entered create user function")
    db_user = crud.get_user_by_username(
        current_uuid=current_uuid, db=db, username=user.username
    )
    if db_user:
        logger.info(f"{current_uuid} - Email alreadys exists, user will not be created")
        raise HTTPException(status_code=400, detail="Email already registered")
    logger.debug(f"{current_uuid} - Exiting create user function")
    logger.info(f"{current_uuid} - Creating user")
    return crud.create_user(current_uuid=current_uuid, db=db, user=user)


@app.get(
    "/users",
    response_model=list[schemas.User],
    dependencies=[Depends(auth.is_admin)],
)
def read_users(
    request: Request,
    response: Response,
    range: Union[list[int], None] = Query(default=None),
    sort: Union[list[str], None] = Query(default=["id", "ASC"]),
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    logger.debug(f"{current_uuid} - Entered read users function")
    users = crud.get_all_entities(
        current_uuid=current_uuid, db=db, range=range, sort=sort, model=models.User
    )
    logger.info(f"{current_uuid} - Retrived users")
    response.headers["Content-Range"] = str(len(users))
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    logger.debug(f"{current_uuid} - Exiting read users function")
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    current_uuid = request.state.uuid
    logger.debug(f"{current_uuid} - Entered read users function")
    db_user: schemas.User = crud.get_entity(
        current_uuid=current_uuid, db=db, id=user_id, model=models.User
    )
    if db_user is None:
        logger.info(f"{request.state.uuid} - Requested user ID does not exist")
        raise HTTPException(status_code=404, detail="User not found")
    elif db_user.id != current_user.id and current_user.admin == False:
        logger.info(
            f"{request.state.uuid} - USER(ID={current_user.id} USERNAME={current_user.username}) attempted to get another users resource"
        )
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return db_user


@app.get("/users/me/", response_model=schemas.User)
def read_own_details(
    request: Request,
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    print(current_user.__dict__)
    return current_user


@app.patch("/users/{user_id}")
def update_user(
    request: Request,
    user_id: int,
    user: schemas.UserUpdate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    existing_user: schemas.User = crud.get_entity(
        current_uuid=current_uuid, db=db, id=user_id, model=models.User
    )
    if existing_user is None:
        logger.info(f"{request.state.uuid} - Requested user ID does not exist")
        raise HTTPException(status_code=404, detail="User not found")
    elif existing_user.id != current_user.id and current_user.admin == False:
        logger.info(
            f"{request.state.uuid} - USER(ID={current_user.id} USERNAME={current_user.username}) attempted to get another users resource"
        )
        raise HTTPException(status_code=403, detail="Operation not permitted")
    updated_user = crud.update_entity(
        current_uuid=current_uuid,
        db=db,
        entity_to_update=existing_user,
        updates=user,
        model=models.User,
    )
    return updated_user


@app.delete("/users/{user_id}", status_code=204, dependencies=[Depends(auth.is_admin)])
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    current_uuid = request.state.uuid
    user_to_delete = crud.get_entity(
        current_uuid=current_uuid, db=db, id=user_id, model=models.User
    )
    if user_to_delete is None:
        logger.info(f"{request.state.uuid} - Requested ID for deletion does not exist")
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_entity(current_uuid=current_uuid, db=db, id=user_id, model=models.User)


# Room Endpoints


@app.post(
    "/rooms",
    response_model=schemas.Room,
    dependencies=[Depends(auth.get_current_active_user)],
)
def create_room(
    request: Request, room: schemas.RoomCreate, db: Session = Depends(get_db)
):
    current_uuid = request.state.uuid
    db_room = crud.get_room_by_name(
        current_uuid=current_uuid, db=db, room_name=room.name
    )
    if db_room:
        logger.info(f"{request.state.uuid} - Room already exists")
        raise HTTPException(status_code=400, detail="Room already exists")
    return crud.create_room(current_uuid=current_uuid, db=db, room=room)


@app.get(
    "/rooms",
    response_model=list[schemas.Room],
    dependencies=[Depends(auth.get_current_active_user)],
)
def read_rooms(
    request: Request,
    response: Response,
    range: Union[list[int], None] = Query(default=None),
    sort: Union[list[str], None] = Query(default=["id", "ASC"]),
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    rooms = crud.get_all_entities(
        current_uuid=current_uuid, db=db, range=range, sort=sort, model=models.Room
    )
    response.headers["Content-Range"] = str(len(rooms))
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return rooms


@app.get(
    "/rooms/{room_id}",
    response_model=schemas.Room,
    dependencies=[Depends(auth.get_current_active_user)],
)
def read_room(request: Request, room_id: int, db: Session = Depends(get_db)):
    current_uuid = request.state.uuid
    db_room = crud.get_entity(
        current_uuid=current_uuid, db=db, id=room_id, model=models.Room
    )
    if db_room is None:
        logger.info(f"{request.state.uuid} - Requested room does not exist")
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room


@app.patch("/rooms/{room_id}", dependencies=[Depends(auth.is_admin)])
def update_room(
    request: Request,
    room_id: int,
    room: schemas.RoomUpdate,
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    existing_room = crud.get_entity(
        current_uuid=current_uuid, db=db, id=room_id, model=models.Room
    )
    if existing_room is None:
        logger.info(f"{request.state.uuid} - Requested room does not exist")
        raise HTTPException(status_code=404, detail="Room not found")
    updated_room = crud.update_entity(
        current_uuid=current_uuid,
        db=db,
        entity_to_update=existing_room,
        updates=room,
        model=models.Room,
    )
    return updated_room


@app.delete("/rooms/{room_id}", status_code=204, dependencies=[Depends(auth.is_admin)])
def delete_room(request: Request, room_id: int, db: Session = Depends(get_db)):
    current_uuid = request.state.uuid
    room_to_delete = crud.get_entity(
        current_uuid=current_uuid, db=db, id=room_id, model=models.Room
    )
    if room_to_delete is None:
        logger.info(f"{request.state.uuid} - Requested ID for deletion does not exist")
        raise HTTPException(status_code=404, detail="Room not found")
    crud.delete_entity(current_uuid=current_uuid, db=db, id=room_id, model=models.Room)


# Desk Endpoints


@app.post("/desks", response_model=schemas.Desk, dependencies=[Depends(auth.is_admin)])
def create_desk(
    request: Request, desk: schemas.DeskCreate, db: Session = Depends(get_db)
):
    current_uuid = request.state.uuid
    db_desk = crud.get_desk_by_room_and_number(
        current_uuid=current_uuid, db=db, room_id=desk.room_id, desk_number=desk.number
    )
    if db_desk:
        logger.info(f"{request.state.uuid} - Desk already exists")
        raise HTTPException(status_code=400, detail="Desk already exists")
    return crud.create_desk(current_uuid=current_uuid, db=db, desk=desk)


@app.get(
    "/desks",
    response_model=list[schemas.Desk],
    dependencies=[Depends(auth.is_admin)],
)
def read_desks(
    request: Request,
    response: Response,
    range: Union[list[int], None] = Query(default=None),
    sort: Union[list[str], None] = Query(default=None),
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    desks = crud.get_all_entities(
        current_uuid=current_uuid, db=db, range=range, sort=sort, model=models.Desk
    )
    response.headers["Content-Range"] = str(len(desks))
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return desks


@app.get(
    "/rooms/{room_id}/desks",
    response_model=list[schemas.Desk],
    dependencies=[Depends(auth.get_current_active_user)],
)
def read_desks_in_room(
    request: Request,
    response: Response,
    room_id: int,
    range: Union[list[int], None] = Query(default=None),
    sort: Union[list[str], None] = Query(default=["id", "ASC"]),
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    desks = crud.get_desks_in_room(
        current_uuid=current_uuid, db=db, room_id=room_id, range=range, sort=sort
    )
    response.headers["Content-Range"] = str(len(desks))
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    if desks is None:
        logger.info(f"{request.state.uuid} - Requested room does not exist")
        raise HTTPException(status_code=404, detail="Room not found")
    return desks


@app.get(
    "/desks/{desk_id}",
    response_model=schemas.Desk,
    dependencies=[Depends(auth.get_current_active_user)],
)
def read_desk(request: Request, desk_id: int, db: Session = Depends(get_db)):
    current_uuid = request.state.uuid
    db_desk = crud.get_entity(
        current_uuid=current_uuid, db=db, id=desk_id, model=models.Desk
    )
    if db_desk is None:
        logger.info(f"{request.state.uuid} - Requested desk does not exist")
        raise HTTPException(status_code=404, detail="Desk not found")
    return db_desk


@app.patch("/desks/{desk_id}", dependencies=[Depends(auth.is_admin)])
def update_desk(
    request: Request,
    desk_id: int,
    desk: schemas.DeskUpdate,
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    existing_desk = crud.get_entity(
        current_uuid=current_uuid, db=db, id=desk_id, model=models.Desk
    )
    if existing_desk is None:
        logger.info(f"{request.state.uuid} - Requested desk does not exist")
        raise HTTPException(status_code=404, detail="Desk not found")
    updated_desk = crud.update_entity(
        current_uuid=current_uuid,
        db=db,
        entity_to_update=existing_desk,
        updates=desk,
        model=models.Desk,
    )
    return updated_desk


@app.delete("/desks/{desk_id}", status_code=204, dependencies=[Depends(auth.is_admin)])
def delete_desk(request: Request, desk_id: int, db: Session = Depends(get_db)):
    current_uuid = request.state.uuid
    desk_to_delete = crud.get_entity(
        current_uuid=current_uuid, db=db, id=desk_id, model=models.Desk
    )
    if desk_to_delete is None:
        logger.info(f"{request.state.uuid} - Requested ID for deletion does not exist")
        raise HTTPException(status_code=404, detail="Desk not found")
    crud.delete_entity(current_uuid=current_uuid, db=db, id=desk_id, model=models.Desk)


# Booking Endpoints


@app.post(
    "/bookings", response_model=schemas.Booking, dependencies=[Depends(auth.is_admin)]
)
def create_booking(
    request: Request, booking: schemas.BookingCreate, db: Session = Depends(get_db)
):
    current_uuid = request.state.uuid
    db_booking = crud.get_booking_by_desk_and_date(
        current_uuid=current_uuid, db=db, desk_id=booking.desk_id, date=booking.date
    )
    if db_booking:
        logger.info(f"{request.state.uuid} - Booking already exists")
        raise HTTPException(status_code=400, detail="Booking already exists")
    return crud.create_booking(current_uuid=current_uuid, db=db, booking=booking)


@app.get(
    "/bookings",
    response_model=list[schemas.Booking],
    dependencies=[Depends(auth.is_admin)],
)
def read_bookings(
    request: Request,
    response: Response,
    range: Union[list[int], None] = Query(default=None),
    sort: Union[list[str], None] = Query(default=["id", "ASC"]),
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    bookings = crud.get_all_entities(
        current_uuid=current_uuid, db=db, range=range, sort=sort, model=models.Booking
    )
    response.headers["Content-Range"] = str(len(bookings))
    response.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return bookings


@app.get(
    "/bookings/{booking_id}",
    response_model=schemas.Booking,
    dependencies=[Depends(auth.get_current_active_user)],
)
def read_bookings(
    request: Request, booking_id: int, response: Response, db: Session = Depends(get_db)
):
    current_uuid = request.state.uuid
    db_booking = crud.get_entity(
        current_uuid=current_uuid, db=db, id=booking_id, model=models.Booking
    )
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking


@app.get(
    "/rooms/{room_id}/bookings/{date}",
    response_model=list[schemas.Booking],
    dependencies=[Depends(auth.get_current_active_user)],
)
def read_bookings_by_room(
    request: Request,
    response: Response,
    date: datetime.date,
    room_id: int,
    range: Union[list[int], None] = Query(default=None),
    sort: Union[list[str], None] = Query(default=["id", "ASC"]),
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    db_booking = crud.get_bookings_by_room(
        current_uuid=current_uuid, db=db, date=date, room_id=room_id
    )
    if db_booking is None:
        logger.info(f"{request.state.uuid} - Requested booking does not exist")
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking


@app.patch("/bookings/{booking_id}")
def update_booking(
    request: Request,
    booking_id: int,
    booking: schemas.BookingUpdate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    existing_booking: schemas.Booking = crud.get_entity(
        current_uuid=current_uuid, db=db, id=booking_id, model=models.Booking
    )
    if existing_booking is None:
        logger.info(f"{request.state.uuid} - Requested booking does not exist")
        raise HTTPException(status_code=404, detail="Booking not found")
    elif existing_booking.user_id != current_user.id and current_user.admin == False:
        logger.info(
            f"{request.state.uuid} - USER(ID={current_user.id} USERNAME={current_user.username}) attempted to get another users resource"
        )
        raise HTTPException(status_code=403, detail="Operation not permitted")
    updated_booking = crud.update_entity(
        current_uuid=current_uuid,
        db=db,
        entity_to_update=existing_booking,
        updates=booking,
        model=models.Booking,
    )
    return updated_booking


@app.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(
    request: Request,
    booking_id: int,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    booking_to_delete: models.Booking = crud.get_entity(
        current_uuid=current_uuid, db=db, id=booking_id, model=models.Booking
    )
    if booking_to_delete is None:
        logger.info(f"{request.state.uuid} - Requested ID for deletion does not exist")
        raise HTTPException(status_code=404, detail="Booking not found")
    elif booking_to_delete.user_id != current_user.id and current_user.admin == False:
        logger.info(
            f"{request.state.uuid} - USER(ID={current_user.id} USERNAME={current_user.username}) attempted to get another users resource"
        )
        raise HTTPException(status_code=403, detail="Operation not permitted")
    crud.delete_entity(
        current_uuid=current_uuid, db=db, id=booking_id, model=models.Booking
    )


@app.get("/users/me/bookings/", response_model=list[schemas.BookingSummary])
async def read_own_items(
    request: Request,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db),
):
    current_uuid = request.state.uuid
    return crud.get_users_bookings(
        current_uuid=current_uuid, db=db, user_id=current_user.id
    )
