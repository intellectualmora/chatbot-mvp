import logging
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langsmith import traceable

@traceable(name="build_vectorstore")
def build_vectorstore(docs, user_id: str = None,is_public: bool = False, base_dir="vectorstores"):
    """
    为指定用户或公共空间构建向量库 (Chroma版)
    :param docs: 已加载的文档列表
    :param user_id: 用户唯一标识 (None 表示公共向量库)
    :param base_dir: 向量库存放根目录
    :return: 保存后的 vectorstore
    """
    # 检查 key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("未检测到 DASHSCOPE_API_KEY，请在 .env 或 环境变量中设置。")

    # 公共 / 私有 存储路径
    if is_public:
        persist_dir = os.path.join(base_dir, "public")
        logging.info(f"正在构建公共向量库 -> {persist_dir}")
    else:
        persist_dir = os.path.join(base_dir, "private", str(user_id))
        logging.info(f"正在为用户 {user_id} 构建私人向量库 -> {persist_dir}")

    os.makedirs(persist_dir, exist_ok=True)

    # 文本切分
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    # 构建向量库并持久化
    embeddings = DashScopeEmbeddings(model="text-embedding-v1")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    return vectorstore

def get_vectorstore(user_id: str = None, base_dir: str = "vectorstores") -> Chroma:
    """
    加载 Chroma 向量库
    - user_id=None: 加载公共库
    - user_id=xxx: 优先加载用户私有库，若不存在则回退到公共库
    """
    embeddings = DashScopeEmbeddings(model="text-embedding-v1")

    if user_id:
        private_dir = os.path.join(base_dir, "private", str(user_id))
        if os.path.exists(private_dir):
            logging.info(f"加载用户 {user_id} 的私人向量库 -> {private_dir}")
            return Chroma(persist_directory=private_dir, embedding_function=embeddings)
        else:
            logging.info(f"用户 {user_id} 的私人库不存在，回退到公共库")

    public_dir = os.path.join(base_dir, "public")
    if os.path.exists(public_dir):
        logging.info(f"加载公共向量库 -> {public_dir}")
        return Chroma(persist_directory=public_dir, embedding_function=embeddings)

    raise FileNotFoundError("未找到可用的向量库（无公共库 & 无用户私有库）")
