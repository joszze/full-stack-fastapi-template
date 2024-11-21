from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, Query, Request, WebSocket, WebSocketException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User

class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        return await super().__call__(request or websocket)

reusable_oauth2 = CustomOAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]




def get_current_user(session: SessionDep, token: TokenDep) -> User:    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)        
    except (InvalidTokenError, ValidationError):
        print("hey jude")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )    
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_user_websocket(
    websocket: WebSocket,
    session: SessionDep,
    token: Annotated[str | None, Query()] = None,
) -> User:    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)        
    except (InvalidTokenError, ValidationError):
        print("hey jude")
        raise WebSocketException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )    
    user = session.get(User, token_data.sub)
    if not user:
        raise WebSocketException(status_code=404, detail="User not found")
    if not user.is_active:
        raise WebSocketException(status_code=400, detail="Inactive user")
    return user

WebsocketUser = Annotated[User, Depends(get_current_user_websocket)]

def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
