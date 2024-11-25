""""
This module contains functions for handling user authentication and authorization in a FastAPI application.

The functions defined in this module include:
- `get_db`: A generator function that yields a database session
- `get_current_user`: A function to retrieve the current user based on the provided token
- `get_current_user_websocket`: A function to retrieve the current user for WebSocket connections
- `get_current_active_superuser`: A function to check if the current user is a superuser

Dependencies:
- `SessionDep`: Annotated type representing a database session dependency
- `TokenDep`: Annotated type representing a token dependency
- `CurrentUser`: Annotated type representing the current user dependency
- `WebsocketUser`: Annotated type representing the current user for WebSocket connections

External Dependencies:
- FastAPI, JWT, SQLModel
"""

# Import statements
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query, WebSocket, WebSocketException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User

# OAuth2PasswordBearer instance
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# Database session generator function
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# Session dependency annotation
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

# Function to retrieve the current user
def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    Retrieve the current user based on the provided token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        ) from exc

    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user

# CurrentUser dependency annotation
CurrentUser = Annotated[User, Depends(get_current_user)]

# Function to retrieve the current user for WebSocket connections
def get_current_user_websocket(
    websocket: WebSocket,
    session: SessionDep,
    token: Annotated[str | None, Query()] = None,
) -> User:
    """
    Retrieve the current user for WebSocket connections based on the provided token.
    """
    if not token:
        raise WebSocketException(code=status.HTTP_401_UNAUTHORIZED, reason="Unauthorized")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as exc:
        raise WebSocketException(
            code=status.HTTP_403_FORBIDDEN,
            reason="Could not validate credentials",
        ) from exc

    user = session.get(User, token_data.sub)
    if not user:
        raise WebSocketException(code=status.HTTP_404_NOT_FOUND, reason="User not found")
    if not user.is_active:
        raise WebSocketException(code=status.HTTP_400_BAD_REQUEST, reason="Inactive user")

    return user

# WebsocketUser dependency annotation
WebsocketUser = Annotated[User, Depends(get_current_user_websocket)]

# Function to check if the current user is a superuser
def get_current_active_superuser(current_user: CurrentUser) -> User:
    """
    Checks if the current user is a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges"
        )

    return current_user




