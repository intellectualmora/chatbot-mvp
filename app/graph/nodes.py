from typing import Dict, List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langsmith import traceable
from app.ingest.vectorstore import get_vectorstore

@traceable(name="Retriever")
def retrieve_node(state: Dict) -> Dict:
    """读取用户最后一句，做向量检索，把命中的片段塞进 state['contexts']"""
    messages: List = state.get("messages", [])
    user_id:str = state.get("user_id", "")
    last_user = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), None)
    if last_user is None:
        return state
    retriever = get_vectorstore(user_id=user_id).as_retriever(search_kwargs={"k": 4})
    docs = retriever.vectorstore.similarity_search_with_score(last_user.content, k=4)
    contexts = []
    for d, score in docs:
        meta = d.metadata or {}
        cite = f"(source: {meta.get('source', 'N/A')}, page: {meta.get('page', 'N/A')},score: {score:.2f})"
        contexts.append(d.page_content.strip() + f"\n{cite}")

    new_state = dict(state)
    new_state["contexts"] = contexts

    return new_state

@traceable(name="Generator")
def generate_node(state: Dict) -> Dict:
    messages: List = state.get("messages", [])
    contexts: List[str] = state.get("contexts", [])

    system_inst = (
        "你是一个依据文档回答问题的助手。"
        "必须严格基于提供的上下文回答，无法从上下文得到的信息请明确说明。"
        "回答末尾附上引用。"
    )

    context_block = "\n\n".join(
        [f"【片段{i+1}】\n{ctx}" for i, ctx in enumerate(contexts)]
    ) or "（当前没有可用上下文）"

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_inst),
        SystemMessage(content=f"可用上下文：\n{context_block}"),
        MessagesPlaceholder(variable_name="messages"),
    ])

    llm = ChatTongyi(model="qwen3-max")
    chain = prompt | llm

    ai_msg = chain.invoke({"messages": messages})   # 已是 AIMessage
    new_messages = messages + [ai_msg]

    new_state = dict(state)
    new_state["messages"] = new_messages
    return new_state

@traceable(name="Router")
def router(state: Dict) -> str:
    # TODO 其他工具加进来后可用
    return "generate"
