import sys

from dotenv import load_dotenv
load_dotenv()
import argparse
import os
import logging
from app.ingest.loader import load_document
from app.ingest.vectorstore import build_vectorstore

# 日志配置
logging.basicConfig(
    level=logging.INFO,   # 默认 INFO，可改成 DEBUG
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def download_models():
    """模拟拉取模型"""
    logger.info("正在准备模型...")
    # TODO
    logger.info("模型准备完成！")


def build_index(user_id: str = None,is_public:bool=False):
    """
    从 docs/ 目录加载文档并构建向量库
    - user_id=None: 构建公共向量库 (只用 docs/public)
    - user_id=xxx: 构建对应用户的私人向量库 (公共 + 私人)
    """
    all_docs = []

    # 公共文档（总是加载）
    public_dir = "docs/public"
    if os.path.exists(public_dir):
        for fname in os.listdir(public_dir):
            fpath = os.path.join(public_dir, fname)
            all_docs.extend(load_document(fpath))
    else:
        logger.warning(f"公共文档目录 {public_dir} 不存在，跳过。")

    # 私人文档（仅在 user_id 存在时加载）
    if not is_public:
        private_dir = f"docs/private/{user_id}"
        if os.path.exists(private_dir):
            for fname in os.listdir(private_dir):
                fpath = os.path.join(private_dir, fname)
                all_docs.extend(load_document(fpath))
        else:
            logger.warning(f"用户 {user_id} 的私人文档目录 {private_dir} 不存在，跳过。")

    build_vectorstore(all_docs,is_public=is_public)
    logger.info("向量索引已构建完成！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-models", action="store_true")
    parser.add_argument("--build-index", action="store_true")
    args = parser.parse_args()

    if args.download_models:
        download_models()
    if args.build_index:
        build_index(is_public=True)
