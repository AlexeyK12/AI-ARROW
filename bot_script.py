import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from openai import Client

# получаем переменные окружения из файла .env (.gitignor)
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# клиент для взаимодействия с API
client = Client(api_key=OPENAI_API_KEY)

# приветствие при запуске/старте
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я твой ассистент для хакатона')

# доступные команд - /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '/study_topic <тема> - Изучение новых тем\n'
        '/generate_ideas <контекст> - Формирование идей\n'
        '/write_code <описание> - Писание кода\n'
        '/defend_project <вопрос> - Защита проекта\n'
        '/plan_work <описание> - Планирование работы команды\n'
        '/assign_tasks <описание> - Распределение задач'
    )

# информация по заданной теме 
async def study_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    topic = ' '.join(context.args)  
    response = await generate_response(f'Предоставь информацию по теме: {topic}')
    await update.message.reply_text(response)

# генерация идей на основе заданного контекста
async def generate_ideas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context_text = ' '.join(context.args)  
    response = await generate_response(f'Сгенерируй идеи на основе контекста: {context_text}')
    await update.message.reply_text(response)

# код на основе описания
async def write_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # описание из аргументов
    description = ' '.join(context.args)  
    response = await generate_response(f'Напиши код по следующему описанию: {description}')
    await update.message.reply_text(response)

# ответ на вопрос для защиты проекта
async def defend_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = ' '.join(context.args)  
    response = await generate_response(f'Ответь на вопрос для защиты проекта: {question}')
    await update.message.reply_text(response)

# план работы команды
async def plan_work(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # описание из аргументов
    description = ' '.join(context.args)  
    response = await generate_response(f'Создай план работы команды на основе описания: {description}')
    await update.message.reply_text(response)

# распределение задач среди членов команды
async def assign_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # описание из аргументов
    description = ' '.join(context.args)  
    response = await generate_response(f'Распредели задачи среди членов команды на основе описания: {description}')
    await update.message.reply_text(response)

# функция для запроса к API и получения ответа
async def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=5000  
        )
        return response.choices[0].message['content'].strip()  
    except Exception as e:
        return f'Ошибка API: {e}'  

# функция для запуска бота
async def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()  

    # обработчики команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('study_topic', study_topic))
    application.add_handler(CommandHandler('generate_ideas', generate_ideas))
    application.add_handler(CommandHandler('write_code', write_code))
    application.add_handler(CommandHandler('defend_project', defend_project))
    application.add_handler(CommandHandler('plan_work', plan_work))
    application.add_handler(CommandHandler('assign_tasks', assign_tasks))

    # инициализация и запуск приложения
    await application.initialize()  
    await application.start()  
    print('Бот запущен...')  
    await application.updater.start_polling()  
    while True:
        await asyncio.sleep(1)  

# проверяем, есть ли запущенный асинхронный цикл событий!!!
if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        print('Асинхронный цикл обработки событий УЖЕ запущен. Добавление сопрограммы в цикл обработки событий')
        
        # запускаем основной процесс бота
        task = loop.create_task(main())
    else:
        loop.run_until_complete(main())
