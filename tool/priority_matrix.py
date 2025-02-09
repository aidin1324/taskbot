from datetime import datetime
from langchain.tools import tool
from sqlalchemy import text

from db.db import get_session
from utils.priority_matrix import render_priority_matrix


@tool
async def get_priority_matrix(day: datetime) -> list[dict]:
    """Get the priority matrix for a given day."""
    try:
        async with get_session() as session:
            
            stmt = text(
                """
                SELECT t.title, t.start_date, t.description, t.estimated_time, t.eisenhower_cat_id
                FROM tasks as t
                JOIN eisenhower_categories as ec
                ON t.eisenhower_cat_id = ec.id
                WHERE DATE(t.start_date) = DATE(:day)
                ORDER BY t.start_date
                """
            )
            result = await session.execute(stmt, {"day": day.date()})
            tasks = result.fetchall()
            
        column = ["title", "start_date", "description", "estimated_time", "eisenhower_cat_id"]
        tasks = [dict(zip(column, task)) for task in tasks]
        
        months = {
            1: "января",
            2: "февраля",
            3: "марта",
            4: "апреля",
            5: "мая",
            6: "июня",
            7: "июля",
            8: "августа",
            9: "сентября",
            10: "октября",
            11: "ноября",
            12: "декабря"
        }
        day_number = day.day
        month_str = months[day.month]
        year_number = day.year
        today_date = f"{day_number} {month_str} {year_number}"
        # print(today_date)
        # print("\n\n\n\n")
        # print(tasks)
        eisenhower_define = {
            "Urgent and Important": 1,
            "Not Urgent but Important": 2,
            "Urgent but Not Important": 3,
            "Neither Urgent nor Important": 4
        }
        
        urgent_important_tasks = [
            f'<li class="task-item"><span class="task-priority"></span>{task["title"]}<span class="task-time">Начало: {task["start_date"].split()[1][:5]}</span></li>'
            for task in tasks 
            if task["eisenhower_cat_id"] == eisenhower_define["Urgent and Important"]
        ]
        
        important_not_urgent_tasks = [
            f'<li class="task-item"><span class="task-priority"></span>{task["title"]}<span class="task-time">Начало: {task["start_date"].split()[1][:5]}</span></li>'
            for task in tasks 
            if task["eisenhower_cat_id"] == eisenhower_define["Not Urgent but Important"]
        ]
        urgent_not_important_tasks = [
            f'<li class="task-item"><span class="task-priority"></span>{task["title"]}<span class="task-time">Начало: {task["start_date"].split()[1][:5]}</span></li>'
            for task in tasks 
            if task["eisenhower_cat_id"] == eisenhower_define["Urgent but Not Important"]
        ]
        
        not_urgent_not_important_tasks = [
            f'<li class="task-item"><span class="task-priority"></span>{task["title"]}<span class="task-time">Начало: {task["start_date"].split()[1][:5]}</span></li>'
            for task in tasks 
            if task["eisenhower_cat_id"] == eisenhower_define["Neither Urgent nor Important"]
        ]
        # print(urgent_important_tasks + important_not_urgent_tasks + urgent_not_important_tasks + not_urgent_not_important_tasks)
        if not tasks:
            return {"error": "No tasks found for the given day."}
        
        if await render_priority_matrix(
            today_date,
            urgent_important_tasks,
            important_not_urgent_tasks,
            urgent_not_important_tasks,
            not_urgent_not_important_tasks
        ):
            return tasks
        else:
            return {"error": "Failed to render the priority matrix.", "tasks": tasks}
    except Exception as e:
        return {"error": repr(e)}