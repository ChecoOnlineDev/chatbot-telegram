import logging
import os
import sys

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from src.infrastructure.container import Container
from src.infrastructure.presentation.bot.handlers import telegram_handlers

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

def main() -> None:
    # 1. Cargar variables de entorno
    load_dotenv()
    
    # Validar variables críticas
    token = os.getenv("TELEGRAM_TOKEN_API")
    if not token:
        logger.critical("No se encontró TELEGRAM_TOKEN_API. Verifica tu archivo .env")
        sys.exit(1)

    # 2. Inicializar Contenedor de Dependencias
    container = Container()
    
    # Imprimir estado de wiring para depuración
    print("Iniciando contenedor y wiring...")
    try:
        container.init_resources()
        # El wiring se hace automáticamente por la configuración en container.py al importar los módulos
        # pero también podemos forzar validación si quisiéramos.
    except Exception as e:
        logger.critical(f"Error inicializando recursos del contenedor: {e}", exc_info=True)
        sys.exit(1)

    # 3. Construir la Aplicación de Telegram
    from telegram.constants import ParseMode
    from telegram.ext import Defaults

    defaults = Defaults(parse_mode=ParseMode.HTML)
    app = ApplicationBuilder().token(token).defaults(defaults).build()

    # 4. Registrar Handlers
    # Usamos las funciones del módulo telegram_handlers que ya tienen @inject
    
    # Comandos
    app.add_handler(CommandHandler("start", telegram_handlers.start_command))
    
    # Botones (Callback Queries)
    app.add_handler(CallbackQueryHandler(telegram_handlers.handle_telegram_message))

    # Mensajes de texto (excluyendo comandos)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handlers.handle_telegram_message))

    # 5. Ejecutar
    logger.info("Bot iniciado con Clean Architecture. Conectando a infraestructura...")
    app.run_polling()

if __name__ == "__main__":
    main()
