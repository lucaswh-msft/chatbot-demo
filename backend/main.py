from fastapi import FastAPI, Body, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import os
from dotenv import load_dotenv
import json

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

# Store the most recent product payload posted to /product so /message can augment user input
product_info = None

def extract_specification_groups_from_text(text: str) -> List[str]:
    """Search the provided text for occurrences of the exact substring
    '"specificationGroups": [{' and for each occurrence return the full JSON
    array string by scanning forward and counting brackets until the matching
    closing bracket for the array is found.
    """
    results: List[str] = []
    # Match the exact escaped sequence: "specificationGroups":[{
    search_term = '"specificationGroups":[{'
    start = 0
    n = len(text)
    while True:
        idx = text.find(search_term, start)
        if idx == -1:
            break

        # Find the '[' that begins the array; start scanning from that position
        array_start = text.find('[', idx)
        if array_start == -1:
            # malformed, give up for this occurrence
            start = idx + len(search_term)
            continue

        i = array_start
        bracket_count = 0
        # Walk forward counting brackets until the top-level array is closed
        while i < n:
            ch = text[i]
            if ch == '[':
                bracket_count += 1
            elif ch == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    # capture the array from '[' .. ']' inclusive
                    results.append(text[array_start:i+1])
                    start = i + 1
                    break
            i += 1
        else:
            # Reached end of text without closing bracket; stop searching
            break

    return results

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

@app.post("/product")
async def product_hook(request: Request):
    """Receive and persist the latest product payload for later augmentation of user messages.

    This endpoint stores an aggregation of any found `specificationGroups` arrays into
    the module-level `product_info` variable and logs a short snippet for debugging.
    """
    # Read raw body as text first; payload might not be valid JSON
    raw_bytes = await request.body()
    payload_text = raw_bytes.decode("utf-8", errors="replace")

    # Try to parse JSON to extract friendly fields for logging, but tolerate failures
    try:
        payload_obj = json.loads(payload_text)
    except Exception:
        payload_obj = None

    original_url = payload_obj.get("originalUrl") if isinstance(payload_obj, dict) else None
    response_body = payload_obj.get("responseBody") if isinstance(payload_obj, dict) else None

    print("Got product:", original_url)
    if isinstance(response_body, str):
        print("Response body:", response_body[:200], "...")
    else:
        # fall back to a short raw-body snippet for debugging
        print("Response body (fallback):", payload_text[:200], "...")

    # Dump response_body and full payload to a debug file for offline inspection
    # # try:
    # #     debug_path = os.path.join(os.path.dirname(__file__), "product_debug.txt")
    # #     with open(debug_path, "a", encoding="utf-8") as dbg:
    # #         dbg.write("---\n")
    # #         dbg.write(f"timestamp: {datetime.utcnow().isoformat()}\n")
    # #         dbg.write(f"originalUrl: {original_url}\n")
    # #         dbg.write("--- response_body START ---\n")
    # #         dbg.write((response_body if isinstance(response_body, str) else "<None or non-string>") + "\n")
    # #         dbg.write("--- response_body END ---\n")
    # #         dbg.write("--- full payload START ---\n")
    # #         dbg.write(payload_text + "\n")
    # #         dbg.write("--- full payload END ---\n\n")
    # # except Exception as e:
    # #     print("Failed to write product debug file:", e)

    # Extract all specificationGroups arrays found in the raw payload text
    specification_group_array_strings = extract_specification_groups_from_text(response_body or payload_text)
    print(f"Found {len(specification_group_array_strings)} specificationGroups arrays")

    global product_info
    # Join array-string captures into a single string per the requested behavior
    product_info = ",".join(specification_group_array_strings)

    return {"status": "received"}

@app.post("/services/conversation/web/api/v1/unified-chat/caip/message")
async def send_message(payload: MessageRequest = Body(...)):
    # Integrate with Azure OpenAI (via the lightweight wrapper in openai_client.py).
    # If the OpenAI client isn't configured or the call fails, fall back to the original echo response.
    user_text = payload.message.message or ""

    global product_info

    # If a product payload has been previously posted to /product, augment the user's text
    # with a brief excerpt of that product information to help the AI provide context-aware replies.
    if product_info:
        user_text = f"Question:\n{user_text} \n\n Product Info:\n{product_info}"
    else:
        print("No product info available to augment user message. Falling back to backend/assets/test_product1.txt for demo.")
        try:
            sample_path = os.path.join(os.path.dirname(__file__), "assets", "test_product1.txt")
            with open(sample_path, "r", encoding="utf-8") as f:
                sample_text = f.read()
            specification_group_array_strings = extract_specification_groups_from_text(sample_text)
            print(f"Fallback: found {len(specification_group_array_strings)} specificationGroups arrays in test_product1.txt")
            if specification_group_array_strings:
                product_info = ",".join(specification_group_array_strings)
                user_text = f"Question:\n{user_text} \n\n Product Info:\n{product_info}"
            else:
                print("Fallback: no specificationGroups found in test_product1.txt")
        except Exception as e:
            print("Fallback reading test_product1.txt failed:", e)
    display = f"ECHO1 {user_text}"

    try:
        # support importing the wrapper both as a top-level module and as a package-relative module
        try:
            from openai_client import OpenAIClient
        except Exception:
            from .openai_client import OpenAIClient

        client = OpenAIClient()
        ai_reply = client.chat_completion(
            user_message=user_text,
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