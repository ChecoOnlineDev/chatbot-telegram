from src.models.constants import MainMenuOptions
from src.models.dtos.service_dtos import ButtonsDto


#funciones para las opciones que hay en el menu del bot
class NavigationMenuBotView:
    @staticmethod
    def main_menu_buttons() -> list:
        return [
            MainMenuOptions.CONSULTAR.value,
            MainMenuOptions.IA.value,
            MainMenuOptions.SOPORTE.value,
        ]
    
    @staticmethod
    def back_to_main_menu_button() -> list:
        return [MainMenuOptions.VOLER.value]
    

#Bienvenida y mensaje de error generico y opcion invalida
class CommonBotView:
    @staticmethod
    def welcome_message() -> ButtonsDto:
        return ButtonsDto(
            text = ("Hola! Soy el asistente virtual de XROM Systems, ¿En que puedo ayudarte hoy?."),
            buttons = NavigationMenuBotView.main_menu_buttons()
        )
        
    
    @staticmethod
    def generic_error_message() -> ButtonsDto:
        return ButtonsDto(
            text = ("Lo lamento, ha ocurrido un error inesperado. Por favor intenta nuevamente mas tarde o contacta a nuestro equipo de soporte!"),
            buttons = NavigationMenuBotView.back_to_main_menu_button()
        )
    
    @staticmethod
    def invalid_option_message() -> ButtonsDto:
        return ButtonsDto(
            text = ("Lo lamento, la opcion que has seleccionado no es valida. Por favor elige una de las opciones del menu."),
            buttons = NavigationMenuBotView.main_menu_buttons()
        )



#funciones para la opcion de consultar servicio por folio
class ConsultServiceBotView:
    @staticmethod
    def request_folio_message() -> ButtonsDto:
        return ButtonsDto(
            text = ("Perfecto, ingresa el folio del servicio que deseas consultar."),
            buttons = NavigationMenuBotView.back_to_main_menu_button()
        )
    
    @staticmethod
    def folio_not_found_message(folio: str) -> ButtonsDto:
        text = (
                f"Lo lamento, no pude encontrar ningun servicio asociado al folio: {folio}.\n"
                "Porfavor verifica que el folio sea correcto e intenta nuevamente o contacta a nuestro equipo de soporte."
            )
        return ButtonsDto(text=text, buttons=NavigationMenuBotView.back_to_main_menu_button())
        

    @staticmethod
    def show_service_details_by_folio(service_data: dict) -> ButtonsDto:
        text = (
            "¡Buenas noticias! Encontré la siguiente información:\n\n"
            f"• Folio: {service_data.get('folio','N/A')}\n"
            f"• Tipo: {service_data.get('service_type','N/A')}\n"
            f"• Estado: {service_data.get('status','N/A')}\n"
            f"• Fecha: {service_data.get('completion_date','N/A')}\n"
        )
        return ButtonsDto(text=text, buttons=NavigationMenuBotView.main_menu_buttons())

class SupportContactBotView:
    @staticmethod
    def support_contact_bot_message():
        text = (
            "Excelente, si tu problema requiere una atencion mas personalizada"
            "Contacta a los siguientes numeros, ya sea via whatsapp o por llamada, estamos a tus ordenes!"
        )
        return ButtonsDto(text=text, buttons=NavigationMenuBotView.back_to_main_menu_button())