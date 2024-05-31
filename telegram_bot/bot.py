import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from models import Base, engine, SessionLocal
from datetime import datetime, timedelta
from models.appointment import Appointment
from models.user import User
from models.massage import Massage
from telegram_bot.keyboards import main_menu, massage_menu, admin_menu

from telegram_bot.models.media import Media

API_TOKEN = '5826313815:AAHtpbJedfAFA0CsYDnYS-x3QfUFtLomPBI'
ADMIN_ID = 1298160179

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
scheduler = AsyncIOScheduler()

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Добро пожаловать! Используйте /register для регистрации. И эти еще поклацай /menu /admin")
    await message.delete()
    logger.info(f"User {message.from_user.id} started the bot.")


@dp.message_handler(commands=['register'])
async def register_user(message: types.Message):
    session = SessionLocal()
    user = User.register(session, message.from_user.id, message.from_user.username)
    if user:
        await message.reply("Вы успешно зарегистрированы!")
        await message.delete()
        logger.info(f"User {message.from_user.id} registered successfully.")
    else:
        await message.reply("Произошла ошибка при регистрации.")
        logger.error(f"Error registering user {message.from_user.id}.")


@dp.message_handler(commands=['menu'])
async def show_menu(message: types.Message):
    await message.reply("Выберите действие:", reply_markup=main_menu)


@dp.message_handler(commands=['massages'])
async def list_massages(message: types.Message):
    session = SessionLocal()
    massages = session.query(Massage).all()
    response = "\n".join([f"{m.name}: {m.price} рублей" for m in massages])
    await message.reply(response)
    logger.info(f"User {message.from_user.id} requested massage list.")


@dp.message_handler(commands=['book'])
async def book_appointment(message: types.Message):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user or not user.is_registered:
        await message.reply("Пожалуйста, зарегистрируйтесь сначала с помощью команды /register.")
        return

    # Логика для выбора времени и даты (примерно)
    now = datetime.now()
    available_time = now + timedelta(days=1)
    appointment = Appointment(user_id=user.id, massage_id=1, appointment_time=available_time)
    session.add(appointment)
    session.commit()

    await message.reply(f"Вы записаны на {available_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"User {message.from_user.id} booked an appointment for {available_time}.")


@dp.message_handler(commands=['gallery'])
async def show_gallery(message: types.Message):
    session = SessionLocal()
    media_files = session.query(Media).all()
    for media in media_files:
        await message.reply_photo(media.url,
                                  caption=media.description) if media.type == 'photo' else await message.reply_video(
            media.url, caption=media.description)
        logger.info(f"User {message.from_user.id} requested gallery.")


@dp.message_handler(lambda message: message.text == 'Виды массажа')
async def list_massages(message: types.Message):
    await message.reply("Выберите вид массажа:", reply_markup=massage_menu)


@dp.callback_query_handler(lambda c: c.data.startswith('massage_'))
async def process_massage_selection(callback_query: types.CallbackQuery):
    massage_id = callback_query.data.split('_')[1]
    # Логика для обработки выбора массажа
    await bot.send_message(callback_query.from_user.id, f"Вы выбрали массаж {massage_id}")


@dp.message_handler(commands=['feedback'])
async def ask_feedback(message: types.Message):
    await message.reply("Пожалуйста, оставьте ваш отзыв или вопрос, и мы свяжемся с вами.")


# @dp.message_handler()
# async def handle_feedback(message: types.Message):
#     if message.text:
#         # Логика для сохранения отзыва или вопроса в базу данных
#         await message.reply("Спасибо за ваш отзыв! Мы скоро с вами свяжемся.")
#         logger.info(f"Feedback from user {message.from_user.id}: {message.text}")


"""ADMINKA"""


@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет доступа к этой команде.")
        return
    await message.reply("Добро пожаловать в админ панель", reply_markup=admin_menu)
    logger.info(f"Admin {message.from_user.id} accessed admin panel.")


@dp.message_handler(lambda message: message.text == 'Добавить массаж')
async def add_massage(message: types.Message):
    await message.reply("Пожалуйста, отправьте название и цену массажа в формате 'Название:Цена'")
    logger.info(f"Admin {message.from_user.id} requested to add a massage.")


@dp.message_handler(lambda message: ':' in message.text)
async def save_massage(message: types.Message):
    name, price = message.text.split(':')
    session = SessionLocal()
    massage = Massage(name=name, price=int(price))
    session.add(massage)
    session.commit()
    await message.reply(f"Массаж {name} добавлен с ценой {price} рублей.")
    logger.info(f"Admin {message.from_user.id} added massage {name} with price {price}.")


@scheduler.scheduled_job('interval', minutes=1)
async def notify_upcoming_appointments():
    session = SessionLocal()
    now = datetime.now()
    one_day_later = now + timedelta(days=1)
    appointments = session.query(Appointment).filter(Appointment.appointment_time.between(now, one_day_later)).all()
    for appointment in appointments:
        user = session.query(User).filter_by(id=appointment.user_id).first()
        await bot.send_message(user.telegram_id, f"Напоминание: у вас запись на массаж {appointment.appointment_time}")
        logger.info(f"Reminder sent to user {user.telegram_id} for appointment at {appointment.appointment_time}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
