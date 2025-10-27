# app/utils/file_utils.py
import os
import re
from pathlib import Path
import fitz  # PyMuPDF
import markdown
from bs4 import BeautifulSoup
from typing import Dict, List
import requests
import uuid
from urllib.parse import urlparse
import shutil

def _safe_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    if not name:
        name = str(uuid.uuid4()) + ".png"
    return name

def download_and_save_image(img_ref: str, image_dir: str) -> str:
    """
    如果 img_ref 是 url -> 下载并保存到 image_dir，返回本地路径
    如果 img_ref 是本地路径 -> 尝试复制到 image_dir 并返回新路径（或直接返回原路径）
    """
    os.makedirs(image_dir, exist_ok=True)
    if img_ref.startswith("http://") or img_ref.startswith("https://"):
        try:
            r = requests.get(img_ref, timeout=10, stream=True)
            r.raise_for_status()
            filename = _safe_filename_from_url(img_ref)
            save_path = os.path.join(image_dir, filename)
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return save_path
        except Exception as e:
            print(f"[file_utils] download failed {img_ref}: {e}")
            return ""
    else:
        # local path - if exists, copy into image_dir or just return original absolute path
        if os.path.exists(img_ref):
            try:
                dest = os.path.join(image_dir, os.path.basename(img_ref))
                if os.path.abspath(img_ref) != os.path.abspath(dest):
                    shutil.copy(img_ref, dest)
                return dest
            except Exception as e:
                print(f"[file_utils] copy failed {img_ref}: {e}")
                return img_ref
        else:
            print(f"[file_utils] image path not found: {img_ref}")
            return ""

def extract_from_pdf(file_path: str) -> Dict:
    """
    从 PDF 中提取文本（按页聚合）和图片资源列表（图片保存为 bytes -> 由 parser 再保存）
    返回 {"text": "...", "images": ["path_or_url", ...]}
    """
    text_content = ""
    images = []
    doc = fitz.open(file_path)
    for page_index, page in enumerate(doc):
        page_text = page.get_text("text")
        if page_text:
            text_content += page_text + "\n\n"
        # find images references via page.get_images
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                img_bytes = pix.tobytes(output="png")
                # produce a temp path under same folder as pdf
                images.append(("bytes", img_bytes))
                pix = None
            except Exception as e:
                print(f"[file_utils] pdf image extract failed p{page_index} i{img_index}: {e}")
    return {"text": text_content, "images": images}

def extract_from_md(file_path: str) -> Dict:
    """
    解析 Markdown：提取文本（转换 html -> text）和图片链接（本地或远程）
    """
    with open(file_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 提取图片链接 Markdown 语法
    img_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
    images = img_pattern.findall(md_content)

    # 转成 html 后再提取文本
    html = markdown.markdown(md_content)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n")
    return {"text": text, "images": images}

def extract_from_txt(file_path: str) -> Dict:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return {"text": text, "images": []}

def load_file(file_path: str) -> Dict:
    """
    统一入口：返回 {'text':..., 'images': [...]}
    images 元素可能为:
      - URL string
      - local path string
      - tuple ('bytes', b'...') 表示从 pdf 中直接提取的 bytes
    parser 会负责将 bytes 保存为文件
    """
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return extract_from_pdf(file_path)
    elif suffix in (".md", ".markdown"):
        return extract_from_md(file_path)
    elif suffix == ".txt":
        return extract_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
