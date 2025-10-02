from typing import Dict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import GraphState
from .nodes import retrieve_node, generate_node, router

def build_graph():
    workflow = StateGraph(GraphState)

    # 注册节点
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)

    # 入口：先检索
    workflow.set_entry_point("retrieve")

    # 路由：检索 -> generate；generate -> 结束
    workflow.add_conditional_edges(
        "retrieve",
        router,
        {
            "generate": "generate"
        }
    )
    workflow.add_edge("generate", END)

    # 使用内存检查点保存对话
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app
