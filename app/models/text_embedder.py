# app/models/text_embedder.py
from sentence_transformers import SentenceTransformer
from typing import List

class TextEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]):
        """
        支持批量编码，返回 numpy.float32 矩阵
        """
        if isinstance(texts, str):
            texts = [texts]
        emb = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return emb.astype("float32")

# 单例
text_embedder = TextEmbedder()

