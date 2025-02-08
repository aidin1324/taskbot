from datetime import datetime, timedelta
from typing import Literal, Optional

from langchain_core.documents import Document
from langchain.tools import tool

from db.db import get_session

from utils.vector_search import VectorDB
from core.config import get_settings

from db import Task
from sqlalchemy import text

settings = get_settings()

task_vectordb = VectorDB(
    api_key=settings.openai_api_key,
    model="text-embedding-3-large",
    collection_name="tasks"
)

@tool
async def get_k_tasks_filter_date(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    k: int = 5
):
    """Get k tasks that fall within the specified date range."""
    if not start_date:
        start_date = datetime.now()
    if not end_date:
        end_date = datetime.now() + timedelta(days=7)
    try:
        async with get_session() as session:
            result = await session.execute(
                text("SELECT * FROM tasks WHERE start_date >= :start_date AND due_date <= :end_date LIMIT :k"),
                {"start_date": start_date, "end_date": end_date, "k": k}
            )
            tasks = result.fetchall()
            return f"Tasks found: {tasks}"
    except Exception as e:
        raise ValueError(f"Error getting tasks: {e}")


@tool
async def get_task(query: str):
    """Get a task by query."""
    try:
        # query vector DB and retrieve document metadata
        task_doc: Document = task_vectordb.query(query=query, top_k=1)
        if not task_doc:
            return "No task found"
        task_id = task_doc[0].metadata["id"]

        async with get_session() as session:
            result = await session.execute(
                text("SELECT * FROM tasks WHERE id = :task_id"),
                {"task_id": task_id}
            )
            fetched_task = result.fetchone()
            return f"Task found: {fetched_task}"
    except Exception as e:
        raise ValueError(f"Error getting task: {e}")


@tool
async def create_task(
    title: str,
    description: Optional[str],
    notify_at: datetime,
    start_date: datetime,
    completed_at: datetime,
    estimated_time: timedelta,
    eisenhower_category: Literal[
        "Urgent and Important",
        "Not Urgent but Important", 
        "Urgent but Not Important", 
        "Not Urgent and Not Important"
    ]
):
    """Create a new task. Use only when all arguments are specified by user."""
    try:
        async with get_session() as session:
            result = await session.execute(
                text("SELECT id FROM eisenhower_categories WHERE category = :category"),
                {"category": eisenhower_category}
            )
            eisenhower_cat_id = result.fetchone()[0]
            task: Task = Task(
                title=title,
                description=description,
                notify_at=notify_at,
                start_date=start_date,
                due_date=None,
                completed_at=completed_at,
                estimated_time=estimated_time.total_seconds() // 60,
                eisenhower_cat_id=eisenhower_cat_id
            )
            session.add(task)
            await session.flush()       # task becomes persistent
            await session.refresh(task) # gets updated attributes (e.g., task.id)
            task_id = task.id           # store id before commit
            await session.commit()
        task_doc = Document(
            page_content=title + (description if description else ""),
            metadata={"id": task_id}
        )
        return "Task created successfully"
    except Exception as e:
        raise ValueError(f"Error creating task: {e}")


# @tool
async def update_task(
    id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    notify_at: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    due_date: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    estimated_time: Optional[timedelta] = None,
    eisenhower_category: Optional[Literal[
        "Urgent and Important",
        "Not Urgent but Important", 
        "Urgent but Not Important", 
        "Not Urgent and Not Important"
    ]] = None
):
    """Update a task by id."""
    try:
        async with get_session() as session:
            # Optional: Check if task exists
            result = await session.execute(
                text("SELECT * FROM tasks WHERE id = :id"),
                {"id": id}
            )
            existing_task = result.fetchone()
            if not existing_task:
                return f"No task found with id {id}"
                
            if title:
                await session.execute(
                    text("UPDATE tasks SET title = :title WHERE id = :id"),
                    {"title": title, "id": id}
                )
            if description:
                await session.execute(
                    text("UPDATE tasks SET description = :description WHERE id = :id"),
                    {"description": description, "id": id}
                )
            if notify_at:
                await session.execute(
                    text("UPDATE tasks SET notify_at = :notify_at WHERE id = :id"),
                    {"notify_at": notify_at, "id": id}
                )
            if start_date:
                await session.execute(
                    text("UPDATE tasks SET start_date = :start_date WHERE id = :id"),
                    {"start_date": start_date, "id": id}
                )
            if due_date:
                await session.execute(
                    text("UPDATE tasks SET due_date = :due_date WHERE id = :id"),
                    {"due_date": due_date, "id": id}
                )
            if completed_at:
                await session.execute(
                    text("UPDATE tasks SET completed_at = :completed_at WHERE id = :id"),
                    {"completed_at": completed_at, "id": id}
                )
            if estimated_time:
                estimated_minutes = estimated_time.total_seconds() // 60
                await session.execute(
                    text("UPDATE tasks SET estimated_time = :estimated_time WHERE id = :id"),
                    {"estimated_time": estimated_minutes, "id": id}
                )
            if eisenhower_category:
                result_cat = await session.execute(
                    text("SELECT id FROM eisenhower_categories WHERE category = :category"),
                    {"category": eisenhower_category}
                )
                eisenhower_cat_id = result_cat.fetchone()[0]
                await session.execute(
                    text("UPDATE tasks SET eisenhower_cat_id = :eisenhower_cat_id WHERE id = :id"),
                    {"eisenhower_cat_id": eisenhower_cat_id, "id": id}
                )
            await session.commit()
            return "Task updated successfully"
    except Exception as e:
        raise ValueError(f"Error updating task: {e}")


@tool
async def delete_task(
    id: int
):
    """Delete a task by id."""
    try:
        async with get_session() as session:
            await session.execute(
                text("DELETE FROM tasks WHERE id = :id"),
                {"id": id}
            )
            await session.commit()
            return "Task deleted successfully"
    except Exception as e:
        raise ValueError(f"Error deleting task: {e}")


task_safe_tools = [get_k_tasks_filter_date, get_task]
task_sensitive_tools = [create_task, update_task, delete_task]

task_toolkit = task_safe_tools + task_sensitive_tools


# # Test section
# if __name__ == "__main__":
#     import asyncio

#     async def test_tools():
#         print("Creating a new task...")
#         create_result = await create_task(
#             title="Test task",
#             description="Test description",
#             notify_at=datetime.now(),
#             start_date=datetime.now(),
#             completed_at=datetime.now(),
#             estimated_time=timedelta(hours=1),
#             eisenhower_category="Urgent and Important"
#         )
#         print(create_result)

#         print("\nFiltering tasks...")
#         filter_result = await get_k_tasks_filter_date()
#         print(filter_result)

#         print("\nGetting task based on query...")
#         get_result = await get_task(query="Test task")
#         print(get_result)

#         print("\nUpdating the task...")
#         # Assuming task id 1 exists; replace with a valid id.
#         update_result = await update_task(
#             id=1,
#             title="Updated Test Task",
#             estimated_time=timedelta(minutes=90)
#         )
#         print(update_result)

#         print("\nDeleting the task...")
#         # Assuming task id 1 exists; replace with a valid id.
#         delete_result = await delete_task(id=1)
#         print(delete_result)

#     asyncio.run(test_tools())