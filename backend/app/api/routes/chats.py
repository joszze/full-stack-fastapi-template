from datetime import datetime
from email import message
from app.models import ChatMessage, ChatMessageBase, ChatMessageCreate, ChatMessagePublic, ChatMessagesPublic
from fastapi import APIRouter, WebSocket
from fastapi import WebSocket, WebSocketDisconnect,WebSocketException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep, WebsocketUser
from app.core.websocket import manager

router = APIRouter()

@router.get("/",response_model=ChatMessagesPublic)
def get_messages(session: SessionDep, current_user: CurrentUser):
    """
    Retrieve chat messages for the current user.
    """
    query = select(ChatMessage).where(ChatMessage.author_id == current_user.id)
    messages = session.exec(query).all()    
    chat_messages_public_list = [ChatMessagePublic(**item.model_dump()) for item in messages]
    return ChatMessagesPublic(data=chat_messages_public_list)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user: WebsocketUser, session: SessionDep):
    """
    Handle WebSocket connections for real-time chat.
    """
    await manager.connect(websocket)
    try:
        while True:
            recived_message = await websocket.receive_json()
            try:                
                validated_message = ChatMessageBase.model_validate(recived_message)
                print(validated_message.message)
                created_message_model = ChatMessageCreate(**validated_message.model_dump())
                session.add(ChatMessage(**created_message_model.model_dump(), author_id=current_user.id, author_alias=current_user.full_name))
                session.commit()
                await manager.broadcast(created_message_model.model_dump_json())
            except WebSocketException as e:
                print(e)                
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{current_user.full_name} left the chat")
