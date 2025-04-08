from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Укажите токен вашего бота Telegram (полученный от @BotFather)
TOKEN = "8167071326:AAE9Rt6ZihRAq8upyHW6XUjMeI0pzZgEkoA"

# Укажите ID администратора (целое число Telegram ID)
ADMIN_ID = 173565167

# Внутренний словарь для хранения соответствия "ID сообщения, отправленного админу -> ID чата пользователя"
question_user_map = {}

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает входящее сообщение от пользователя (анонимный вопрос).
    Если сообщение начинается с '/', выводит приглашение задать вопрос.
    Иначе пересылает текст вопроса админу без указания информации о пользователе.
    """
    user_chat_id = update.effective_chat.id
    message_text = update.message.text

    # Если сообщение является командой, выводим приглашение и не пересылаем админу
    if message_text.startswith('/'):
        await update.message.reply_text("Напишите анонимный вопрос")
        return

    # Отправляем вопрос админу (анонимно)
    sent_message = await context.bot.send_message(chat_id=ADMIN_ID, text=message_text)

    # Сохраняем соответствие: ID сообщения, отправленного админу -> ID чата пользователя
    question_user_map[sent_message.message_id] = user_chat_id

    # Подтверждаем пользователю, что вопрос отправлен
    await update.message.reply_text("Вопрос отправлен")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает ответ администратора на пересланный ботом вопрос.
    Если админ отвечает реплаем на сообщение, бот отправляет его ответ анонимно пользователю,
    то есть от имени бота. Если сообщение не является реплаем, администратору отправляется уведомление.
    """
    # Проверяем, что сообщение является ответом на пересланное сообщение
    if update.message.reply_to_message:
        orig_msg_id = update.message.reply_to_message.message_id
        if orig_msg_id in question_user_map:
            target_user_id = question_user_map[orig_msg_id]
            # Отправляем ответ пользователю от имени бота
            await context.bot.send_message(chat_id=target_user_id, text=update.message.text)
            # Отправляем админу подтверждение, что ответ доставлен
            await update.message.reply_text("Ответ отправлен пользователю.")
            # Удаляем запись, чтобы избежать повторной отправки
            del question_user_map[orig_msg_id]
        else:
            # Если соответствующая запись не найдена
            await update.message.reply_text("Не найден соответствующий вопрос пользователя.")
    else:
        await update.message.reply_text("Пожалуйста, ответьте реплаем на сообщение вопроса.")

def main():
    """
    Инициализирует бота и запускает опрос Telegram API с использованием run_polling().
    """
    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчик для сообщений от пользователей (не от администратора)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.User(user_id=ADMIN_ID), handle_user_message))
    
    # Регистрируем обработчик для сообщений от администратора
    app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=ADMIN_ID), handle_admin_reply))

    print("Bot started...")
    # Запускаем бота (блокирующий вызов)
    app.run_polling()

if __name__ == "__main__":
    main()
