from __future__ import annotations
import json, logging, uuid, os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents import SQLiteSession

from draft_store import DRAFT, apply_patch
from risk_agents.agent_library.orchestrator_agent import run_incident_flow
from risk_agents.context import IncidentRunContext

log = logging.getLogger("backend")
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

if not os.getenv("OPENAI_API_KEY"):
    log.warning("OPENAI_API_KEY not set; LLM calls may fail.")

app = FastAPI(title="Risk-Incident Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.websocket("/agent/run")
async def agent_ws(ws: WebSocket):
    await ws.accept()
    session = SQLiteSession(str(uuid.uuid4()))
    ctx = IncidentRunContext()

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            if msg.get("role") != "user":
                continue

            result = await run_incident_flow(msg["content"], session=session, context=ctx)

            patch = list(ctx.last_patch or [])
            ctx.last_patch = []

            if patch:
                apply_patch(patch)
                await ws.send_json({"type": "json_patch", "payload": patch})

            await ws.send_json({
                "type": "chat",
                "payload": {"role": "assistant", "content": result.get("reply", "")}
            })
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        log.exception("WS failure: %s", exc)
        await ws.close(code=1011)

@app.post("/api/incidents/submit")
async def submit_incident(payload: dict):
    if not DRAFT:
        raise HTTPException(400, "Nothing to submit")
    return {"status": "ok", "draft": DRAFT}