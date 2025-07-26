# agents/llm_response_agent.py

import google.generativeai as genai
from mcp.protocol import MCPMessage
from dotenv import load_dotenv
import os
load_dotenv()

# === Configure Gemini API ===
genai.configure(api_key=os.getenv("YOUR_GEMINI_API_KEY"))  # replace with your real key

# === Load the Gemini Model ===
model = genai.GenerativeModel("gemini-1.5-flash")


# === LLM Response Agent ===
class LLMResponseAgent:
    def __init__(self, name="LLMResponseAgent"):
        self.name = name

    def handle(self, mcp_message: MCPMessage) -> MCPMessage:
        if mcp_message.type != "RETRIEVAL_RESULT":
            raise ValueError(f"{self.name} cannot handle type: {mcp_message.type}")

        context_chunks = mcp_message.payload.get("retrieved_context", [])
        query = mcp_message.payload.get("query", "")
        chat_history = mcp_message.payload.get("history", [])

        prompt = self.format_prompt(context_chunks, query, chat_history)

        response = model.generate_content(prompt)

        return MCPMessage(
            sender=self.name,
            receiver="UI",
            type="FINAL_ANSWER",
            trace_id=mcp_message.trace_id,
            payload={
                "query": query,
                "answer": response.text,
                "sources": context_chunks
            }
        )

    def format_prompt(self, context_chunks, query, chat_history=[]):
        history_str = "\n".join([f"User: {turn['query']}\nBot: {turn['answer']}" for turn in chat_history])
        context_str = "\n".join(context_chunks)

        return f"""{history_str}

Use the following context to answer the question.

Context:
{context_str}

Question: {query}
Answer:"""