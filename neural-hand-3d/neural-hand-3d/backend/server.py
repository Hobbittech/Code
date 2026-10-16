import os
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neural-hand-3d")

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "neural_hand_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if x.strip()]

app = FastAPI(title="Neural-Hand 3D API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_client: Optional[AsyncIOMotorClient] = None
db = None
openai_client: Optional[AsyncOpenAI] = None

SUPPORTED_COMMANDS = {"set_color", "set_shape", "set_scale", "rotate", "reset", "spawn_particles"}
SUPPORTED_SHAPES = {"cube", "sphere", "torus", "cone", "pyramid"}

class GestureEvent(BaseModel):
    session_id: str = Field(default="default")
    gesture: str
    confidence: float = 0
    hand: str = "unknown"
    timestamp: Optional[str] = None

class SceneState(BaseModel):
    session_id: str = Field(default="default")
    shape: str = "cube"
    color: str = "#00F0FF"
    scale: float = 1.0
    rotation: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    particles: bool = False

class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str
    scene: Optional[SceneState] = None

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def sanitize_command(command: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(command, dict):
        return None
    op = command.get("op")
    if op not in SUPPORTED_COMMANDS:
        return None
    value = command.get("value")
    if op == "set_shape" and value not in SUPPORTED_SHAPES:
        return None
    if op == "set_color":
        if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            return None
    if op == "set_scale":
        try:
            value = max(0.25, min(4.0, float(value)))
        except (TypeError, ValueError):
            return None
    if op == "rotate":
        if isinstance(value, dict):
            value = {axis: float(value.get(axis, 0)) for axis in ("x", "y", "z")}
        else:
            try:
                value = {"x": 0, "y": float(value), "z": 0}
            except (TypeError, ValueError):
                return None
    return {"op": op, "value": value}

SYSTEM_PROMPT = """You are NEURAL AI, the assistant for a spatial 3D workstation.
Help the user control a single interactive 3D object. Be concise and useful.
When a user asks to modify the scene, return a JSON action object inside a fenced
json block using exactly one supported op:
set_color (value: hex color), set_shape (value: cube|sphere|torus|cone|pyramid),
set_scale (value: number from 0.25 to 4), rotate (value: {x,y,z} degrees),
reset (value: null), spawn_particles (value: true or false).
You may include a short natural-language explanation before or after the action.
Do not invent unsupported operations. Never reveal secrets or API keys.
"""

@app.on_event("startup")
async def startup():
    global mongo_client, db, openai_client
    try:
        mongo_client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=1500)
        await mongo_client.admin.command("ping")
        db = mongo_client[DB_NAME]
        logger.info("MongoDB connected")
    except Exception as exc:
        logger.warning("MongoDB unavailable: %s", exc)
        mongo_client = None
        db = None
    if OPENAI_API_KEY:
        openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    else:
        logger.warning("OPENAI_API_KEY is not configured")

@app.on_event("shutdown")
async def shutdown():
    global mongo_client
    if mongo_client:
        mongo_client.close()

@app.get("/api/")
async def root():
    return {"name": "neural-hand-3d", "status": "online", "mongodb": db is not None, "openai": openai_client is not None}

@app.post("/api/gestures")
async def create_gesture(event: GestureEvent):
    payload = event.model_dump()
    payload["timestamp"] = payload.get("timestamp") or now_iso()
    if db is not None:
        try:
            await db.gestures.insert_one(payload)
        except Exception as exc:
            logger.warning("Gesture persistence failed: %s", exc)
    return {"ok": True, "event": payload}

@app.get("/api/gestures/recent")
async def recent_gestures(session_id: str = "default", limit: int = 30):
    limit = max(1, min(limit, 100))
    if db is None:
        return []
    try:
        cursor = db.gestures.find({"session_id": session_id}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    except Exception as exc:
        logger.warning("Gesture read failed: %s", exc)
        return []

@app.get("/api/scene/{session_id}")
async def get_scene(session_id: str):
    default = SceneState(session_id=session_id).model_dump()
    if db is None:
        return default
    try:
        saved = await db.scenes.find_one({"session_id": session_id}, {"_id": 0})
        return saved or default
    except Exception as exc:
        logger.warning("Scene read failed: %s", exc)
        return default

@app.post("/api/scene")
async def save_scene(scene: SceneState):
    if scene.shape not in SUPPORTED_SHAPES:
        raise HTTPException(400, "Unsupported shape")
    scene_data = scene.model_dump()
    if db is not None:
        try:
            await db.scenes.update_one(
                {"session_id": scene.session_id},
                {"$set": scene_data},
                upsert=True,
            )
        except Exception as exc:
            logger.warning("Scene persistence failed: %s", exc)
    return {"ok": True, "scene": scene_data}

def extract_action(text: str) -> Optional[Dict[str, Any]]:
    matches = re.findall(r"```json\s*(.*?)\s*```", text, flags=re.I | re.S)
    candidates = matches or [text]
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                command = obj.get("action", obj)
                clean = sanitize_command(command)
                if clean:
                    return clean
        except json.JSONDecodeError:
            continue
    return None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if openai_client is None:
        raise HTTPException(503, "OpenAI is not configured. Add OPENAI_API_KEY to backend/.env.")
    scene = request.scene.model_dump() if request.scene else SceneState(session_id=request.session_id).model_dump()
    prompt = f"Current scene state: {json.dumps(scene)}\nUser request: {request.message}"
    try:
        response = await openai_client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=prompt,
        )
        text = response.output_text.strip()
        return {"ok": True, "response": text, "action": extract_action(text)}
    except Exception as exc:
        logger.exception("OpenAI request failed")
        raise HTTPException(502, f"OpenAI request failed: {exc}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
