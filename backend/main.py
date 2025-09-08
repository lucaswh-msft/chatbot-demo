from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

app = FastAPI(title="Basalt Chatbot API", version="1.0.0")

# CORS for local React dev server
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Shared Schemas ---
class Memberships(BaseModel):
    isBetaMember: bool = False
    isTotalTechSupport: bool = False

class ClientLite(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    memberships: Memberships = Memberships()
    membershipList: List[str] = []
    orderId: Optional[str] = None

# --- Init Schema ---
class InitMessageClient(ClientLite):
    emailAddress: Optional[str] = None
    primaryPhoneNumber: Optional[str] = None
    userPin: Optional[str] = None

class InitMessage(BaseModel):
    requestedProductDataType: Optional[str] = None
    client: InitMessageClient

class Provider(BaseModel):
    currentProvider: str = "caip"
    queue: Optional[str] = None
    previousProvider: Optional[str] = None
    channel: str = "chat"
    pillar: Optional[str] = None
    category: Optional[str] = None
    chatAttributes: Optional[Dict] = None

class InitRequest(BaseModel):
    client: ClientLite
    id: str = ""
    message: InitMessage
    connection: str = Field(pattern=r"^(connecting)$")
    provider: Provider
    requestedAgentPool: str = "caip"
    requestedAgentQueue: Optional[str] = None
    clientId: str
    caipConversationId: Optional[str] = None
    paidMember: bool = False
    loggedInAtInitChat: bool = False
    isNative: bool = True
    chatSessionStart: Optional[str] = None
    mediaTrack: str = "text"

# --- Message Schema ---
class MetadataMore(BaseModel):
    membershipState: Optional[str] = None
    logInState: Optional[str] = None
    referer: Optional[str] = None
    botSource: Optional[str] = None
    prevUtterance: Optional[str] = None
    requestedProductDataType: Optional[str] = None
    existingUtterance: Optional[str] = None
    intentName: Optional[str] = None
    prevResponse: Optional[str] = None

class Metadata(BaseModel):
    more: MetadataMore = MetadataMore()
    correlationId: Optional[str] = None
    conversationId: Optional[str] = None
    genAI: Optional[bool] = True

class ChatMessage(BaseModel):
    turnId: int
    msgTimestamp: datetime
    latLong: Optional[str] = None
    metadata: Metadata = Metadata()
    message: str
    msgSource: str = Field(pattern=r"^(user_typed|system)$")

class MessageRequest(BaseModel):
    client: ClientLite
    id: str
    message: ChatMessage
    connection: str = Field(pattern=r"^(connected)$")
    provider: Provider
    requestedAgentPool: str = "caip"
    requestedAgentQueue: Optional[str] = None
    clientId: str
    caipConversationId: str
    paidMember: bool = False
    loggedInAtInitChat: bool = False
    isNative: bool = True
    chatSessionStart: Optional[str] = None
    mediaTrack: str = "text"

# --- Response Schemas ---
class BotMessage(BaseModel):
    type: str
    displayText: Optional[str] = None
    hyperlinks: List[str] = []
    options: List[str] = []
    dynamicText: Optional[List[Dict]] = None

class MessageResponse(BaseModel):
    messages: List[BotMessage]

# --- API Endpoints ---
@app.post("/services/conversation/web/api/v1/unified-chat/caip/init")
async def init_chat(payload: InitRequest = Body(...)):
    # Minimal state echo; a real impl would create a conversation record
    return {"status": "chat_initialized", "conversationId": payload.caipConversationId or "conv_mock"}

@app.post("/services/conversation/web/api/v1/unified-chat/caip/message", response_model=MessageResponse)
async def send_message(payload: MessageRequest = Body(...)):
    # Simple echo response
    return MessageResponse(messages=[
        BotMessage(type="Text", displayText=f"Echo: {payload.message.message}")
    ])

@app.get("/health")
async def health():
    return {"status": "ok"}