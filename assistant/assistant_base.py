from typing import Optional
from langchain_core.runnables import Runnable, RunnableConfig
from core.state import State
from pydantic import BaseModel
from core.config import get_settings
from langchain_openai import ChatOpenAI

settings = get_settings()

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    async def __call__(self, state: State, config: Optional[RunnableConfig] = None):
        while True:
            result = await self.runnable.ainvoke(state, config)
            # print(result.tool_calls)
            # print("\n\n\n\n\n\n\n\n")
            if len(result.tool_calls) > 1:
                
                # delegate_tools = {
                #     "ToTaskAssistant": {} 
                # }
                # Если в списке есть вызов ToTaskAssistant, выбираем только его
                to_task_calls = [tc for tc in result.tool_calls if tc["name"] == "ToTaskAssistant"]
                if to_task_calls:
                    # Если их несколько, можно объединить аргументы, как делалось ранее
                    merged = to_task_calls[0]
                    for tc in to_task_calls[1:]:
                        merged["args"]["user_request"] += " " + tc["args"]["user_request"]
                    result.tool_calls = [merged]
                else:
                    # Иначе оставляем вызовы как есть (или объединяем остальные по вашему правилу)
                    result.tool_calls = result.tool_calls
                # new_formed_tool_calls = []
                # for i in range(len(result.tool_calls)):
                #     # print(tool_call)
                #     # print("\n\n\n\n\n\n\n\n")
                #     name = result.tool_calls[i]["name"]
                #     if name in delegate_tools:
                #         if not delegate_tools[name]:
                #             delegate_tools[name] = result.tool_calls[i]
                #         else:
                #             delegate_tools[name]["args"]["user_request"] += " " + result.tool_calls[i]["args"]["user_request"]
                #     else:
                #         new_formed_tool_calls.append(result.tool_calls[i])
                        
                # result.tool_calls = new_formed_tool_calls + [delegate_tools[x] for x in delegate_tools if delegate_tools[x]]
                
            from rich.style import Style
            from rich.text import Text
            
            from rich.console import Console
            console = Console()
            value_style = Style(color="yellow")
            console.print(
                Text(f"ASSISTANT ToolCall: {result.tool_calls}", style=value_style)
            )
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
            
        
        return {"messages": result} 

# Define the CompleteOrEscalate tool
class CompleteOrEscalate(BaseModel):
    """A tool to mark the current task as completed or to escalate control to the main assistant."""
    cancel: bool = True
    reason: str