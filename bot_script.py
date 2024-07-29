import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from openai import Client

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = Client(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я ваш ассистент для хакатона.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/study_topic <тема> - Изучение новых тем\n"
        "/generate_ideas <контекст> - Формирование идей\n"
        "/write_code <описание> - Писание кода\n"
        "/defend_project <вопрос> - Защита проекта\n"
        "/plan_work <описание> - Планирование работы команды\n"
        "/assign_tasks <описание> - Распределение задач"
    )

async def study_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    topic = ' '.join(context.args)
    response = await generate_response(f"Предоставь информацию по теме: {topic}")
    await update.message.reply_text(response)

async def generate_ideas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context_text = ' '.join(context.args)
    response = await generate_response(f"Сгенерируй идеи на основе контекста: {context_text}")
    await update.message.reply_text(response)

async def write_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    description = ' '.join(context.args)
    response = await generate_response(f"Напиши код по следующему описанию: {description}")
    await update.message.reply_text(response)

async def defend_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = ' '.join(context.args)
    response = await generate_response(f"Ответь на вопрос для защиты проекта: {question}")
    await update.message.reply_text(response)

async def plan_work(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    description = ' '.join(context.args)
    response = await generate_response(f"Создай план работы команды на основе следующего описания: {description}")
    await update.message.reply_text(response)

async def assign_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    description = ' '.join(context.args)
    response = await generate_response(f"Распредели задачи среди членов команды на основе следующего описания: {description}")
    await update.message.reply_text(response)

async def generate_response(prompt):
    try:
        # Запрос к OpenAI API с использованием нового метода
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=750
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Ошибка API OpenAI: {e}"

async def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("study_topic", study_topic))
    application.add_handler(CommandHandler("generate_ideas", generate_ideas))
    application.add_handler(CommandHandler("write_code", write_code))
    application.add_handler(CommandHandler("defend_project", defend_project))
    application.add_handler(CommandHandler("plan_work", plan_work))
    application.add_handler(CommandHandler("assign_tasks", assign_tasks))

    await application.initialize()
    await application.start()
    print("Bot is running...")
    await application.updater.start_polling()
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        print("Async event loop already running. Adding coroutine to the event loop.")
        task = loop.create_task(main())
    else:
        loop.run_until_complete(main())
