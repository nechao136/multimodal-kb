# app/services/parser.py
"""
parser.py
负责接收文件路径，解析文本与图片，产生 chunk 列表。
每个 chunk 为 dict:
{
  "id": ...,
  "text": "...",
  "images": ["data/images/xxx.png", ...],
  "source": "uploads/name.pdf",
  "meta": {"page": n}
}
"""
import os
from pathlib import Path
from typing import List, Dict
import uuid
from app.utils.file_utils import load_file, download_and_save_image
from app.utils.image_utils import ensure_image_saved

def _make_chunk(text: str, images: List[str], source: str, meta: Dict = None):
    return {
        "id": str(uuid.uuid4()),
        "text": text or "",
        "images": images or [],
        "source": source,
        "meta": meta or {}
    }

def split_text_into_paragraphs(text: str, min_len: int = 50) -> List[str]:
    """
    简单按换行分段，并合并过短段落
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return []
    paras = []
    buf = ""
    for line in lines:
        if len(buf) == 0:
            buf = line
        else:
            if len(buf) < min_len:
                buf = buf + " " + line
            else:
                paras.append(buf)
                buf = line
    if buf:
        paras.append(buf)
    return paras

def parse_file(path: str, extracted_dir: str = "data/extracted", image_dir: str = "data/images") -> List[Dict]:
    """
    解析文件，返回 chunk 列表并将远程图片下载到 image_dir
    """
    path = str(path)
    fileinfo = load_file(path)
    text = fileinfo.get("text", "")
    images = fileinfo.get("images", [])  # 可能是本地路径或 URL

    os.makedirs(extracted_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    # 先把图片（如果是 URL）下载到 image_dir；如果是 local path, 尝试复制/确认其存在
    saved_images = []
    for img in images:
        try:
            saved = download_and_save_image(img, image_dir)
            if saved:
                saved_images.append(saved)
        except Exception as e:
            print(f"[parser] image save failed {img}: {e}")

    # 将文本切分为段落 chunk
    chunks = []
    paras = split_text_into_paragraphs(text)
    if paras:
        for i, p in enumerate(paras):
            ch = _make_chunk(p, saved_images if i == 0 else [], source=path, meta={"para_index": i})
            chunks.append(ch)
    else:
        # 没有文本，但可能只有图片（如纯图片 PDF）
        if saved_images:
            ch = _make_chunk("", saved_images, source=path, meta={})
            chunks.append(ch)

    return chunks
