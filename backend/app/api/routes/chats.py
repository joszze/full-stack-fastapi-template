from app.models import ChatMessage, ChatMessagePublic, ChatMessagesPublic
from fastapi import APIRouter, WebSocket
from fastapi import WebSocket, WebSocketDisconnect
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep, WebsocketUser
from app.core.websocket import manager

router = APIRouter()

@router.get("/",response_model=ChatMessagesPublic)
def get(session: SessionDep, current_user: CurrentUser):
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
            data = await websocket.receive_text()
            session.add(ChatMessage(author_id=current_user.id, message=data))
            session.commit()
            await manager.broadcast(f"{current_user.full_name}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{current_user.full_name} left the chat")
