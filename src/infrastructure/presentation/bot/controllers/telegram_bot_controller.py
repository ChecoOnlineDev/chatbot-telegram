from src.application.dtos.bot_dtos import HandleMessageDto, BotResponse
from src.application.use_cases.handler_conversation import HandleConversationUseCase

class BotController:
    def __init__(
        self,
        conversation_handler: HandleConversationUseCase
    ):
        self.conversation_handler = conversation_handler

    async def handle_message(self, request: HandleMessageDto) -> BotResponse:
        """Maneja los mensajes entrantes y delega al caso de uso de conversación"""
        try:
            return self.conversation_handler.execute(request)
        except Exception as e:
            # En un entorno real, usaría un logger
            print(f"Error handling message: {str(e)}")
            # Retornar un mensaje de error genérico. 
            # Dado que el controlador es 'thin', idealmente el caso de uso maneja las excepciones,
            # pero mantenemos esto por seguridad.
            # Accedemos a la vista de error a través de una nueva instancia o estática si es necesario, 
            # pero aquí devolveremos un simple BotResponse de error.
            return BotResponse(text="Lo sentimos, ocurrió un error inesperado.")