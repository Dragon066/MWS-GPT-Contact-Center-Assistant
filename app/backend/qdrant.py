import os

import pandas as pd
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL")
LLM_EMBEDDING_VECTOR_SIZE = os.getenv("LLM_EMBEDDING_VECTOR_SIZE")

llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
qdrant_client = QdrantClient(host="qdrant", port=6333)


def get_embeds(texts: list[str], batch_size: int = 128):
    result = []
    for i in range(0, len(texts), batch_size):
        emb = llm_client.embeddings.create(
            model=LLM_EMBEDDING_MODEL,
            input=texts[i : i + batch_size],
        )
        result.extend(emb.data)

    return result


async def create_collection_from_file(collection_name: str, file_csv):
    df = pd.read_csv(file_csv, index_col=0)

    if is_collection_exists(collection_name):
        qdrant_client.delete_collection(collection_name)

    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=LLM_EMBEDDING_VECTOR_SIZE, distance=Distance.COSINE
        ),
    )

    vectorized = get_embeds(df.iloc[:, 0].to_list())

    points = [
        PointStruct(
            id=i, vector=vectorized[i].embedding, payload=df.iloc[i, 1:].to_dict()
        )
        for i in range(len(df))
    ]

    qdrant_client.upload_points(collection_name=collection_name, points=points)

    return True


def is_collection_exists(collection_name: str):
    try:
        return qdrant_client.get_collection(collection_name) is not None
    except Exception:
        return False


def get_collection(collection_name: str):
    if not is_collection_exists(collection_name):
        raise ValueError(f"Collection {collection_name} not found")
    return qdrant_client.get_collection(collection_name)


def get_topk_results(collection_name: str, text: str, k: int = 3):
    emb = (
        llm_client.embeddings.create(
            model=LLM_EMBEDDING_MODEL,
            input=text,
        )
        .data[0]
        .embedding
    )
    most_relevant = qdrant_client.query_points(
        collection_name=collection_name, query=emb, limit=k
    )
    most_relevant = [m.payload for m in most_relevant.points]

    return most_relevant
