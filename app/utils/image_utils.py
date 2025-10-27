# app/utils/image_utils.py
import os
from typing import Optional
from PIL import Image
import io
import base64
import uuid

def ensure_image_saved(img_source, image_dir: str) -> Optional[str]:
    """
    将不同来源的图片统一保存为本地文件并返回本地路径。
    img_source 可为:
      - tuple('bytes', b'...')  --> 保存二进制
      - 本地路径字符串         --> 若存在则返回路径
      - URL 字符串            --> 不在此模块处理（由 file_utils.download_and_save_image 处理）
    """
    os.makedirs(image_dir, exist_ok=True)

    if isinstance(img_source, tuple) and img_source[0] == "bytes":
        data = img_source[1]
        fname = f"{uuid.uuid4().hex}.png"
        out_path = os.path.join(image_dir, fname)
        try:
            with open(out_path, "wb") as f:
                f.write(data)
            return out_path
        except Exception as e:
            print(f"[image_utils] save bytes failed: {e}")
            return None

    elif isinstance(img_source, str):
        # assume local path
        if os.path.exists(img_source):
            return img_source
        else:
            print(f"[image_utils] image path not exists: {img_source}")
            return None
    else:
        print(f"[image_utils] unsupported image source: {type(img_source)}")
        return None
