import logging
import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.database import SessionLocal

from app import schemas, crud, security

logger = logging.getLogger(__name__)

# Dependency is remade since an import would create circular dependencies


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# JSON Web Token (JWT) Functions


def generic_token_creation(
    current_uuid: UUID, data: dict, expires_delta: datetime.timedelta, token_type: str
):
    """
    Creates a JWT
    """
    logger.debug(f"{current_uuid} - Entered authenticate user function")
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    if token_type == "access":
        encoded_jwt = jwt.encode(
            to_encode, security.SECRET_KEY, algorithm=security.ALGORITHM
        )
        logger.info(f"{current_uuid} - Created JWT")
    else:
        encoded_jwt = jwt.encode(
            to_encode, security.JWT_REFRESH_SECRET_KEY, algorithm=security.ALGORITHM
        )
        logger.info(f"{current_uuid} - Created JWT Refresh Token")
    logger.debug(f"{current_uuid} - Exiting authenticate user function")
    return encoded_jwt


def authenticate_user(current_uuid: UUID, db: Session, username: str, password: str):
    """
    Checks if a user exists with credentials provided
    """
    logger.debug(f"{current_uuid} - Entered authenticate user function")
    user = crud.get_user_by_username(
        current_uuid=current_uuid, db=db, username=username
    )
    logger.debug(f"{current_uuid} - Retrived users details")
    if not user:
        logger.info(f"{current_uuid} - User does not exist")
        return False
    if not security.verify_password(password, user.hashed_password):
        logger.info(f"{current_uuid} - Users password is incorrect")
        return False
    logger.info(f"{current_uuid} - User authenticated")
    logger.debug(f"{current_uuid} - Exiting authenticate user function")
    return user


# Current user functions
# Won't work in tests due to quirks in the security of JWTS


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(security.reuseable_oauth),
):  # pragma: no cover
    """
    Gets the current logged in user entity based on the JWT (token) passed in
    """
    current_uuid = request.state.uuid
    logger.debug(f"{current_uuid} - Entered get current user function")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.debug(f"{current_uuid} - Decoding JWT")
        payload = jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        logger.debug(f"{current_uuid} - Getting username from JWT")
        username: str = payload.get("sub")
        if username is None:
            logger.info(f"{current_uuid} - JWT doesn't contain username")
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        logger.info(f"{current_uuid} - Failed to decode JWT")
        raise credentials_exception
    user = crud.get_user_by_username(
        current_uuid=current_uuid, db=db, username=token_data.username
    )
    if user is None:
        logger.info(f"{current_uuid} - User does not exist")
        raise credentials_exception
    logger.info(
        f"{current_uuid} - Retrived current USER(ID={user.id} USERNAME={user.username})"
    )
    return user


def get_current_active_user(
    request: Request,
    current_user: schemas.User = Depends(get_current_user),
):  # pragma: no cover
    logger.debug(f"{request.state.uuid} - Running get current active user function")
    return current_user


def is_admin(request: Request, user: schemas.User = Depends(get_current_active_user)):
    logger.debug(f"{request.state.uuid} - Running is admin function")
    if user.admin == False:
        logger.info(
            f"{request.state.uuid} - USER(ID={user.id} USERNAME={user.username}) attempted to hit a restricted admin endpoint as a non-admin"
        )
        raise HTTPException(status_code=403, detail="Operation not permitted")
    logger.info(
        f"{request.state.uuid} - USER(ID={user.id} USERNAME={user.username}) is authorised to use this endpoint as admin"
    )
