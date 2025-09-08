# Basalt Chatbot API Schema Documentation

This document captures the system design perspective of the Basalt chatbot APIs, based on observed request/response interactions.

---

## 1. Chat Initialization API (`POST /services/conversation/web/api/v1/unified-chat/caip/init`)

```yaml
paths:
  /services/conversation/web/api/v1/unified-chat/caip/init:
    post:
      summary: Initialize a chatbot session
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                client:
                  type: object
                  properties:
                    firstName: { type: [string, "null"] }
                    lastName: { type: [string, "null"] }
                    email: { type: [string, "null"] }
                    phoneNumber: { type: [string, "null"] }
                    memberships:
                      type: object
                      properties:
                        isBetaMember: { type: boolean }
                        isTotalTechSupport: { type: boolean }
                    membershipList:
                      type: array
                      items: { type: string }
                    orderId: { type: string }
                id: { type: string } # typically empty
                message:
                  type: object
                  properties:
                    requestedProductDataType: { type: string } # e.g., "drawer"
                    client: { $ref: "#/components/schemas/ClientLite" }
                connection: { type: string, enum: ["connecting"] }
                provider:
                  type: object
                  properties:
                    currentProvider: { type: string } # usually "caip"
                    queue: { type: [string, "null"] }
                    previousProvider: { type: [string, "null"] }
                    channel: { type: string } # "chat"
                    pillar: { type: [string, "null"] }
                    category: { type: [string, "null"] }
                    chatAttributes: { type: [object, "null"] }
                requestedAgentPool: { type: string } # "caip"
                requestedAgentQueue: { type: [string, "null"] }
                clientId: { type: string }
                caipConversationId: { type: [string, "null"] }
                paidMember: { type: boolean }
                loggedInAtInitChat: { type: boolean }
                isNative: { type: boolean }
                chatSessionStart: { type: [string, "null"] }
                mediaTrack: { type: string, enum: ["text"] }
      responses:
        "200":
          description: Chat session initialized
          content:
            application/json:
              schema:
                type: object # actual response is compressed JSON, details vary
```

---

## 2. Chat Message API (`POST /services/conversation/web/api/v1/unified-chat/caip/message`)

```yaml
paths:
  /services/conversation/web/api/v1/unified-chat/caip/message:
    post:
      summary: Send a message within a chat session
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                client: { $ref: "#/components/schemas/ClientLite" }
                id: { type: string } # unique message-id-uuid
                message:
                  type: object
                  properties:
                    turnId: { type: integer } # incremented per user turn
                    msgTimestamp: { type: string, format: date-time }
                    latLong: { type: string } # "lat,long"
                    metadata:
                      type: object
                      properties:
                        more:
                          type: object
                          properties:
                            membershipState: { type: string } # e.g. "No"
                            logInState: { type: string } # e.g. "loggedOut"
                            referer: { type: string }
                            botSource: { type: string, enum: ["dfcx"] }
                            prevUtterance: { type: string }
                            requestedProductDataType: { type: string }
                            existingUtterance: { type: string }
                            intentName: { type: string } # e.g. "sales.purchase_product"
                            prevResponse: { type: string } # JSON string of last bot reply
                        correlationId: { type: string }
                        conversationId: { type: string }
                        genAI: { type: boolean }
                    message: { type: string } # user’s actual input
                    msgSource: { type: string, enum: ["user_typed", "system"] }
                connection: { type: string, enum: ["connected"] }
                provider:
                  type: object
                  properties:
                    currentProvider: { type: string }
                    queue: { type: [string, "null"] }
                    previousProvider: { type: [string, "null"] }
                    channel: { type: string }
                    pillar: { type: [string, "null"] }
                    category: { type: [string, "null"] }
                    chatAttributes: { type: [object, "null"] }
                requestedAgentPool: { type: string }
                requestedAgentQueue: { type: [string, "null"] }
                clientId: { type: string }
                caipConversationId: { type: string }
                paidMember: { type: boolean }
                loggedInAtInitChat: { type: boolean }
                isNative: { type: boolean }
                chatSessionStart: { type: [string, "null"] }
                mediaTrack: { type: string, enum: ["text"] }
      responses:
        "200":
          description: Chatbot/system response
          content:
            application/json:
              schema:
                type: object
                properties:
                  messages:
                    type: array
                    items:
                      type: object
                      properties:
                        type: { type: string } # "Text", "DynamicText"
                        displayText: { type: string }
                        hyperlinks: { type: array, items: { type: string } }
                        options: { type: array, items: { type: string } }
                        dynamicText: { type: array }
```

---

## 3. Shared Schema Component

```yaml
components:
  schemas:
    ClientLite:
      type: object
      properties:
        firstName: { type: [string, "null"] }
        lastName: { type: [string, "null"] }
        email: { type: [string, "null"] }
        phoneNumber: { type: [string, "null"] }
        memberships:
          type: object
          properties:
            isBetaMember: { type: boolean }
            isTotalTechSupport: { type: boolean }
        membershipList:
          type: array
          items: { type: string }
        orderId: { type: string }
```
