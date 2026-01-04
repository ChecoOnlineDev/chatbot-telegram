from src.application.dtos.bot_dtos import HandleMessageDto, BotResponse
from src.domain.constants import BotState, MainMenuOptions
from src.domain.entities.user_session import UserSession
from src.domain.ports.user_session_port import ISessionRepository
from src.infrastructure.presentation.bot.views.bot_views import (
    CommonBotView,
    ConsultServiceBotView,
    NavigationMenuBotView,
    SupportContactBotView
)

class BotController:
    def __init__(
        self,
        session_repository: ISessionRepository,
        folio_service,
        common_view: CommonBotView | None = None,
        consult_view: ConsultServiceBotView | None = None,
        support_view: SupportContactBotView  | None = None
    ):
        self.session_repo = session_repository
        self.folio_service = folio_service
        
        # Inicializar vistas con valores por defecto si no se proporcionan
        self.views = {
            'common': common_view or CommonBotView(),
            'consult': consult_view or ConsultServiceBotView(),
            'support': support_view or SupportContactBotView()
        }
        
        # Mapeo de comandos a sus handlers
        self.command_handlers = {
            'start': self._handle_start,
            'menu': self._handle_menu,
            'consult': self._handle_consult,
            'support': self._handle_support,
            'help': self._handle_help
        }

    async def handle_message(self, request: HandleMessageDto) -> BotResponse:
        """Maneja los mensajes entrantes y delega a los manejadores correspondientes"""
        try:
            # Obtener o crear sesión del usuario en redis para memoria de sesiones
            session = await self._get_or_create_session(request.user_id)
            
            # Limpiar y normalizar el texto del mensaje
            clean_text = request.message_text.strip().lower()
            
            # Manejar comandos globales
            command = self._identify_command(clean_text)
            if command:
                return await command(request, session)
                
            # Manejar según el estado actual
            if session.state == BotState.WAITING_FOR_FOLIO:
                return await self._handle_folio_input(clean_text, request.user_id, session)
                
            # Si no se reconoce el comando
            return self.views['common'].invalid_option_message()
            
        except Exception as e:
            # Registrar el error (deberías implementar un logger)
            print(f"Error handling message: {str(e)}")
            return self.views['common'].generic_error_message()

    # --- Helpers de manejo de sesión ---
    
    async def _get_or_create_session(self, user_id: int) -> UserSession:
        """Obtiene o crea una sesión para el usuario"""
        session = await self.session_repo.get_session(user_id)
        if not session:
            session = UserSession(
                user_id=user_id,
                state=BotState.START
            )
            await self.session_repo.save_session(user_id, session)
        return session

    async def _update_session_state(
        self, 
        user_id: int, 
        session: UserSession, 
        new_state: BotState,
        **extra_data
    ) -> None:
        """Actualiza el estado de la sesión"""
        session.state = new_state
        session.metadata.update(extra_data)
        await self.session_repo.save_session(user_id, session)

    # --- Identificación de comandos ---
    
    def _identify_command(self, text: str):
        """Identifica si el texto es un comando conocido"""
        command_map = {
            'start': ['/start', 'inicio', 'comenzar'],
            'menu': ['menu', 'menú', 'volver', 'inicio'],
            'consult': ['consultar', 'folio', 'estado'],
            'support': ['soporte', 'ayuda', 'contacto'],
            'help': ['ayuda', 'comandos']
        }
        
        for command, triggers in command_map.items():
            if text in triggers:
                return self.command_handlers.get(command)
        return None

    # --- Manejadores de comandos ---
    
    async def _handle_start(self, request: HandleMessageDto, session: UserSession) -> BotResponse:
        """Maneja el comando de inicio"""
        await self._update_session_state(
            request.user_id, 
            session, 
            BotState.MAIN_MENU
        )
        return self.views['common'].welcome_message()

    async def _handle_menu(self, request: HandleMessageDto, session: UserSession) -> BotResponse:
        """Maneja la navegación al menú principal"""
        await self._update_session_state(
            request.user_id, 
            session, 
            BotState.MAIN_MENU
        )
        # Usamos el mensaje de bienvenida como menú principal
        return self.views['common'].welcome_message()

    async def _handle_consult(self, request: HandleMessageDto, session: UserSession) -> BotResponse:
        """Inicia el flujo de consulta de folio"""
        await self._update_session_state(
            request.user_id, 
            session, 
            BotState.WAITING_FOR_FOLIO
        )
        return self.views['consult'].request_folio_message()

    async def _handle_support(self, request: HandleMessageDto, session: UserSession) -> BotResponse:
        """Muestra la información de soporte"""
        return self.views['support'].support_contact_bot_message()

    async def _handle_help(self, request: HandleMessageDto, session: UserSession) -> BotResponse:
        """Muestra la ayuda"""
        return BotResponse(
            text=(
                "🤖 **Ayuda y Comandos**\n\n"
                "Puedes usar los siguientes comandos:\n\n"
                "• /start - Iniciar el bot\n"
                "• Menú - Mostrar menú principal\n"
                "• Consultar - Ver estado de un servicio\n"
                "• Soporte - Contactar a soporte\n\n"
                "También puedes usar los botones del menú para navegar."
            ),
            buttons=NavigationMenuBotView.main_menu_buttons()
        )

    # --- Manejadores de estados ---
    
    async def _handle_folio_input(self, folio: str, user_id: int, session: UserSession) -> BotResponse:
        """Maneja la entrada de folio del usuario"""
        # Validar formato del folio
        if not self.folio_service.validate_folio_format(folio):
            return self.views['consult'].folio_not_found_message(folio)
        
        try:
            # Buscar el servicio
            service = await self.folio_service.get_service_by_folio(folio)
            if not service:
                return self.views['consult'].folio_not_found_message(folio)
            
            # Volver al menú principal
            await self._update_session_state(
                user_id, 
                session, 
                BotState.MAIN_MENU
            )
            
            # Mostrar detalles del servicio
            return self.views['consult'].show_service_details_by_folio(service)
            
        except Exception as e:
            print(f"Error al buscar folio: {str(e)}")
            return self.views['common'].generic_error_message()