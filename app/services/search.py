# app/services/search.py
from typing import Dict, Any
from app.models.text_embedder import text_embedder
from app.models.image_embedder import image_embedder
from app.services import vector_store

def query_multimodal(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    文本查询 -> 同时检索 text_chunks（text->text）与 image_chunks（text->image via CLIP）
    返回结构:
    {
      "query": q,
      "texts": [{"score":..., "payload": {...}}...],
      "images": [{"score":..., "payload": {...}}...]
    }
    """
    # 文本嵌入（用于 text->text）
    text_vec = text_embedder.encode(query)[0]

    # CLIP 文本向量（用于 text->image）
    image_space_vec = image_embedder.encode_text([query])[0]

    texts = vector_store.search_text(text_vec, limit=top_k)
    images = vector_store.search_image(image_space_vec, limit=top_k)

    return {
        "query": query,
        "texts": texts,
        "images": images
    }
