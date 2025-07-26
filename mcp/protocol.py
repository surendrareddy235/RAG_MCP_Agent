# mcp/protocol.py

import uuid
from typing import Dict


class MCPMessage:
    def __init__(self, sender: str, receiver: str, type: str, trace_id: str = None, payload: Dict = None):
        self.sender = sender
        self.receiver = receiver
        self.type = type  # e.g., "DOCUMENT_PARSED", "RETRIEVAL_RESULT", etc.
        self.trace_id = trace_id or str(uuid.uuid4())
        self.payload = payload or {}

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.type,
            "trace_id": self.trace_id,
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            sender=data["sender"],
            receiver=data["receiver"],
            type=data["type"],
            trace_id=data.get("trace_id"),
            payload=data.get("payload", {})
        )

    def __repr__(self):
        return f"<MCPMessage type={self.type} trace_id={self.trace_id}>"
