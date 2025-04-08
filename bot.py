from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8167071326:AAE9Rt6ZihRAq8upyHW6XUjMeI0pzZgEkoA"
ADMIN_ID = 173565167

question_user_map = {}

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_chat_id = update.effective_chat.id
    message_text = update.message.text

    if message_text.startswith('/'):
        await update.message.reply_text("Напишите анонимный вопрос")
        return


    sent_message = await context.bot.send_message(chat_id=ADMIN_ID, text=message_text)

    question_user_map[sent_message.message_id] = user_chat_id

    await update.message.reply_text("Вопрос отправлен")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.reply_to_message:
        orig_msg_id = update.message.reply_to_message.message_id
        if orig_msg_id in question_user_map:
            target_user_id = question_user_map[orig_msg_id]
            await context.bot.send_message(chat_id=target_user_id, text=update.message.text)
            await update.message.reply_text("Ответ отправлен пользователю.")
            del question_user_map[orig_msg_id]
        else:
            await update.message.reply_text("Не найден соответствующий вопрос пользователя.")
    else:
        await update.message.reply_text("Пожалуйста, ответьте реплаем на сообщение вопроса.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.User(user_id=ADMIN_ID), handle_user_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=ADMIN_ID), handle_admin_reply))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
