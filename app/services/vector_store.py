# app/services/vector_store.py
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
import numpy as np
from typing import List, Dict
from uuid import uuid4

from app.models.text_embedder import text_embedder
from app.models.image_embedder import image_embedder

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

TEXT_COLLECTION = "text_chunks"
IMAGE_COLLECTION = "image_chunks"

def init_collections():
    """
    创建或确保 collections 存在
    text: dim 384 (all-MiniLM-L6-v2)
    image: dim 512 (clip)
    """
    # text collection
    if not client.get_collections().collections or TEXT_COLLECTION not in {c.name for c in client.get_collections().collections}:
        try:
            client.recreate_collection(
                collection_name=TEXT_COLLECTION,
                vectors_config=rest_models.VectorParams(size=384, distance=Distance.COSINE),
            )
        except Exception as e:
            # 如果 collection 已存在，recreate 可能报错（安全忽略）
            print(f"[vector_store] init text collection error (ignored): {e}")

    # image collection
    if not client.get_collections().collections or IMAGE_COLLECTION not in {c.name for c in client.get_collections().collections}:
        try:
            client.recreate_collection(
                collection_name=IMAGE_COLLECTION,
                vectors_config=rest_models.VectorParams(size=512, distance=Distance.COSINE),
            )
        except Exception as e:
            print(f"[vector_store] init image collection error (ignored): {e}")

def insert_chunks(chunks: List[Dict]) -> int:
    """
    将 parser 返回的 chunks 插入到 qdrant：
    - 每个 chunk 的 text 生成 text vector 并插入 text_chunks（payload 包含 chunk）
    - chunk.images 中每个图片单独生成 image vector 并插入 image_chunks（payload 包含 image path 与 source chunk id）
    返回插入总数（points count）
    """
    inserted = 0
    for ch in chunks:
        payload = {
            "chunk_id": ch["id"],
            "text": ch.get("text", ""),
            "source": ch.get("source", ""),
            "meta": ch.get("meta", {})
        }
        # 文本向量
        text = ch.get("text", "")
        if text and len(text.strip()) > 0:
            vec = text_embedder.encode(text)  # returns (1, dim)
            vec = vec[0].astype("float32")
            pid = str(uuid4())
            p = PointStruct(id=pid, vector=vec.tolist(), payload=payload)
            client.upsert(collection_name=TEXT_COLLECTION, points=[p])
            inserted += 1

        # 图片向量（chunk.images）
        imgs = ch.get("images", []) or []
        for img_path in imgs:
            try:
                vec_img = image_embedder.encode_image_path(img_path)
                payload_img = {
                    "chunk_id": ch["id"],
                    "image_path": img_path,
                    "source": ch.get("source", ""),
                    "meta": ch.get("meta", {})
                }
                pid = str(uuid4())
                p = PointStruct(id=pid, vector=vec_img.tolist(), payload=payload_img)
                client.upsert(collection_name=IMAGE_COLLECTION, points=[p])
                inserted += 1
            except Exception as e:
                print(f"[vector_store] failed embed image {img_path}: {e}")
                continue

    return inserted

def search_text(query_vector, limit: int = 5):
    hits = client.search(collection_name=TEXT_COLLECTION, query_vector=query_vector.tolist(), limit=limit)
    # 返回 (score, payload) 列表
    return [{"score": h.score, "payload": h.payload} for h in hits]

def search_image(query_vector, limit: int = 5):
    hits = client.search(collection_name=IMAGE_COLLECTION, query_vector=query_vector.tolist(), limit=limit)
    return [{"score": h.score, "payload": h.payload} for h in hits]
