from datetime import datetime, timedelta
from typing import Literal, Optional

from langchain_core.documents import Document
from langchain import tools

from db.db import get_session

from ..utils.vector_search import VectorDB
from core.config import get_settings

from db import Task

settings = get_settings()

task_vectordb = VectorDB(
    api_key=settings.openai_api_key,
    model="text-embedding-3-large",
    collection_name="tasks"
)

@tools
async def get_k_tasks_filter_date(
    start_date: Optional[datetime] = datetime.now(),
    end_date: datetime = datetime.now() + timedelta(days=7),
    k: int = 5
):
    try:
        async with get_session() as session:
            tasks = session.execute(
                f"SELECT * FROM tasks WHERE start_date>='{start_date}' AND due_date<='{end_date}' LIMIT {k}"
            ).fetchall()
            return f"Tasks found: {tasks}"
        
    except Exception as e:
        raise ValueError(f"Error getting tasks: {e}")
    
    
@tools
async def get_task(query: str):
    try:
        task: Document = task_vectordb.query(query=query, top_k=1)
        task_id = task.metadata["id"]
        
        async with get_session() as session:
            task = session.execute(f"SELECT * FROM tasks WHERE id={task_id}")
            return f"Task found: {task.fetchone()}"
    except Exception as e:
        raise ValueError(f"Error getting task: {e}")


@tools
async def create_task(
    title: str,
    description: str,
    notify_at: datetime,
    start_date: datetime,
    due_date: datetime,
    completed_at: datetime,
    estimated_time: datetime,
    eisenhower_category: Literal[
        "Urgent and Important",
        "Not Urgent but Important", 
        "Urgent but Not Important", 
        "Not Urgent and Not Important"
    ]
):
    try:
        async with get_session() as session:
            eisenhower_cat_id = session.execute(
                f"SELECT id FROM eisenhower_categories WHERE category='{eisenhower_category}'"
            ).fetchone()[0]
            task: Task = Task(
                title=title,
                description=description,
                notify_at=notify_at,
                start_date=start_date,
                due_date=due_date,
                completed_at=completed_at,
                estimated_time=estimated_time,
                eisenhower_cat_id=eisenhower_cat_id
            )
        
        task_doc = Document(
            content=description,
            metadata={"id": task.id}
        )
        
        return "Task created successfully"
    except Exception as e:
        raise ValueError(f"Error creating task: {e}")


@tools
async def update_task(
    id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    notify_at: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    due_date: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    estimated_time: Optional[datetime] = None,
    eisenhower_category: Optional[Literal[
        "Urgent and Important",
        "Not Urgent but Important", 
        "Urgent but Not Important", 
        "Not Urgent and Not Important"
    ]] = None
):
    try:
            
        async with get_session() as session:
            task = session.execute(f"SELECT * FROM tasks WHERE id={id}").fetchone()
            
            if title:
                session.execute(f"UPDATE tasks SET title='{title}' WHERE id={id}")
            if description:
                session.execute(f"UPDATE tasks SET description='{description}' WHERE id={id}")
            if notify_at:
                session.execute(f"UPDATE tasks SET notify_at='{notify_at}' WHERE id={id}")
            if start_date:
                session.execute(f"UPDATE tasks SET start_date='{start_date}' WHERE id={id}")
            if due_date:
                session.execute(f"UPDATE tasks SET due_date='{due_date}' WHERE id={id}")
            if completed_at:
                session.execute(f"UPDATE tasks SET completed_at='{completed_at}' WHERE id={id}")
            if estimated_time:
                session.execute(f"UPDATE tasks SET estimated_time='{estimated_time}' WHERE id={id}")
            if eisenhower_category:
                eisenhower_cat_id = session.execute(
                    f"SELECT id FROM eisenhower_categories WHERE category='{eisenhower_category}'"
                ).fetchone()[0]
                session.execute(f"UPDATE tasks SET eisenhower_cat_id='{eisenhower_cat_id}' WHERE id={id}")
            return "Task updated successfully"
    except Exception as e:
        raise ValueError(f"Error updating task: {e}")


@tools
async def delete_task(
    id: int
):
    try:
        async with get_session() as session:
            session.execute(f"DELETE FROM tasks WHERE id={id}")
            return "Task deleted successfully"
    except Exception as e:
        raise ValueError(f"Error deleting task: {e}")   
    


task_safe_tools = [get_k_tasks_filter_date, get_task]
task_sensitive_tools = [create_task, update_task, delete_task]

task_toolkit = task_safe_tools + task_sensitive_tools