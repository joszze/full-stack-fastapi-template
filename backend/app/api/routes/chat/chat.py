import random
import string
from fastapi import APIRouter, Depends, WebSocket
from fastapi import WebSocket, WebSocketDisconnect

from fastapi import  WebSocket
from datetime import datetime
import json

from fastapi.responses import HTMLResponse

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser, get_current_user
from app.core.websocket import manager 
from collections import deque


from string import ascii_uppercase
rooms = deque()

router = APIRouter()
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/")
async def get(session: SessionDep, current_user: CurrentUser):
    print(current_user)
    return HTMLResponse(html)

@router.websocket("/ws", dependencies=[Depends(get_current_user)])
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@router.websocket("/join/{room}")
async def join_room(session: SessionDep, current_user: CurrentUser, websocket: WebSocket, room: str):

    rooms.append(room)

    if room not in rooms:
        return {"error": "Room not found"}

    await manager.connect(websocket, room)
    await manager.send_personal_message(f"You# joined the room {room}", websocket)
    await manager.broadcast(f"User# {current_user.email} joined the room", websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You#: {data}", websocket)
            await manager.broadcast(f"User# {current_user.email} says: {data}", websocket, room)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        await manager.broadcast(f"User# {current_user.email} left the room", websocket, room)





# Create a room
@router.websocket("/create")
async def create_room(session: SessionDep, current_user: CurrentUser, websocket: WebSocket):
        
    room = random.choice(string.ascii_uppercase + string.digits)
    rooms.append(room)

    await manager.connect(websocket, room)
    await manager.send_personal_message(f"You# created the room {room}", websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You#: {data}", websocket)
            await manager.broadcast(f"User# {current_user.email} says: {data}", websocket, room)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        await manager.broadcast(f"User# {current_user.email} left the room", websocket, room)
