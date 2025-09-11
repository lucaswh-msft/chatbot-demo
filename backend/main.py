from fastapi import FastAPI, Body, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import os
from dotenv import load_dotenv
import httpx
import time
from urllib.parse import urlparse, parse_qs

# Load environment variables from backend/.env so AZURE_OPENAI_* values are available
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

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
    allow_origins=["https://www.bestbuy.com"],
    allow_origin_regex=r"^http://localhost:\\d+$",
    allow_credentials=True,
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

        # Only add CORS headers if an Origin header was provided and it's allowed
        def origin_allowed(o: Optional[str]) -> bool:
            if not o:
                return False
            if o == "https://www.bestbuy.com":
                return True
            if o.startswith("http://localhost:"):
                return True
            return False

        if origin and origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = (
                request.headers.get("access-control-request-headers", "*")
            )
        return response

app.add_middleware(DynamicCORSMiddleware)

# In-memory store for fetched product pages
PRODUCTS: Dict[str, Dict] = {}

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
    # Integrate with Azure OpenAI (via the lightweight wrapper in openai_client.py).
    # If the OpenAI client isn't configured or the call fails, fall back to the original echo response.
    user_text = payload.message.message or ""
    display = f"ECHO1 {user_text}"

    try:
        # support importing the wrapper both as a top-level module and as a package-relative module
        try:
            from openai_client import OpenAIClient
        except Exception:
            from .openai_client import OpenAIClient

        client = OpenAIClient()
        # If we have any fetched products, use the most-recently-added one
        if PRODUCTS:
            # get the last-inserted key from the dict (preserved insertion order in Python 3.7+)
            last_product_id = next(reversed(PRODUCTS))
            prod = PRODUCTS[last_product_id]
            print(f"[send_message] using product_id={last_product_id} url={prod.get('url')}")
            # build a short prompt that includes the product URL and a snippet of HTML
            html_snippet = (prod.get('html') or '')[:1000]
            prompt = f"Query:\n{user_text}\n\nProduct:{prod.get('url')}\n\nHTML_SNIPPET:{html_snippet}"
        else:
            prompt = user_text
        ai_reply = client.chat_completion(
            user_message=prompt,
            system_instruction="You are a helpful assistant.",
            max_tokens=512,
            temperature=1.0,
            top_p=1.0,
        )

        if ai_reply:
            display = ai_reply.strip()
    except Exception as ex:
        # If anything goes wrong (missing env vars, network, library), gracefully fallback to echo.
        print(ex)
        display = f"ECHO2 {user_text}"

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

# Track a pageview. Expects JSON with an `originalUrl` that contains
# a query parameter `url` whose value is the Basalt product page URL.
@app.post("/track/pageview")
async def track_pageview(request: Request):
    data = await request.json()
    original_url = data.get("originalUrl")
    if not original_url:
        return {"status": "ignored", "reason": "missing originalUrl"}

    parsed = urlparse(original_url)
    qs = parse_qs(parsed.query)
    product_url = qs.get("url", [None])[0]

    if not product_url:
        return {"status": "ignored", "reason": "no url param"}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(product_url, timeout=10.0)

        product_id = product_url.rstrip("/").split("/")[-1]
        PRODUCTS[product_id] = {
            "url": product_url,
            "timestamp": time.time(),
            "html": resp.text,
        }
        print(f"[track_pageview] saved product_id={product_id} url={product_url} timestamp={PRODUCTS[product_id]['timestamp']}")

        return {"status": "ok", "product_id": product_id}
    except Exception as ex:
        return {"status": "error", "error": str(ex)}


@app.get("/product/{product_id}")
async def get_product(product_id: str):
    record = PRODUCTS.get(product_id)
    if not record:
        return {"error": "not found"}
    return record

@app.get("/health")
async def health():
    return {"status": "ok"}