import os
import logging
import chardet
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.documents import Document

def detect_encoding(file_path: str, sample_size: int = 50000) -> str:
    """大文件编码检测（采样 + chardet）"""
    length = os.path.getsize(file_path)
    with open(file_path, "rb") as f:
        # 开头
        raw_start = f.read(sample_size)
        # 中间
        if length > 2 * sample_size:
            f.seek(length // 2)
            raw_middle = f.read(sample_size)
        else:
            raw_middle = b""
        # 结尾
        f.seek(-min(sample_size, length), os.SEEK_END)
        raw_end = f.read(sample_size)

    raw = raw_start + raw_middle + raw_end
    result = chardet.detect(raw)
    return result["encoding"] or "utf-8"


def load_document(file_path: str):
    ext = Path(file_path).suffix.lower()
    logging.info(f"Loading file: {file_path}")

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
        return loader.load()

    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
        return loader.load()

    elif ext in [".txt", ".md"]:
        # 自动检测编码
        encoding = detect_encoding(file_path)
        logging.info(f"Detected encoding for {file_path}: {encoding}")

        # 常见编码 fallback
        candidates = [encoding,  "utf-8", "utf-8-sig",
        "gb18030", "gbk", "gb2312", "hz",
        "big5", "big5hkscs",
        "utf-16", "utf-16le", "utf-16be",
        "utf-32", "utf-32le", "utf-32be"]

        for enc in candidates:
            if not enc:
                continue
            try:
                loader = TextLoader(file_path, encoding=enc)
                doc = loader.load()
                logging.warning(f"编码格式为 {enc} 成功")
                return doc
            except Exception as e:
                logging.warning(f"尝试编码 {enc} 失败: {e}")
                continue

        raise ValueError(f"无法解码文件: {file_path}")

    else:
        raise ValueError(f"不支持的文件类型: {ext}")
