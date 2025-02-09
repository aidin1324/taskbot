import asyncio
import imgkit
config = imgkit.config(wkhtmltoimage=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe')
from aiogram import Bot
from aiogram.types.input_file import FSInputFile

from core.config import get_settings


settings = get_settings()
chat_id = settings.telegram_chat_id
bot = Bot(token=settings.telegram_api_key)
path = 'photo/output.jpg'


async def render_priority_matrix(
    date,
    urgent_important_tasks,
    important_not_urgent_tasks,
    urgent_not_important_tasks,
    not_urgent_not_important_tasks,
):
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            body {{
                min-height: 100vh;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 20px;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                color: #2d3436;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
                margin-bottom: 2rem;
            }}
            .header h1 {{
                font-size: 2.5rem;
                background: linear-gradient(45deg, #2d3436 0%, #636e72 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .current-date {{
                font-size: 1.2rem;
                color: #636e72;
            }}
            .matrix {{
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                gap: 25px;
            }}
            .quadrant {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 25px;
                transition: all 0.3s ease;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
                backdrop-filter: blur(4px);
                border: 1px solid rgba(255, 255, 255, 0.18);
                width: calc(50% - 12.5px);
                margin-bottom: 25px;
            }}
            .quadrant:hover {{
                transform: translateY(-5px);
                box-shadow: 0 12px 48px rgba(31, 38, 135, 0.15);
            }}
            .quadrant-header {{
                padding-bottom: 15px;
                border-bottom: 2px solid;
            }}
            .quadrant-header h2 {{
                font-size: 1.5rem;
            }}
            .task-list {{
                list-style: none;
                padding: 0;
            }}
            .task-item {{
                background: rgba(255, 255, 255, 0.8);
                padding: 15px;
                border-radius: 10px;
                border: 1px solid rgba(0, 0, 0, 0.05);
                transition: all 0.2s ease;
                margin-bottom: 10px;
            }}
            .task-item:hover {{
                background: rgba(255, 255, 255, 0.95);
                transform: translateX(5px);
            }}
            .task-priority {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 10px;
            }}
            .task-time {{
                background: rgba(0, 0, 0, 0.05);
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 0.9rem;
                color: #2d3436;
                text-align: right;
                float: right;
            }}
            .urgent-important {{
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 236, 236, 0.95));
            }}
            .urgent-important .quadrant-header {{
                border-color: #ff7675;
                color: #d63031;
            }}
            .urgent-important .task-priority {{
                background: #ff7675;
            }}
            .important-not-urgent {{
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(236, 255, 236, 0.95));
            }}
            .important-not-urgent .quadrant-header {{
                border-color: #00b894;
                color: #00897b;
            }}
            .important-not-urgent .task-priority {{
                background: #00b894;
            }}
            .urgent-not-important {{
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(236, 236, 255, 0.95));
            }}
            .urgent-not-important .quadrant-header {{
                border-color: #74b9ff;
                color: #0984e3;
            }}
            .urgent-not-important .task-priority {{
                background: #74b9ff;
            }}
            .not-urgent-not-important {{
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(245, 245, 245, 0.95));
            }}
            .not-urgent-not-important .quadrant-header {{
                border-color: #a4b0be;
                color: #636e72;
            }}
            .not-urgent-not-important .task-priority {{
                background: #a4b0be;
            }}
            @media (max-width: 768px) {{
                .quadrant {{
                    width: 100%;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header class="header">
                <h1>Матрица Эйзенхауэра</h1>
                <div class="current-date">{date}</div>
                <p>План задач на день</p>
            </header>
            <div class="matrix">
                <div class="quadrant urgent-important">
                    <div class="quadrant-header">
                        <h2>Срочно и важно</h2>
                        <p>Сделать немедленно</p>
                    </div>
                    <ul class="task-list">
                        {urgent_important_tasks}
                    </ul>
                </div>
                <div class="quadrant important-not-urgent">
                    <div class="quadrant-header">
                        <h2>Важно, но не срочно</h2>
                        <p>Запланировать время</p>
                    </div>
                    <ul class="task-list">
                        {important_not_urgent_tasks}
                    </ul>
                </div>
                <div class="quadrant urgent-not-important">
                    <div class="quadrant-header">
                        <h2>Срочно, но не важно</h2>
                        <p>Делегировать другим</p>
                    </div>
                    <ul class="task-list">
                        {urgent_not_important_tasks}
                    </ul>
                </div>
                <div class="quadrant not-urgent-not-important">
                    <div class="quadrant-header">
                        <h2>Не срочно и не важно</h2>
                        <p>Исключить или отложить</p>
                    </div>
                    <ul class="task-list">
                        {not_urgent_not_important_tasks}
                    </ul>
                </div>
            </div>
        </div>
    </body>
    </html>
    """.format(
        date=date,
        urgent_important_tasks="".join(urgent_important_tasks),
        important_not_urgent_tasks="".join(important_not_urgent_tasks),
        urgent_not_important_tasks="".join(urgent_not_important_tasks),
        not_urgent_not_important_tasks="".join(not_urgent_not_important_tasks)
    )
    # Выполнение блокирующего кода в отдельном потоке
    imgkit.from_string(html_code, path, config=config)
    
    # Отправка сгенерированного изображения в Telegram
   


    file_to_send = FSInputFile(path, filename="output.jpg")
    await bot.send_photo(chat_id=chat_id, photo=file_to_send)
    print("Priority matrix sent to Telegram.")
    return True
