# agents/retrieval_agent.py
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from mcp.protocol import MCPMessage
import os
import pickle

# === Setup vector store path ===
VECTOR_DB_PATH = "vector_store/faiss_index"

class RetrievalAgent:
    def __init__(self, name="RetrievalAgent"):
        self.name = name
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # Try to load existing FAISS index
        if os.path.exists(VECTOR_DB_PATH):
            with open(f"{VECTOR_DB_PATH}.pkl", "rb") as f:
                self.vectorstore = pickle.load(f)
        else:
            self.vectorstore = None

    def handle(self, mcp_message: MCPMessage) -> MCPMessage:
        if mcp_message.type != "DOCUMENT_PARSED":
            raise ValueError(f"{self.name} cannot handle message type: {mcp_message.type}")

        documents = mcp_message.payload.get("documents", [])
        query = mcp_message.payload.get("query", "")

        # Convert strings to Document objects
        docs = [Document(page_content=d) for d in documents]

        # Split documents into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        chunks = splitter.split_documents(docs)

        # Embed and store in FAISS
        self.vectorstore = FAISS.from_documents(chunks, self.embedding_model)

        # Save for reuse
        with open(f"{VECTOR_DB_PATH}.pkl", "wb") as f:
            pickle.dump(self.vectorstore, f)

        # Retrieve top chunks
        top_k = 4
        results = self.vectorstore.similarity_search(query, k=top_k)
        retrieved_chunks = [doc.page_content for doc in results]

        # Return new MCP message with retrieved chunks
        return MCPMessage(
            sender=self.name,
            receiver="LLMResponseAgent",
            type="RETRIEVAL_RESULT",
            trace_id=mcp_message.trace_id,
            payload={
                "retrieved_context": retrieved_chunks,
                "query": query
            }
        )
