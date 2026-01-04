from dependency_injector import containers, providers
from src.infrastructure.database.configuration import get_db, SessionLocal
from src.infrastructure.adapters.technical_service_adapter import SQLAlchemyTechnicalServiceAdapter
from src.infrastructure.redis.redis_configuration import get_redis_client
from src.infrastructure.adapters.redis_session_adapter import RedisSessionRepository
from src.application.use_cases.get_service_by_folio import GetServiceByFolioUseCase
from src.application.use_cases.handler_conversation import HandleConversationUseCase
from src.infrastructure.presentation.bot.controllers.telegram_bot_controller import BotController
from src.infrastructure.presentation.bot.views.bot_views import CommonBotView, ConsultServiceBotView, SupportContactBotView

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[
        "src.application.use_cases.get_service_by_folio",
        "src.infrastructure.presentation.bot.handlers.telegram_handlers"
    ])

    db_session = providers.Resource(get_db)

    # Adapters
    technical_service_adapter = providers.Factory(
        SQLAlchemyTechnicalServiceAdapter,
        session=db_session
    )

    redis_client = providers.Resource(get_redis_client)

    session_repository = providers.Factory(
        RedisSessionRepository,
        client=redis_client
    )

    get_service_use_case = providers.Factory(
        GetServiceByFolioUseCase,
        service_port=technical_service_adapter
    )

    # Views
    views_dict = providers.Object({
        'common': CommonBotView(),
        'consult': ConsultServiceBotView(),
        'support': SupportContactBotView()
    })

    # Conversation Handler
    conversation_handler = providers.Factory(
        HandleConversationUseCase,
        session_repo=session_repository,
        views=views_dict,
        get_service_use_case=get_service_use_case
    )

    # Bot Controller
    bot_controller = providers.Factory(
        BotController,
        conversation_handler=conversation_handler
    )

