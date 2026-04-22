"""FastAPI server for WorkFlow Arena with Gradio UI."""

import json
import uuid
import os
import sys
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server.environment import WorkFlowEnvironment
from workflows import WORKFLOWS

api_app = FastAPI(title="WorkFlow Arena", description="Multi-App Enterprise Workflow RL Environment", version="1.0.0")
api_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

sessions: Dict[str, WorkFlowEnvironment] = {}


@api_app.get("/health")
async def health():
    return {"status": "healthy"}


@api_app.post("/reset")
async def reset(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    task_name = body.get("task_name", "employee_onboarding")
    session_id = body.get("session_id") or str(uuid.uuid4())
    env = WorkFlowEnvironment()
    sessions[session_id] = env
    result = env.reset(task_name)
    result["session_id"] = session_id
    return JSONResponse(content=result)


@api_app.post("/step")
async def step(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "")
    message = body.get("message", "")
    env = sessions.get(session_id)
    if env is None:
        return JSONResponse(content={"error": "Session not found."}, status_code=404)
    result = env.step(message)
    if result["done"]:
        sessions.pop(session_id, None)
    return JSONResponse(content=result)


@api_app.get("/state")
async def get_state(session_id: str = ""):
    env = sessions.get(session_id)
    if env is None:
        return JSONResponse(content={"error": "Session not found."}, status_code=404)
    return JSONResponse(content=env.state())


@api_app.get("/tasks")
async def list_tasks():
    return JSONResponse(content={
        "tasks": [
            {
                "name": wf["name"],
                "task_id": tid,
                "difficulty": wf["difficulty"],
                "description": wf["description"],
                "max_steps": wf["max_steps"],
                "num_required_actions": len(wf["required_actions"]),
            }
            for tid, wf in WORKFLOWS.items()
        ]
    })


@api_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    env = WorkFlowEnvironment()
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type", "")
            if msg_type == "reset":
                task_name = data.get("task_name") or "employee_onboarding"
                result = env.reset(task_name)
                await websocket.send_text(json.dumps(result))
            elif msg_type == "step":
                action = data.get("action", {})
                message = action.get("message", "") if isinstance(action, dict) else str(action)
                result = env.step(message)
                await websocket.send_text(json.dumps(result))
            elif msg_type == "state":
                await websocket.send_text(json.dumps(env.state()))
            else:
                await websocket.send_text(json.dumps({"error": f"Unknown type: {msg_type}"}))
    except WebSocketDisconnect:
        pass


# Mount Gradio UI at root
import gradio as gr
from ui import demo as gradio_demo

app = gr.mount_gradio_app(api_app, gradio_demo, path="/")


def main():
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "7860"))
    uvicorn.run("server.app:app", host=host, port=port, workers=1)


if __name__ == "__main__":
    main()
