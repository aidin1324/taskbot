from typing import Optional
from langchain_core.runnables import Runnable, RunnableConfig
from core.state import State
from pydantic import BaseModel
from core.config import get_settings
from langchain_openai import ChatOpenAI

settings = get_settings()
model = "gpt-4o-mini"
temperature = 0.2

# Initialize the language model (shared among assistants)
llm = ChatOpenAI(
    model=model,
    openai_api_key=settings.openai_api_key,
    temperature=temperature,
)


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    async def __call__(self, state: State, config: Optional[RunnableConfig] = None):
        while True:
            result = await self.runnable.ainvoke(state, config)
            if len(result.tool_calls) > 1:
                tool_call = result.tool_calls[0]
                for i in range(1, len(result.tool_calls)):
                    print(tool_call)
                    print("\n\n\n\n\n\n\n\n")
                    if result.tool_calls[i]["name"] == "ToTaskAssistant":
                        tool_call["args"]["user_request"] += " " + result.tool_calls[i]["args"]["user_request"]
                result.tool_calls = [tool_call]
                
            from rich.style import Style
            from rich.text import Text
            
            from rich.console import Console
            console = Console()
            value_style = Style(color="white")
            console.print(
                Text(f"ASSISTANT BASE: {result.tool_calls}", style=value_style)
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