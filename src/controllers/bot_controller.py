from src.models.folio_service import FolioValidatorService
from src.models.dtos.service_dtos import HandleMessageDto
from src.models.constants import BotState, MainMenuOptions
from src.models.dtos.service_dtos import ButtonsDto
from src.view.bot_view import CommonBotView, ConsultServiceBotView, NavigationMenuBotView, SupportContactBotView

class BotController:
    def __init__(
            self,
            folio_service: FolioValidatorService, 
            common_bot_view: CommonBotView, 
            navigation_menu_bot_view: NavigationMenuBotView,
            consult_service_bot_view: ConsultServiceBotView,
            support_contact_bot_view: SupportContactBotView
        ):
        self.folio_service = folio_service
        self.common_bot_view = common_bot_view
        self.navigation_menu_bot_view = navigation_menu_bot_view
        self.consult_service_bot_view = consult_service_bot_view
        self.support_contact_bot_view = support_contact_bot_view
        self.user_states = {}

    #maneja los mensajes del usuario y distribuye los estados segun la opcion seleccionada
    def handle_message(self, dto: HandleMessageDto) -> ButtonsDto:
        """Punto de entrada principal: decide a qué estado enviar el mensaje"""
        text = dto.message_text.strip() #eliminamos los espacios a los extremos
        state = self.user_states.get(dto.user_id, BotState.START) #si no se tiene un estado disponible
        #se asigna por defecto en start

        #status de la conversacion segun el id del usuario

        #text se supone que es el texto que envia el usuario
        if text == MainMenuOptions.VOLER.value: #si el usuario quiere volver al menu principal
            self.user_states[dto.user_id] = BotState.MAIN_MENU
            return self.common_bot_view.welcome_message()

        if state == BotState.START:
            return self._handle_start(dto) #si el usuario acaba de iniciar o manda start
        
        elif state == BotState.MAIN_MENU:
            return self._handle_main_menu(dto) #si el usuario esta en el menu principal
        
        elif state == BotState.WAITING_FOR_FOLIO:
            return self._handle_waiting_for_folio(dto) #si el bot esta esperando un folio
        
        # Estado por defecto: Si algo falla, lo mandamos al menú
        return self.common_bot_view.invalid_option_message()

    
    #handlers de estado
    
    def _handle_start(self, dto: HandleMessageDto) -> ButtonsDto:
        """El usuario acaba de llegar o envió /start"""
        self.user_states[dto.user_id] = BotState.MAIN_MENU #el status del bot en el menu
        return self.common_bot_view.welcome_message()

    def _handle_main_menu(self, dto: HandleMessageDto) -> ButtonsDto:
        """El usuario está eligiendo una opción del menú principal"""
        selection = dto.message_text.strip()

        if selection == MainMenuOptions.CONSULTAR.value:
            self.user_states[dto.user_id] = BotState.WAITING_FOR_FOLIO
            return self.consult_service_bot_view.request_folio_message()
        
        elif selection == MainMenuOptions.SOPORTE.value:
            self.user_states[dto.user_id] = BotState.SUPPORT_CONNECT
            return self.support_contact_bot_view.support_contact_bot_message()
            
            
        elif selection == MainMenuOptions.IA.value:
            self.user_states[dto.user_id] = BotState.AI_ASSISTANT
            # Aquí llamarías a la vista de IA (que puedes crear luego)
            return ButtonsDto("Has entrado al modo IA...", [])

        return self.common_bot_view.invalid_option_message()

    def _handle_waiting_for_folio(self, dto: HandleMessageDto) -> ButtonsDto:
        """El usuario está escribiendo un folio"""
        folio = dto.message_text.strip()
        
        # Usamos el servicio inyectado para buscar la data
        normalized_folio = self.folio_service.extract_and_validate_folio(folio)
        if not normalized_folio:
            return self.consult_service_bot_view.folio_not_found_message(folio) #cambiar por mensaje de folio invalido
        
        service_data = self.folio_service.consult_folio_in_database(normalized_folio)
        if service_data:
            # Si lo encuentra, mostramos detalles y volvemos al menú principal
            self.user_states[dto.user_id] = BotState.MAIN_MENU
            return self.consult_service_bot_view.show_service_details_by_folio(service_data)
        
        # Si no lo encuentra, permanecemos en el mismo estado para que reintente
        return self.consult_service_bot_view.folio_not_found_message(folio)
    



def simulate_bot():
    # 1. Instanciamos las dependencias
    # Si tus Views tienen métodos estáticos, puedes pasar la clase o una instancia
    service = FolioValidatorService() # O FolioValidatorService() si ya es funcional
    common_view = CommonBotView()
    nav_view = NavigationMenuBotView()
    consult_view = ConsultServiceBotView()
    support_contact = SupportContactBotView()

    # 2. Inyectamos las dependencias al controlador
    controller = BotController(
        folio_service=service,
        common_bot_view=common_view,
        navigation_menu_bot_view=nav_view,
        consult_service_bot_view=consult_view,
        support_contact_bot_view= support_contact
    )

    user_id = 555
    print("--- INICIANDO SIMULACIÓN (Escribe 'salir' para cerrar) ---")

    # Simulamos el primer mensaje (como si el usuario escribiera /start)
    current_dto = HandleMessageDto(user_id=user_id, user_name="Alex", message_text="hola")
    response = controller.handle_message(current_dto)

    while True:
        print(f"\n[BOT]: {response.text}")
        if response.buttons:
            print(f"[BOTONES]: | {' | '.join(response.buttons)} |")
        
        user_input = input(f"\n[YO]: ")
        
        if user_input.lower() == "salir":
            break
            
        # Creamos el DTO de entrada con lo que escribimos en consola
        input_dto = HandleMessageDto(
            user_id=user_id, 
            user_name="Alex", 
            message_text=user_input
        )
        
        # El controlador procesa y nos da un nuevo ButtonsDto
        response = controller.handle_message(input_dto)

if __name__ == "__main__":
    simulate_bot()