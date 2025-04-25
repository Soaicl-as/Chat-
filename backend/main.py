
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from instagrapi import Client
from pydantic import BaseModel
import asyncio
import time
import random
import uuid
import io

app = FastAPI()

origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

clients = {}
logs = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class TwoFARequest(BaseModel):
    session_id: str
    verification_code: str
    two_factor_identifier: str

class DMRequest(BaseModel):
    session_id: str
    target_username: str
    list_type: str
    message: str
    count: int
    min_delay: int
    max_delay: int

@app.post("/api/login")
def login(req: LoginRequest):
    session_id = str(uuid.uuid4())
    cl = Client()
    try:
        cl.login(req.username, req.password)
        clients[session_id] = cl
        logs[session_id] = []
        return {"session_id": session_id}
    except Exception as e:
        if hasattr(e, 'two_factor_required') and e.two_factor_required:
            two_factor_info = {
                "session_id": session_id,
                "two_factor_identifier": e.two_factor_info.get("two_factor_identifier"),
                "username": req.username,
                "password": req.password
            }
            clients[session_id] = two_factor_info
            return {"two_factor_required": True, "session_id": session_id, "two_factor_identifier": two_factor_info["two_factor_identifier"]}
        raise

@app.post("/api/verify_2fa")
def verify_2fa(req: TwoFARequest):
    info = clients[req.session_id]
    cl = Client()
    cl.login(info["username"], info["password"], verification_code=req.verification_code, two_factor_identifier=req.two_factor_identifier)
    clients[req.session_id] = cl
    logs[req.session_id] = []
    return {"session_id": req.session_id}

@app.post("/api/send_dms")
async def send_dms(req: DMRequest):
    cl = clients[req.session_id]
    log = logs[req.session_id]
    user_id = cl.user_id_from_username(req.target_username)
    users = []
    if req.list_type == "followers":
        users = list(cl.user_followers(user_id).values())
    else:
        users = list(cl.user_following(user_id).values())
    users = users[:req.count]
    for u in users:
        delay = random.randint(req.min_delay, req.max_delay)
        try:
            cl.direct_send(req.message, [u.pk])
            log.append(f"Sent to {u.username}")
        except Exception as e:
            log.append(f"Failed to send to {u.username}: {e}")
        await asyncio.sleep(delay)
    return {"status": "done"}

@app.get("/api/logs/{session_id}")
def stream_logs(session_id: str):
    async def log_stream():
        last_index = 0
        while True:
            log = logs.get(session_id, [])
            if last_index < len(log):
                yield f"data: {log[last_index]}

"
                last_index += 1
            await asyncio.sleep(1)
    return StreamingResponse(log_stream(), media_type="text/event-stream")
