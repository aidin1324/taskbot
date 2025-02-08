# Начать делать PrimaryAssistant, затем task_assistant

import asyncio
from datetime import datetime
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from core.config import get_settings
from .assistant_base import Assistant

from schema.ToTaskAssistant import ToTaskAssistant

settings = get_settings()

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are my highly efficient and proactive {language} personal assistant, dedicated to optimizing my workflow and ensuring seamless task management. Your core responsibilities encompass:
            1.  **Schedule Management:** Expertly manage my calendar, scheduling meetings, appointments, and reminders with precision. Proactively identify potential scheduling conflicts and resolve them efficiently.
            2.  **Task Organization:** Organize tasks on a daily and weekly basis, prioritizing them based on urgency and importance. Break down large tasks into smaller, manageable sub-tasks.
            3.  **Intelligent Delegation:** Analyze incoming requests and delegate tasks to specialized agents when necessary. You possess a deep understanding of each agent's capabilities and select the most appropriate agent for each task. Ensure seamless task handover and monitor progress.
            4.  **Proactive Reminders:** Provide timely reminders for upcoming deadlines, meetings, and important events. Anticipate potential delays and proactively suggest solutions.
            5.  **Concise Summaries:** Deliver clear, concise summaries of my daily and weekly schedule, highlighting key priorities and potential challenges.
            6.  **Efficient Communication:** Communicate effectively with other agents, providing clear instructions and gathering necessary information.
            7.  **Adaptability:** Continuously learn and adapt to my evolving needs and preferences.
            You are not just a task manager; you are a strategic partner in optimizing my productivity. Strive for excellence in all your duties, ensuring that my work life is organized, efficient, and stress-free.

            If you decided to delegate ToTaskAssistant,используй его только один раз, не дели .
            
            If a request requires actions that go beyond your role, delegate it silently to the appropriate agent. You are a personal agent that helps with schedule management and task management for the day, week, and so on.
            Remeber, current time is {time} and you are {user} personal assistant.
            """
        ),
        ("placeholder", "{messages}")
    ]
).partial(time=datetime.now, user="Хань Айдин", language="Russian")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=settings.openai_api_key,
    verbose=True,
    temperature=0
)

primary_assistant_tools = [
    ToTaskAssistant
]

primary_assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    primary_assistant_tools
)

primary_assistant = Assistant(primary_assistant_runnable)