# Начать делать taskAssistant, затем task_assistant
from tool.tasks import task_toolkit

from datetime import datetime
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from core.config import get_settings
from .assistant_base import Assistant, CompleteOrEscalate


settings = get_settings()

task_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a specialized assistant for task management and organization. The primary assistant delegates work to you whenever the user needs assistance with managing tasks, scheduling, and ensuring that all work is executed efficiently.
            When handling task management, you must:
            - Be thorough: If your initial query or task organization returns incomplete results, expand your search criteria or request additional information.
            - Always include a temporary task ID in your responses for reference.
            - Break down larger tasks into smaller, manageable subtasks.
            - Escalate the task back to the primary assistant if you require additional details or if the user's request gets revised.
            - Confirm that the corresponding tool has been successfully executed before finalizing any task outcome.
            Please, every argument in tool should be specified by user, you should not invent any arguments.
            Current time: {time}.

            If the user's needs cannot be met by any of your available tools or if uncertainty persists, immediately 'CompleteOrEscalate' the conversation to the primary assistant. Do not waste the user's time or invent non-existent tools or functions.

            Your role is to provide clear, efficient, and prompt task management support that seamlessly integrates with the overall workflow.    
            """
        ),
        ("placeholder", "{messages}")
    ]
).partial(time=datetime.now)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=settings.openai_api_key,
    verbose=True,
    temperature=0
)

task_assistant_tools = task_toolkit + [CompleteOrEscalate]

task_assistant_runnable = task_assistant_prompt | llm.bind_tools(
    task_assistant_tools
)

task_assistant = Assistant(task_assistant_runnable)