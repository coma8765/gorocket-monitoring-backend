import asyncio
import logging
import threading
from typing import List

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect

from .saver import Saver
from .transport import Transfer, InputData

logging.basicConfig(level=logging.INFO)

app = FastAPI()


transfer = Transfer()
saver = Saver()


class WebSocketSender:
    clients: [WebSocket] = []
    messages: [InputData] = []
    is_on_thread = False

    async def send(self, data):
        for client in self.clients.copy():
            try:
                await client.send_json({"data": data})
            except (WebSocketDisconnect, RuntimeError):
                try:
                    self.clients.remove(client)
                except ValueError:
                    pass

    async def thread_async(self):
        if self.is_on_thread:
            return
        else:
            self.is_on_thread = True

        while True:
            if self.messages:
                messages = [self.messages.pop() for _ in range(len(self.messages))]
                await self.send(messages)
                await asyncio.sleep(0.5)


class Messages:
    messages: List[InputData] = []


web_socket_sender = WebSocketSender()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    transfer.callbacks.append(saver.save)
    transfer.callbacks.append(web_socket_sender.messages.append)
    transfer.callbacks.append(Messages.messages.append)
    threading.Thread(target=transfer.thread, daemon=True).start()


@app.on_event("shutdown")
def shutdown():
    transfer.is_on = False
    logging.basicConfig(level=logging.DEBUG)
    transfer.callbacks.remove(saver.save)
    transfer.callbacks.remove(web_socket_sender.messages.append)
    transfer.callbacks.remove(Messages.messages.append)
    saver.close()


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    web_socket_sender.clients.append(websocket)
    await web_socket_sender.thread_async()


@app.get("/messages")
async def list_messages():
    return Messages.messages
