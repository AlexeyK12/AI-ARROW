import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from openai import Client

# получаем переменные окружения из файла .env(.gitignor)
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# взаимодействие с API
client = Client(api_key=OPENAI_API_KEY)

# приветствие при запуске/старте
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Привет! Я твой ассистент для хакатона')
    await help_command(update, context)

# доступные команды - /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=
        '/study_topic <тема> - Изучение новых тем\n'
        '/generate_ideas <контекст> - Формирование идей\n'
        '/write_code <описание> - Писание кода\n'
        '/defend_project <вопрос> - Защита проекта\n'
        '/plan_work <описание> - Планирование работы команды\n'
        '/assign_tasks <описание> - Распределение задач'
    )

# обработчик команды при заходе в бот
async def initial_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton('ЗАПУСТИТЬ', callback_data='start_and_help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Добро пожаловать!!! Нажмите кнопку, чтобы начать', reply_markup=reply_markup)

# обработчик нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() 
    chat_id = query.message.chat_id  
    # отправляем сообщение в чат
    await context.bot.send_message(chat_id=chat_id, text='Привет! Я твой ассистент для хакатона')
    await help_command(update, context)

# информация по заданной теме 
async def study_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    topic = ' '.join(context.args)
    response = await generate_response(f'Предоставь информацию по теме: {topic}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

# генерация идей на основе заданного контекста
async def generate_ideas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context_text = ' '.join(context.args)
    response = await generate_response(f'Сгенерируй идеи на основе контекста: {context_text}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

# код на основе описания
async def write_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    description = ' '.join(context.args)
    response = await generate_response(f'Напиши код по следующему описанию: {description}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

# ответ на вопрос для защиты проекта
async def defend_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = ' '.join(context.args)
    response = await generate_response(f'Ответь на вопрос для защиты проекта: {question}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

# план работы команды
async def plan_work(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    description = ' '.join(context.args)
    response = await generate_response(f'Создай план работы команды на основе описания: {description}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

# распределение задач среди членов команды
async def assign_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    description = ' '.join(context.args)
    response = await generate_response(f'Распредели задачи среди членов команды на основе описания: {description}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

# функция для запроса к API
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
    application.add_handler(CommandHandler('start', initial_start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('study_topic', study_topic))
    application.add_handler(CommandHandler('generate_ideas', generate_ideas))
    application.add_handler(CommandHandler('write_code', write_code))
    application.add_handler(CommandHandler('defend_project', defend_project))
    application.add_handler(CommandHandler('plan_work', plan_work))
    application.add_handler(CommandHandler('assign_tasks', assign_tasks))
    application.add_handler(CallbackQueryHandler(button))  

    # инициализация и запуск приложения
    await application.initialize()
    await application.start()
    print('Бот запущен...')
    await application.updater.start_polling()
    while True:
        await asyncio.sleep(1)

# проверяем, есть ли запущенный асинхронный цикл событий
if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        print('Асинхронный цикл обработки событий УЖЕ запущен. Добавление сопрограммы в цикл обработки событий')
        
        # Запускаем основной процесс бота
        task = loop.create_task(main())
    else:
        loop.run_until_complete(main())
