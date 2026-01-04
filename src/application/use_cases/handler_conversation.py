from typing import Dict, Any, Callable

from application.dtos.bot_dtos import BotResponse, HandleMessageDto
from domain.entities.user_session import UserSession
from domain.ports.user_session_port import ISessionRepository
from src.domain.constants import BotState, MainMenuOptions

class HandleConversationUseCase:
    def __init__(
        self, 
        session_repo: ISessionRepository, 
        views: Dict[str, Any], 
        services: Dict[str, Any]
    ):
        self.repo = session_repo
        self.views = views
        self.services = services

    def execute(self, input_dto: HandleMessageDto) -> BotResponse:
        # 1. Obtener estado actual (Dominio)
        session = self.repo.get_session(input_dto.user_id)
        
        # 2. Lógica global (Comandos de escape)
        clean_text = input_dto.message_text.strip().upper()
        if clean_text in ["/START", "VOLVER", "MENU"]:
            return self._transition_to(input_dto.user_id, BotState.MAIN_MENU)

        # 3. Mapeo de Handlers por estado
        handlers: Dict[BotState, Callable[[HandleMessageDto, UserSession], BotResponse]] = {
            BotState.START: self._handle_start,
            BotState.MAIN_MENU: self._handle_main_menu,
            BotState.WAITING_FOR_FOLIO: self._handle_waiting_for_folio,
            #BotState.AI_ASSISTANT: self._handle_ai_mode,
        }

        handler = handlers.get(session.state, self._handle_start)
        return handler(input_dto, session)

    # --- Handlers de Transición ---

    def _transition_to(self, user_id: int, state: BotState, metadata: dict = None) -> BotResponse: #type: ignore
        """Actualiza el estado en el repositorio y retorna la vista inicial"""
        new_session = UserSession(state=state, metadata=metadata or {})
        self.repo.save_session(user_id, new_session)

        # Retornar DTO de respuesta basado en las vistas
        if state == BotState.MAIN_MENU:
            return self.views['common'].welcome_message()
        if state == BotState.WAITING_FOR_FOLIO:
            return self.views['consult'].request_folio_message()
        
        return self.views['common'].welcome_message()

    # --- Lógica de los Handlers ---

    def _handle_start(self, dto: HandleMessageDto, session: UserSession) -> BotResponse:
        return self._transition_to(dto.user_id, BotState.MAIN_MENU)

    def _handle_main_menu(self, dto: HandleMessageDto, session: UserSession) -> BotResponse:
        selection = dto.message_text.strip().upper()

        if selection == MainMenuOptions.CONSULTAR.value:
            return self._transition_to(dto.user_id, BotState.WAITING_FOR_FOLIO)
        
        # Si no entiende la opción, devuelve mensaje de error (sin cambiar estado)
        return self.views['common'].invalid_option_message()

    def _handle_waiting_for_folio(self, dto: HandleMessageDto, session: UserSession) -> BotResponse:
        folio_input = dto.message_text.strip()
        
        # Uso de servicios de dominio/infraestructura inyectados
        normalized = self.services['folio'].validate_format(folio_input)
        if not normalized:
            return self.views['consult'].invalid_format_message()

        result = self.services['folio'].search(normalized)
        if result:
            # Si lo encuentra, muestra info y resetea al menú
            view_data = self.views['consult'].show_details(result)
            self._transition_to(dto.user_id, BotState.MAIN_MENU)
            return view_data
        
        return self.views['consult'].not_found_message(folio_input)

    #def _handle_ai_mode(self, dto: HandleMessageDto, session: UserSession) -> BotResponse:
        # Aquí iría la integración con LangChain o tu servicio de IA
        return BotResponse("Modo IA activado. (En desarrollo)")