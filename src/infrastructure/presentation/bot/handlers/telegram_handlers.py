import logging
from telegram import Update
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide

from src.infrastructure.container import Container
from src.application.use_cases.handler_conversation import HandleConversationUseCase
from src.application.dtos.bot_dtos import HandleMessageDto

logger = logging.getLogger(__name__)

@inject
async def handle_telegram_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    conversation_handler: HandleConversationUseCase = Provide[Container.conversation_handler]
) -> None:
    """
    Handler genérico de Telegram.
    Convierte el objeto Update de la librería externa a un DTO de nuestra aplicación.
    """
    if not update.effective_message or not update.effective_user:
        return

    user_text = update.effective_message.text or ""
    # Si es un botón (callback_query), el texto viene del data, si es mensaje normal, del text
    if update.callback_query:
        await update.callback_query.answer()
        user_text = update.callback_query.data or ""
        # user_id ya está en effective_user

    # Construimos el DTO de entrada
    input_dto = HandleMessageDto(
        user_id=update.effective_user.id,
        message_text=user_text,
        user_name=update.effective_user.username or "Unknown",
        first_name=update.effective_user.first_name
    )

    try:
        # Delegamos al Caso de Uso (Adaptador -> Aplicación)
        response_dto = conversation_handler.execute(input_dto)

        # Renderizamos la respuesta (Adaptadores hacia afuera)
        # Aquí convertimos nuestro BotResponse agnóstico a objetos de Telegram
        
        # Mapeo de botones (BotResponse -> Telegram InlineKeyboardMarkup)
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        reply_markup = None
        if response_dto.buttons:
            # Creamos una lista de listas (filas) de botones Inline
            # Por defecto ponemos 1 botón por fila para que se vea bien en móviles
            keyboard = []
            for btn_text in response_dto.buttons:
                # Usamos el texto del botón como callback_data
                # OJO: Telegram limita callback_data a 64 bytes.
                keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=btn_text)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
             # Si venimos de un clic, editamos el mensaje anterior para dar efecto de "navegación"
             try:
                await update.callback_query.edit_message_text(
                    text=response_dto.text, 
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
             except Exception as e:
                 # Si el mensaje es idéntico (Message is not modified), Telegram lanza error. Lo ignoramos.
                 if "Message is not modified" in str(e):
                     logger.warning(f"Intento de editar mensaje con el mismo contenido: {e}")
                 else:
                     raise e
        else:
            # Si es mensaje nuevo, respondemos normal
            await update.effective_message.reply_text(
                text=response_dto.text, 
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        await update.effective_message.reply_text("Lo siento, ocurrió un error interno.")

@inject
async def start_command(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE,
    conversation_handler: HandleConversationUseCase = Provide[Container.conversation_handler]
) -> None:
    """Comando /start explícito"""
    # Reutilizamos la lógica genérica simulando el texto /START
    if not update.effective_message or not update.effective_user:
        return

    input_dto = HandleMessageDto(
        user_id=update.effective_user.id,
        message_text="/START",
        user_name=update.effective_user.username or "Unknown",
        first_name=update.effective_user.first_name
    )
    
    # Delegamos al caso de uso directamente
    response = conversation_handler.execute(input_dto)
    
    # Renderizamos botones si existen (mismo mapping que arriba)
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    reply_markup = None
    if response.buttons:
        keyboard = [[InlineKeyboardButton(text=btn, callback_data=btn)] for btn in response.buttons]
        reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        text=response.text, 
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
