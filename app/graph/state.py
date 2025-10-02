from typing import List, TypedDict, Optional
from langchain_core.messages import AnyMessage

class GraphState(TypedDict, total=False):
    # 全量对话历史（system/user/ai）
    messages: List[AnyMessage]
    # 当前轮检索到的文档片段（可选，用于调试或可视化）
    contexts: Optional[List[str]]
    user_id: str

