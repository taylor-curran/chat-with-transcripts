"""
Utils for ChromaDB collections.
"""

import os

import chromadb
import chromadb.utils.embedding_functions as embedding_functions

CHROMA_DB_PATH = (
    "/Users/taylorcurran/Documents/tay/chat-with-transcripts/presales_chromadb"
)
EMBEDDING_MODEL_NAME = "text-embedding-3-small"


def get_collection():
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"), model_name=EMBEDDING_MODEL_NAME
    )
    collection = chroma_client.get_or_create_collection(
        "presale_calls", embedding_function=openai_ef
    )
    return collection
