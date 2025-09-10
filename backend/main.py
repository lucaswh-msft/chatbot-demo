from fastapi import FastAPI, Body, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
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
    allow_origins=["*"], # Instead of specific origins, allow all for demo purposes
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamic CORS middleware for demo - reflect incoming Origin
class DynamicCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")

        # Short-circuit preflight requests so they get a 200
        if request.method == "OPTIONS":
            response = Response(status_code=200)
        else:
            response: Response = await call_next(request)

        # Only add CORS headers if an Origin header was provided
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = (
                request.headers.get("access-control-request-headers", "*")
            )
        return response

app.add_middleware(DynamicCORSMiddleware)

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
    # Hardcoded basalt \init response for demo purposes
    return {
        "body": {
            "contents": [
                {
                    "dataType": "text",
                    "data": {
                        "type": "Text",
                        "displayText": " Hi, I'm Microsoft FDE's chatbot! What can I help you with?",
                        "hyperlinks": [],
                        "options": [],
                        "dynamicText": [
                            {
                                "type": "DynamicText",
                                "textData": [
                                    {
                                        "type": "TextOption",
                                        "displayText": "Hi, I'm Microsoft FDE's chatbot!"
                                    }
                                ]
                            },
                            {
                                "type": "DynamicText",
                                "textData": [
                                    {
                                        "type": "TextOption",
                                        "displayText": "What can I help you with?"
                                    }
                                ]
                            }
                        ]
                    }
                }
            ],
            "turnId": 0,
            "metadata": {
                "more": {
                    "membershipState": "No",
                    "logInState": "loggedOut",
                    "referer": "",
                    "botSource": "dfcx",
                    "prevUtterance": "Hello",
                    "requestedProductDataType": "",
                    "intentName": "Default Welcome Intent",
                    "prevResponse": "[{\"type\": \"Text\", \"displayText\": \" Hi, I'm Microsoft FDE's chatbot! What can I help you with?\", \"hyperlinks\": [], \"options\": [], \"dynamicText\": [{\"type\": \"DynamicText\", \"textData\": [{\"type\": \"TextOption\", \"displayText\": \"Hi, I'm Microsoft FDE's chatbot!\"}]}, {\"type\": \"DynamicText\", \"textData\": [{\"type\": \"TextOption\", \"displayText\": \"What can I help you with?\"}]}]}]"
                },
                "correlationId": "a0b0654b-fab5-4a41-8e5a-df13f7b7d0dc",
                "conversationId": "77670569-5b9e-4da2-a472-253d7dbe029e",
                "genAI": False
            }
        },
        "escapeHatch": {
            "showEscapeHatch": True,
            "provider": "twilio",
            "queue": "care.postpurchasesupport.en.chat.all",
            "pillar": "care",
            "channel": "chat"
        }
    }

@app.post("/services/conversation/web/api/v1/unified-chat/caip/message")
async def send_message(payload: MessageRequest = Body(...)):
    # Echo input into Basalt-like response schema
    user_text = payload.message.message or ""
    display = f"ECHO BACK {user_text}"
    return {
        "body": {
            "contents": [
                {
                    "dataType": "text",
                    "data": {
                        "type": "Text",
                        "displayText": display,
                        "hyperlinks": [],
                        "options": [],
                        "dynamicText": [
                            {
                                "type": "DynamicText",
                                "textData": [
                                    {
                                        "type": "TextOption",
                                        "displayText": display
                                    }
                                ]
                            }
                        ]
                    }
                }
            ],
            "turnId": payload.message.turnId,
            "metadata": {
                "more": {
                    "membershipState": payload.message.metadata.more.membershipState or "No",
                    "logInState": payload.message.metadata.more.logInState or "loggedOut",
                    "referer": payload.message.metadata.more.referer or "",
                    "botSource": payload.message.metadata.more.botSource or "dfcx",
                    "prevUtterance": payload.message.metadata.more.prevUtterance or "",
                    "requestedProductDataType": payload.message.metadata.more.requestedProductDataType or "",
                    "existingUtterance": payload.message.metadata.more.existingUtterance or "",
                    "intentName": payload.message.metadata.more.intentName or "Default Welcome Intent",
                    "prevResponse": payload.message.metadata.more.prevResponse or "[{\"type\": \"Text\", \"displayText\": \" What was that?\", \"hyperlinks\": [], \"options\": [], \"dynamicText\": [{\"type\": \"DynamicText\", \"textData\": [{\"type\": \"TextOption\", \"displayText\": \"What was that?\"}]}]}]"
                },
                "correlationId": payload.message.metadata.correlationId,
                "conversationId": payload.message.metadata.conversationId,
                "genAI": False
            }
        },
        "escapeHatch": {
            "showEscapeHatch": True,
            "provider": "twilio",
            "queue": "care.postpurchasesupport.en.chat.all",
            "pillar": "care",
            "channel": "chat"
        }
    }

@app.get("/health")
async def health():
    return {"status": "ok"}