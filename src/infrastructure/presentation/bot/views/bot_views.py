from src.application.dtos.bot_dtos import BotResponse
from src.domain.constants import MainMenuOptions

#Valores que hay en el menu de navegacion principal y helper de volver al menu
class NavigationMenuBotView:
    @staticmethod
    def main_menu_buttons() -> list:
        return [
            MainMenuOptions.CONSULTAR.value,
            MainMenuOptions.IA.value,
            MainMenuOptions.SOPORTE.value
        ]
        
    @staticmethod
    def back_to_main_menu_button()-> list:
        return [MainMenuOptions.VOLER.value]




#Vistas y respuestas comunes del bot
"""Asegurarse de que la opcion parse_mode este en html o markdown en caso de usar"""
class CommonBotView:
    @staticmethod
    def welcome_message() -> BotResponse:
        return BotResponse(
            text = (
                "¡Hola! 👋 Bienvenido a **XROM Systems** 🚀\n\n"
                "Soy tu asistente virtual y estoy aquí para ayudarte a agilizar tus procesos. "
                "¿En qué puedo apoyarte el día de hoy?"
            ),
            buttons = NavigationMenuBotView.main_menu_buttons()
        )
        
    @staticmethod
    def generic_error_message() -> BotResponse:
        return BotResponse(
            text = (
                "⚠️ **¡Ups! Algo salió mal.**\n\n"
                "Lo lamento, ha ocurrido un error inesperado en nuestro sistema. ⚙️ "
                "Por favor, intenta de nuevo en unos minutos o contacta directamente con nuestro "
                "equipo de soporte si el problema persiste. 🛠️"
            ),
            buttons = NavigationMenuBotView.back_to_main_menu_button()
        )
    
    @staticmethod
    def invalid_option_message() -> BotResponse:
        return BotResponse(
            text = (
                "🧐 **Opción no reconocida**\n\n"
                "Lo siento, no pude entender esa instrucción. Por favor, utiliza los "
                "**botones del menú** que aparecen aquí abajo para poder guiarte correctamente. 👇"
            ),
            buttons = NavigationMenuBotView.main_menu_buttons()
        )




#funciones para la opcion de consultar servicio  en base al por folio
class ConsultServiceBotView:
    @staticmethod
    def request_folio_message() -> BotResponse:
        return BotResponse(
            text = (
                "🔍 **Consulta de Servicio**\n\n"
                "Por favor, **escribe el número de folio** que deseas consultar. "
                "Lo buscaré de inmediato en nuestra base de datos. ⚡"
            ),
            buttons = NavigationMenuBotView.back_to_main_menu_button()
        )
    
    @staticmethod
    def folio_not_found_message(folio: str) -> BotResponse:
        text = (
            f"❌ **Folio no encontrado**\n\n"
            f"Lo sentimos, no pudimos hallar ningún registro asociado al folio: `{folio}`. 🕵️‍♂️\n\n"
            "Te recomendamos:\n"
            "1️⃣ Verificar que el folio sea correcto.\n"
            "2️⃣ Intentar escribirlo de nuevo.\n"
            "3️⃣ Contactar a soporte técnico si crees que es un error."
        )
        return BotResponse(text=text, buttons=NavigationMenuBotView.back_to_main_menu_button())

    @staticmethod
    def show_service_details_by_folio(service_data: dict) -> BotResponse:
        folio = service_data.get('folio', 'N/A')
        s_type = service_data.get('service_type', 'No especificado')
        status = service_data.get('status', 'En proceso').upper()
        date = service_data.get('completion_date', 'Pendiente')


        text = (
            "📋 **Detalles del Servicio Encontrado**\n\n"
            f"🆔 **Folio:** `{folio}`\n"
            f"🛠️ **Tipo de Servicio:** {s_type}\n"
            f"📊 **Estado Actual:** {status}\n"
            f"📅 **Fecha de Entrega/Cierre:** {date}\n\n"
            "¿Deseas realizar otra consulta o volver al inicio?"
        )
        return BotResponse(text=text, buttons=NavigationMenuBotView.main_menu_buttons())


#funciones en caso de que se seleccione la opcion de contactar a alguien de soporte
class SupportContactBotView:
    @staticmethod
    def support_contact_bot_message() -> BotResponse:
        # Número de ejemplo (puedes cambiarlo fácilmente después)
        phone_number = "+52 123 456 7890"
        whatsapp_url = f"https://wa.me/{phone_number.replace(' ', '').replace('+', '')}"

        text = (
            "👨‍💻 **Atención Personalizada XROM Systems**\n\n"
            "¡Entiendo! Si necesitas asistencia técnica detallada o una solución a medida, "
            "nuestro equipo de expertos está listo para escucharte. 🤝\n\n"
            "Puedes contactarnos por estos medios:\n\n"
            f"📱 **WhatsApp:** [Clic aquí para chatear]({whatsapp_url})\n"
            f"📞 **Llamada:** `{phone_number}`\n"
            "📧 **Correo:** `duvallier@xromsystems.com`\n\n"
            "⏰ **Horario de atención:**\n"
            "Lunes a Sabado | 9:00 AM - 7:00 PM\n\n"
            "Estamos a tus órdenes para resolver cualquier duda. 🚀"
        )
        return BotResponse(
            text=text, 
            buttons=NavigationMenuBotView.back_to_main_menu_button()
        )