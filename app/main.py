# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from typing import List
import os
from pathlib import Path

from app.services import parser, vector_store, search

DATA_DIR = Path("data")
UPLOAD_DIR = DATA_DIR / "uploads"
EXTRACT_DIR = DATA_DIR / "extracted"
IMAGE_DIR = DATA_DIR / "images"

for p in (UPLOAD_DIR, EXTRACT_DIR, IMAGE_DIR):
    p.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Multimodal Knowledge Base (MVP)")

@app.on_event("startup")
def startup_event():
    # 初始化向量数据库集合
    vector_store.init_collections()

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """
    上传文件（pdf / md / txt），解析并入库。
    返回插入的 chunk 数量。
    """
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    save_path = UPLOAD_DIR / filename
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 解析 -> 返回 chunk 列表
    try:
        chunks = parser.parse_file(str(save_path), extracted_dir=str(EXTRACT_DIR), image_dir=str(IMAGE_DIR))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse error: {e}")

    # 插入向量数据库
    try:
        inserted = vector_store.insert_chunks(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector store error: {e}")

    return {"status": "ok", "file": filename, "chunks": inserted}

@app.get("/search")
def search_endpoint(q: str = Query(..., description="text query"),
                    limit: int = Query(5, ge=1, le=50)):
    """
    多模态检索 API（文本查询 -> 返回文本与图片相似项）
    """
    try:
        res = search.query_multimodal(q, top_k=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return res
