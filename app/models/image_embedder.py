# app/models/image_embedder.py
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import numpy as np
from typing import List, Union
import os

class ImageEmbedder:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", device: str = None):
        # 自动选择 GPU（如果可用）
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def encode_image(self, pil_image: Image.Image):
        """
        输入：PIL Image
        输出：numpy float32 向量 (512,)
        """
        inputs = self.processor(images=pil_image, return_tensors="pt")
        # 将 tensors 移到 device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            img_features = self.model.get_image_features(**inputs)
        vec = img_features[0].cpu().numpy().astype("float32")
        return vec

    def encode_image_path(self, image_path: str):
        img = Image.open(image_path).convert("RGB")
        return self.encode_image(img)

    def encode_images(self, image_paths: List[str]):
        out = []
        for p in image_paths:
            try:
                v = self.encode_image_path(p)
                out.append(v)
            except Exception as e:
                print(f"[image_embedder] failed {p}: {e}")
        if out:
            return np.stack(out, axis=0)
        return np.zeros((0, self.model.config.projection_dim), dtype="float32")

    def encode_text(self, texts: List[str]):
        """
        用 CLIP 的 text encoder 得到 text->image-space 的向量（用于 text->image 检索）
        """
        if isinstance(texts, str):
            texts = [texts]
        inputs = self.processor(text=texts, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            txt_features = self.model.get_text_features(**inputs)
        return txt_features.cpu().numpy().astype("float32")

# 单例
image_embedder = ImageEmbedder()
