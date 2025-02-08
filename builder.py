from core.state import State
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition
from langchain_core.runnables import RunnableConfig

from assistant.assistant_base import Assistant, CompleteOrEscalate
from assistant.primary_assistant import primary_assistant, primary_assistant_tools
from assistant.task_assistant import task_assistant

from schema.ToTaskAssistant import ToTaskAssistant
from assistant.task_assistant import task_assistant, task_assistant_tools

from utils.utils import create_entry_node, pop_dialog_state, create_tool_node_with_fallback

builder = StateGraph(State)
builder.add_node("leave_skill", pop_dialog_state)
builder.add_edge("leave_skill", "primary_assistant")


# task assistant
builder.add_node("enter_task_assistant", create_entry_node("task assistant", "task_assistant"))
builder.add_node("task_assistant", task_assistant)
builder.add_edge("enter_task_assistant", "task_assistant")

async def sync_task_assistant_tools(state):
  tool_node = create_tool_node_with_fallback(task_assistant_tools)
  return await tool_node.ainvoke(state)

builder.add_node("task_assistant_tools", sync_task_assistant_tools)

async def route_task_assistant(state: State):
  route = tools_condition(state)
  if route == END:
      print("END from task Assistant")
      return END
  tool_calls = state["messages"][-1].tool_calls
  did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
  if did_cancel:
      return "leave_skill"
  return "task_assistant_tools"

builder.add_conditional_edges(
  "task_assistant",
  route_task_assistant,
  ["task_assistant_tools", "leave_skill", END]
)
builder.add_edge("task_assistant_tools", "task_assistant")
      
# primary assistant
builder.add_node("primary_assistant", primary_assistant)
builder.add_edge(START, "primary_assistant") # START


builder.add_node(
  "primary_assistant_tools", create_tool_node_with_fallback(primary_assistant_tools)
)

def route_primary_assistant(state: State) -> Literal[
  "primary_assistant_tools",
  "enter_task_assistant",
  "__end__",
]:
  route = tools_condition(state)
  if route == END:
      return END
  tool_calls = state["messages"][-1].tool_calls
  if tool_calls:
    tool_name = tool_calls[0]["name"]
    if tool_name == ToTaskAssistant.__name__:
      return "enter_task_assistant"

  return "primary_assistant"


builder.add_conditional_edges(
  "primary_assistant",
  route_primary_assistant,
  ["primary_assistant_tools", "enter_task_assistant", END]
)

builder.add_edge("primary_assistant_tools", "primary_assistant")

memory = MemorySaver()
multi_agentic_graph = builder.compile(
  checkpointer=memory,
#   interrupt_before=interrupt_nodes,
)