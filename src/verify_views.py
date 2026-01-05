import sys
import os

# Ensure src is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from src.infrastructure.presentation.bot.views.bot_views import ConsultServiceBotView, CommonBotView, SupportContactBotView
from src.application.dtos.bot_dtos import BotResponse

def print_response(title: str, response: BotResponse):
    print(f"\n--- {title} ---")
    print(response.text)
    print("-" * 30)

def verify_views():
    # 1. Welcome Message
    print_response("Welcome Message", CommonBotView.welcome_message())

    # 2. Support Contact
    print_response("Support Contact", SupportContactBotView.support_contact_bot_message())

    # 3. AI Assistant (Under Construction)
    print_response("AI Assistant", CommonBotView.ai_assistant_under_construction_message())

    # 4. Consult Service (In Progress)
    data_in_progress = {
        'folio': 'SV-12345',
        'service_type': 'Mantenimiento Preventivo',
        'status': 'En proceso',
        'reception_date': '01/01/2026',
        'completion_date': None,
        'is_delivered': False
    }
    print_response("Service In Progress", ConsultServiceBotView.show_service_details_by_folio(data_in_progress))

    # 4. Consult Service (Cancelled)
    data_cancelled = {
        'folio': 'SV-67890',
        'service_type': 'Reparación de Pantalla',
        'status': 'Cancelado',
        'reception_date': '02/01/2026',
        'completion_date': '03/01/2026',
        'cancellation_reason': 'Refacción no disponible',
        'is_delivered': False
    }
    print_response("Service Cancelled", ConsultServiceBotView.show_service_details_by_folio(data_cancelled))
    
    # 5. Consult Service (Completed & Delivered)
    data_delivered = {
        'folio': 'SV-55555',
        'service_type': 'Formateo',
        'status': 'Terminado',
        'reception_date': '20/12/2025',
        'completion_date': '21/12/2025',
        'is_delivered': True,
        'delivered_at': '22/12/2025'
    }
    print_response("Service Delivered", ConsultServiceBotView.show_service_details_by_folio(data_delivered))

if __name__ == "__main__":
    verify_views()
