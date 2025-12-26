from telegram import Update
from dotenv import load_dotenv
import os
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_TOKEN_API")

async def saludo_inicial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return
    await message.reply_text(
        "Hola!, Soy el asistente virtual de XROM SYSTEMS, ¿En que puedo ayudarte?"
        )

#obtiene el token del bot de las variables de entorno
application = ApplicationBuilder().token(str(TELEGRAM_API_TOKEN)).build()

#los handler son los encargador de escuchar los mensajes que le llegan al bot y reaccionar a distintos tipos de eventos en esos mensajes
application.add_handler(
    CommandHandler("start", saludo_inicial)
)
application.run_polling(allowed_updates=Update.ALL_TYPES)