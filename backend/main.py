from fastapi import FastAPI, Body, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, unquote_plus
from fastapi.responses import JSONResponse

# Load environment variables from backend/.env so AZURE_OPENAI_* values are available
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(title="Basalt Chatbot API", version="1.0.0")

# CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Instead of specific origins, allow all for demo purposes
    allow_origin_regex=r"^http://localhost(:\d+)?$",
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

# In-memory store for captured product pages
product_store: Dict[str, Dict] = {}

# Helper to extract product id from a URL
def _extract_product_id_from_url(full_url: str) -> str:
    parsed = urlparse(full_url)
    path_segments = [seg for seg in parsed.path.split("/") if seg]
    if not path_segments:
        raise ValueError("Unable to extract product id from url")
    return path_segments[-1]


@app.get("/track/pageview", status_code=status.HTTP_204_NO_CONTENT)
async def track_pageview(request: Request):
    """Capture the raw HTML of a product page from the 'url' query param in the request.

    This endpoint intentionally ignores all other query parameters (e.g., Contentsquare beacons)
    and only extracts the 'url' parameter from the raw query string (percent-decoded).
    """
    # Extract the raw query string bytes and percent-decode/parse it ourselves so we
    # only pay attention to the 'url' key and ignore any other parameters.
    raw_qs = request.scope.get("query_string", b"").decode("utf-8", errors="ignore")
    qs = parse_qs(raw_qs, keep_blank_values=True)
    url_values = qs.get("url")

    if not url_values or not url_values[0]:
        return JSONResponse(status_code=400, content={"error": "Missing 'url' query parameter."})

    decoded_url = unquote_plus(url_values[0])

    parsed = urlparse(decoded_url)
    if not parsed.scheme or not parsed.netloc:
        return JSONResponse(status_code=400, content={"error": "Invalid 'url' parameter. Expected absolute URL."})

    try:
        product_id = _extract_product_id_from_url(decoded_url)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Unable to determine product id from the provided URL."})

    # Do not attempt to fetch external HTML from the provided URL (blocked by many sites).
    # Only record the URL and capture timestamp for later reference — do not store page HTML.
    product_store[product_id] = {
        "url": decoded_url,
        "capturedAt": datetime.utcnow().isoformat() + "Z",
    }

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/product/{product_id}")
async def get_product(product_id: str):
    record = product_store.get(product_id)
    if not record:
        raise HTTPException(status_code=404, detail="Product not found")
    return record

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

        # Include recent product capture history as additional context for the model.
        # Limit to the most recent 10 entries to avoid sending excessive data.
        recent_items = list(product_store.items())[-10:]
        if recent_items:
            product_history_lines = []
            for pid, rec in recent_items:
                # rec currently stores only url and capturedAt (no HTML), so include those.
                product_history_lines.append(f"ProductID={pid}; URL={rec.get('url')}; capturedAt={rec.get('capturedAt')}")
            product_history = "\n".join(product_history_lines)
        else:
            product_history = "No product history available."

        # Debug: print product history state for troubleshooting
        print(f"[product_history] count={len(recent_items)}")
        print(f"[product_history] entries:\n{product_history}")

        # Add the product history to the user's message so the model has that context.
        user_message_with_product_context = f"{user_text}\n\nProduct history (most recent items):\n{product_history}"

        ai_reply = client.chat_completion(
            user_message=user_message_with_product_context,
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

@app.get("/health")
async def health():
    return {"status": "ok"}