from typing import Dict, Any, Callable
from src.application.dtos.bot_dtos import BotResponse, HandleMessageDto
from src.domain.entities.user_session import UserSession
from src.domain.ports.user_session_port import ISessionRepository
from src.domain.constants import BotState, MainMenuOptions
from src.application.use_cases.get_service_by_folio import GetServiceByFolioUseCase

class HandleConversationUseCase:
    def __init__(
        self, 
        session_repo: ISessionRepository, 
        views: Dict[str, Any], 
        get_service_use_case: GetServiceByFolioUseCase
    ):
        self.repo = session_repo
        self.views = views
        self.get_service_use_case = get_service_use_case
        
        # Mapeo de Handlers por estado
        self.handlers: Dict[BotState, Callable[[HandleMessageDto, UserSession], BotResponse]] = {
            BotState.START: self._handle_start,
            BotState.MAIN_MENU: self._handle_main_menu,
            BotState.WAITING_FOR_FOLIO: self._handle_waiting_for_folio,
            #BotState.AI_ASSISTANT: self._handle_ai_mode,
        }

    def execute(self, input_dto: HandleMessageDto) -> BotResponse:
        # 1. Obtener estado actual (Dominio)
        session = self.repo.get_session(input_dto.user_id)
        
        # 2. Lógica global (Comandos de escape)
        clean_text = input_dto.message_text.strip().upper()
        if clean_text in ["/START", "VOLVER", "MENU", MainMenuOptions.VOLVER.value.upper()]:
            return self._transition_to(input_dto.user_id, BotState.MAIN_MENU)

        # 3. Delegar al handler correspondiente
        handler = self.handlers.get(session.state, self._handle_start)
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
        selection = dto.message_text.strip().lower()

        if selection == MainMenuOptions.CONSULTAR.value:
            return self._transition_to(dto.user_id, BotState.WAITING_FOR_FOLIO)
        
        if selection == MainMenuOptions.SOPORTE.value:
            # TODO: Implementar transición a soporte si existe el estado, 
            # por ahora retornamos la vista de contacto directamente o transicionamos
            return self.views['support'].support_contact_bot_message()

        if selection == MainMenuOptions.IA.value:
             return self.views['common'].ai_assistant_under_construction_message()

        
        # Si no entiende la opción, devuelve mensaje de error (sin cambiar estado)
        return self.views['common'].invalid_option_message()

    def _handle_waiting_for_folio(self, dto: HandleMessageDto, session: UserSession) -> BotResponse:
        # Delegamos la logica de negocio al caso de uso especifico
        response = self.get_service_use_case.execute(dto)
        
        if response.found and response.service_details:
             self._transition_to(dto.user_id, BotState.MAIN_MENU)
             
             # Convertimos el DTO de detalles a diccionario para pasarlo a la vista
             service_data = {
                 'folio': response.service_details.folio,
                 'service_type': response.service_details.service_reason,
                 'status': response.service_details.status,
                 'reception_date': response.service_details.reception_date,
                 'completion_date': response.service_details.completion_date,
                 'on_hold_reason': response.service_details.on_hold_reason,
                 'cancellation_reason': response.service_details.cancellation_reason,
                 'is_delivered': response.service_details.is_delivered,
                 'delivered_at': response.service_details.delivered_at
             }
             return self.views['consult'].show_service_details_by_folio(service_data)
        
        # Si no se encontró (o el formato era invalido), usamos la vista de error
        # asegurando que tenga botones de navegación
        return self.views['consult'].folio_not_found_message(dto.message_text)