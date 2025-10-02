from dotenv import load_dotenv

from app.api.requests import ChatRequest, HistoryRequest

load_dotenv()
from fastapi import FastAPI, UploadFile, File,Form
from langchain_core.messages import HumanMessage
from app.graph.graph import build_graph
from app.ingest.loader import load_document
from app.ingest.vectorstore import build_vectorstore
import os
app = FastAPI(title="Chatbot MVP (LangGraph + FastAPI)")

# 构建 LangGraph 应用
graph_app = build_graph()

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    cfg = {"configurable": {"thread_id": req.user_id}}
    prev_state = graph_app.get_state(cfg)
    messages = prev_state.values.get("messages", [])
    messages.append(HumanMessage(content=req.message))
    result = graph_app.invoke({"messages": messages, "user_id": req.user_id}, cfg)
    ai_msg = result["messages"][-1].content
    return {"user_id": req.user_id, "answer": ai_msg}

@app.post("/history")
def get_history(req: HistoryRequest):
    """获取某个用户的完整历史对话"""
    cfg = {"configurable": {"thread_id": req.user_id}}
    state = graph_app.get_state(cfg)
    messages = state.values.get("messages", [])

    return {
        "user_id": req.user_id,
        "history": [{"role": m.type, "content": m.content} for m in messages]
    }

@app.post("/upload")
def upload_doc(user_id: str = Form(...), is_public: bool = Form(False) ,file: UploadFile = File(...)):
    """上传文档并更新对应的向量库"""

    if is_public:
        docs_dir = "docs/public"
        msg_scope = "公共库"
    else:
        if not user_id:
            return {"status": "error", "msg": "私人知识库必须提供 user_id"}
        docs_dir = f"docs/private/{user_id}"
        msg_scope = f"用户 {user_id} 的私人库"

    os.makedirs(docs_dir, exist_ok=True)
    path = os.path.join(docs_dir, file.filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    docs = load_document(path)
    build_vectorstore(docs,user_id=user_id,is_public=is_public)

    return {"status": "ok", "msg": f"{file.filename} 已加入 {msg_scope}"}