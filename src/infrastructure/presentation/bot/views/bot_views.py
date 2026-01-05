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
        return [MainMenuOptions.VOLVER.value]


#Vistas y respuestas comunes del bot
"""Asegurarse de que la opcion parse_mode este en html o markdown en caso de usar"""
class CommonBotView:
    @staticmethod
    def welcome_message() -> BotResponse:
        return BotResponse(
            text = (
                "👋 <b>¡Hola, bienvenido a XROM Systems!</b> 🚀\n\n"
                "Soy tu <b>asistente virtual</b> inteligente. Estoy aquí para ayudarte a consultar el estado de tus servicios y brindarte soporte.\n\n"
                "👇 <b>Selecciona una opción del menú para comenzar:</b>"
            ),
            buttons = NavigationMenuBotView.main_menu_buttons()
        )
        
    @staticmethod
    def generic_error_message() -> BotResponse:
        return BotResponse(
            text = (
                "⚠️ <b>¡Ups! Algo salió mal.</b>\n\n"
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
                "🧐 <b>Opción no reconocida</b>\n\n"
                "Lo siento, no pude entender esa instrucción. Por favor, utiliza los "
                "<b>botones del menú</b> que aparecen aquí abajo para poder guiarte correctamente. 👇"
            ),
            buttons = NavigationMenuBotView.main_menu_buttons()
        )

    @staticmethod
    def ai_assistant_under_construction_message() -> BotResponse:
        return BotResponse(
            text = (
                "🧠 <b>Asistente IA en Construcción</b> 🚧\n\n"
                "¡Estamos trabajando arduamente para traerte lo mejor de la Inteligencia Artificial! 🤖✨\n"
                "Esta funcionalidad estará disponible muy pronto para ayudarte a resolver tus dudas al instante.\n\n"
                "Mientras tanto, por favor utiliza las otras opciones del menú. 👇"
            ),
            buttons = NavigationMenuBotView.back_to_main_menu_button()
        )


#funciones para la opcion de consultar servicio  en base al por folio
class ConsultServiceBotView:
    @staticmethod
    def request_folio_message() -> BotResponse:
        return BotResponse(
            text = (
                "🔍 <b>Consulta de Servicio</b>\n\n"
                "Por favor, <b>escribe el número de folio</b> que deseas consultar. "
                "Lo buscaré de inmediato en nuestra base de datos. ⚡"
            ),
            buttons = NavigationMenuBotView.back_to_main_menu_button()
        )
    
    @staticmethod
    def folio_not_found_message(folio: str) -> BotResponse:
        text = (
            f"❌ <b>Folio no encontrado</b>\n\n"
            f"Lo sentimos, no pudimos hallar ningún registro asociado al folio: <code>{folio}</code>. 🕵️‍♂️\n\n"
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
        
        # Status con iconos mejorados
        raw_status = service_data.get('status', 'Desconocido')
        status = raw_status.title() # Capitalizar por estetica
        
        # Fechas
        reception = service_data.get('reception_date', 'N/A')
        completion = service_data.get('completion_date', 'N/A')
        delivered_at = service_data.get('delivered_at', None)
        
        # Razones opcionales
        on_hold_reason = service_data.get('on_hold_reason')
        cancellation_reason = service_data.get('cancellation_reason')
        is_delivered = service_data.get('is_delivered', False)

        # Construcción del Mensaje
        text_lines = [
            f"�️ <b>Reporte de Servicio Técnico</b>",
            f"🆔 <b>Folio:</b> <code>{folio}</code>",
            "",
            "📊 <b>Estado Actual:</b>",
            f"� {status}",
        ]
        
        if on_hold_reason:
            text_lines.append(f"⚠️ <b>Razón de Espera:</b> {on_hold_reason}")
            
        if cancellation_reason:
            text_lines.append(f"⛔ <b>Motivo de Cancelación:</b> {cancellation_reason}")

        text_lines.extend([
            "",
            "📝 <b>Datos del Equipo:</b>",
            f"📌 <b>Servicio:</b> {s_type}",
            f"� <b>Recibido el:</b> {reception}",
        ])
        
        if completion:
            text_lines.append(f"✅ <b>Finalizado el:</b> {completion}")
            
        if is_delivered and delivered_at:
            text_lines.append(f"🚚 <b>Entregado el:</b> {delivered_at}")
        elif is_delivered:
             text_lines.append(f"🚚 <b>Entregado:</b> Sí")

        text_lines.extend([
            "",
            "¿Necesitas realizar otra operación?"
        ])
        
        return BotResponse(text="\n".join(text_lines), buttons=NavigationMenuBotView.main_menu_buttons())


#funciones en caso de que se seleccione la opcion de contactar a alguien de soporte
class SupportContactBotView:
    @staticmethod
    def support_contact_bot_message() -> BotResponse:
        phone_number = "+52 753 119 1766" 
        whatsapp_url = f"https://wa.me/{phone_number.replace(' ', '').replace('+', '')}"

        text = (
            "👨‍💻 <b>Centro de Soporte XROM Systems</b>\n\n"
            "Estamos listos para asesorarte con soluciones a tu medida. 🤝\n\n"
            "📞 <b>Vías de Contacto Directo:</b>\n"
            f"� <a href='{whatsapp_url}'><b>WhatsApp (Clic aquí)</b></a>\n"
            f"� <b>Llamada:</b> <code>{phone_number}</code>\n"
            "📧 <b>Email:</b> <code>soporte@xromsystems.com</code>\n\n"
            "🕒 <b>Horario de Atención:</b>\n"
            "• Lunes a Sábado: 9:00 AM - 7:00 PM\n"
            "• Domingos: Cerrado\n\n"
            "<i>Tu satisfacción es nuestra prioridad. 🚀</i>"
        )
        return BotResponse(
            text=text, 
            buttons=NavigationMenuBotView.back_to_main_menu_button()
        )
