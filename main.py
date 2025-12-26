import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================
# 1) Configuración base
# =========================

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("xrom_bot")

TELEGRAM_TOKEN_API = os.getenv("TELEGRAM_TOKEN_API")
if not TELEGRAM_TOKEN_API:
    raise RuntimeError("Falta TELEGRAM_TOKEN_API en el entorno (.env).")

SUPPORT_CONTACT = os.getenv(
    "SUPPORT_CONTACT",
    "WhatsApp: +52 000 000 0000 | Email: soporte@xrom.systems",
)

# =========================
# 2) Estados del bot
# =========================

class BotState(str, Enum):
    ESPERANDO_INICIO = "ESPERANDO_INICIO"
    ESPERANDO_FOLIO = "ESPERANDO_FOLIO"
    SOPORTE_ACTIVO = "SOPORTE_ACTIVO"


STATE_KEY = "state"
LAST_FOLIO_KEY = "last_folio"


def get_state(context: ContextTypes.DEFAULT_TYPE) -> BotState:
    raw = context.user_data.get(STATE_KEY, BotState.ESPERANDO_INICIO.value)
    try:
        return BotState(raw)
    except ValueError:
        return BotState.ESPERANDO_INICIO


def set_state(context: ContextTypes.DEFAULT_TYPE, state: BotState) -> None:
    context.user_data[STATE_KEY] = state.value


def set_last_folio(context: ContextTypes.DEFAULT_TYPE, folio: str) -> None:
    context.user_data[LAST_FOLIO_KEY] = folio


def get_last_folio(context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    val = context.user_data.get(LAST_FOLIO_KEY)
    return str(val) if val else None


# =========================
# 3) Validación y extracción de folio
# =========================
# Formato: XROM- + alfanumérico (sin guiones extra)
# Ajusta {5,20} si tus folios son más cortos o más largos.
FOLIO_RE = re.compile(r"\bXROM-([A-Z0-9]{5,20})\b", re.IGNORECASE)


def extract_folio(text: str) -> Optional[str]:
    text = (text or "").strip()
    if not text:
        return None
    m = FOLIO_RE.search(text)
    if not m:
        return None
    return f"XROM-{m.group(1).upper()}"


# =========================
# 4) "Base de datos" en memoria (fake DB)
# =========================

@dataclass
class ServiceTicket:
    folio: str
    status: str
    summary: str
    updated_at: datetime
    history: List[str] = field(default_factory=list)


class InMemoryServiceRepository:
    """
    Repositorio en memoria: reemplazable por un repositorio real (Postgres, etc.).
    """

    def __init__(self) -> None:
        self._db: Dict[str, ServiceTicket] = {}

    def seed(self) -> None:
        now = datetime.utcnow()
        samples = [
            ServiceTicket(
                folio="XROM-A1B2C3D4E",
                status="EN DIAGNOSTICO",
                summary="Equipo recibido, revisión inicial en proceso.",
                updated_at=now,
                history=[
                    "RECIBIDO: Se registró el ingreso del equipo.",
                    "EN DIAGNOSTICO: Se inició revisión.",
                ],
            ),
            ServiceTicket(
                folio="XROM-9Z8Y7X6W5",
                status="EN REPARACION",
                summary="Reemplazo de componente autorizado, en taller.",
                updated_at=now,
                history=[
                    "RECIBIDO: Se registró el ingreso del equipo.",
                    "DIAGNOSTICO COMPLETO: Se detectó la falla.",
                    "EN REPARACION: Se inició reparación.",
                ],
            ),
            ServiceTicket(
                folio="XROM-HELLO12345",
                status="LISTO PARA ENTREGA",
                summary="Equipo terminado. Puedes pasar a recoger.",
                updated_at=now,
                history=[
                    "RECIBIDO: Se registró el ingreso del equipo.",
                    "EN DIAGNOSTICO: Se inició revisión.",
                    "EN REPARACION: Se realizó la reparación.",
                    "CALIDAD: Pruebas completadas.",
                    "LISTO PARA ENTREGA: Disponible para entrega.",
                ],
            ),
        ]
        for t in samples:
            self._db[t.folio] = t

    def find_by_folio(self, folio: str) -> Optional[ServiceTicket]:
        return self._db.get(folio)

    def upsert(self, ticket: ServiceTicket) -> None:
        self._db[ticket.folio] = ticket


repo = InMemoryServiceRepository()
repo.seed()


# =========================
# 5) UI (menús y acciones rápidas)
# =========================

CB_MENU_CONSULTAR = "MENU_CONSULTAR"
CB_MENU_SOPORTE = "MENU_SOPORTE"
CB_MENU_HOME = "MENU_HOME"

CB_FOLIO_OTRO = "FOLIO_OTRO"
CB_FOLIO_HIST = "FOLIO_HIST"


def kb_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Consultar Servicio", callback_data=CB_MENU_CONSULTAR)],
            [InlineKeyboardButton("Soporte Humano", callback_data=CB_MENU_SOPORTE)],
        ]
    )


def kb_back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Volver al menú", callback_data=CB_MENU_HOME)]]
    )


def kb_after_consult() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Consultar otro folio", callback_data=CB_FOLIO_OTRO)],
            [InlineKeyboardButton("Ver historial del último folio", callback_data=CB_FOLIO_HIST)],
            [InlineKeyboardButton("Volver al menú", callback_data=CB_MENU_HOME)],
        ]
    )


# =========================
# 6) Render del menú principal
# =========================

async def render_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    set_state(context, BotState.ESPERANDO_INICIO)

    text = (
        "Listo. Soy el Asistente Virtual de Xrom Systems.\n\n"
        "Elige una opción:"
    )

    if update.callback_query and update.callback_query.message:
        await update.callback_query.edit_message_text(text=text, reply_markup=kb_main_menu())
        return

    message = update.effective_message
    if message:
        await message.reply_text(text=text, reply_markup=kb_main_menu())


# =========================
# 7) Respuesta “fallback” (IA_FALLBACK lógico)
# =========================

async def fallback_answer(user_text: str) -> str:
    cleaned = (user_text or "").strip()
    if not cleaned:
        return "No recibí texto. Usa /menu para ver opciones."

    return (
        "No detecté un folio válido.\n\n"
        "Formato esperado:\n"
        "XROM- + alfanumérico (ej: XROM-A1B2C3D4E)\n\n"
        "Si quieres, toca 'Consultar Servicio' y pégalo tal cual."
    )


# =========================
# 8) Casos de uso (fachada hacia DB)
# =========================

def format_ticket(ticket: ServiceTicket) -> str:
    updated = ticket.updated_at.strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"Resultado para {ticket.folio}\n\n"
        f"Estado: {ticket.status}\n"
        f"Detalle: {ticket.summary}\n"
        f"Última actualización: {updated}"
    )


async def handle_folio_query(update: Update, context: ContextTypes.DEFAULT_TYPE, folio: str) -> None:
    message = update.effective_message
    if not message:
        return

    ticket = repo.find_by_folio(folio)
    set_last_folio(context, folio)

    if not ticket:
        await message.reply_text(
            text=(
                f"No encontré el folio: {folio}\n\n"
                "Revisa que esté bien escrito. Si te lo dieron impreso, cópialo tal cual.\n"
                "Si necesitas ayuda, entra a Soporte Humano."
            ),
            reply_markup=kb_main_menu(),
        )
        return

    await message.reply_text(
        text=format_ticket(ticket),
        reply_markup=kb_after_consult(),
    )


# =========================
# 9) Handlers: comandos / botones / texto
# =========================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await render_menu(update, context)


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await render_menu(update, context)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()

    data = query.data or ""

    if data == CB_MENU_HOME:
        await render_menu(update, context)
        return

    if data == CB_MENU_CONSULTAR:
        set_state(context, BotState.ESPERANDO_FOLIO)
        await query.edit_message_text(
            text=(
                "Perfecto. Mándame tu folio ahora.\n\n"
                "Ejemplo:\n"
                "XROM-A1B2C3D4E"
            ),
            reply_markup=kb_back_menu(),
        )
        return

    if data == CB_MENU_SOPORTE:
        set_state(context, BotState.SOPORTE_ACTIVO)
        await query.edit_message_text(
            text=(
                "Soporte humano activado.\n\n"
                f"Contacto: {SUPPORT_CONTACT}\n\n"
                "Para volver al menú: /menu o 'Volver al menú'."
            ),
            reply_markup=kb_back_menu(),
        )
        return

    if data == CB_FOLIO_OTRO:
        set_state(context, BotState.ESPERANDO_FOLIO)
        await query.edit_message_text(
            text=(
                "Va. Mándame el nuevo folio.\n\n"
                "Ejemplo:\n"
                "XROM-9Z8Y7X6W5"
            ),
            reply_markup=kb_back_menu(),
        )
        return

    if data == CB_FOLIO_HIST:
        last = get_last_folio(context)
        if not last:
            await query.edit_message_text(
                text="Aún no has consultado ningún folio. Toca 'Consultar Servicio'.",
                reply_markup=kb_main_menu(),
            )
            return

        ticket = repo.find_by_folio(last)
        if not ticket:
            await query.edit_message_text(
                text=(
                    f"No encontré el último folio ({last}) en la base en memoria.\n"
                    "Consulta otro folio o vuelve al menú."
                ),
                reply_markup=kb_main_menu(),
            )
            return

        hist = "\n".join([f"- {item}" for item in ticket.history]) or "- Sin historial"
        await query.edit_message_text(
            text=(
                f"Historial de {ticket.folio}\n\n"
                f"{hist}"
            ),
            reply_markup=kb_after_consult(),
        )
        return


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not message.text:
        return

    user_text = message.text
    state = get_state(context)

    # SOPORTE_ACTIVO: no interpretamos nada, solo guiamos a humano
    if state == BotState.SOPORTE_ACTIVO:
        await message.reply_text(
            text=(
                "Estás en soporte humano.\n"
                f"Contacto: {SUPPORT_CONTACT}\n\n"
                "Cuando quieras volver: /menu"
            )
        )
        return

    # Si está esperando folio, obligamos a que mande un XROM- válido
    if state == BotState.ESPERANDO_FOLIO:
        folio = extract_folio(user_text)
        if not folio:
            await message.reply_text(
                text=(
                    "Ese texto no trae un folio válido.\n\n"
                    "Formato esperado:\n"
                    "XROM- + alfanumérico (ej: XROM-A1B2C3D4E)\n\n"
                    "Intenta de nuevo pegándolo tal cual."
                ),
                reply_markup=kb_back_menu(),
            )
            return

        set_state(context, BotState.ESPERANDO_INICIO)
        await handle_folio_query(update, context, folio)
        return

    # En inicio: si manda un folio suelto, lo aceptamos (quick win)
    folio = extract_folio(user_text)
    if folio:
        await handle_folio_query(update, context, folio)
        return

    # IA_FALLBACK lógico
    answer = await fallback_answer(user_text)
    await message.reply_text(text=answer, reply_markup=kb_main_menu())


async def on_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    await message.reply_text("Comando no reconocido. Usa /menu para ver opciones.")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Error en handler", exc_info=context.error)


# =========================
# 10) Arranque (polling)
# =========================

def main() -> None:
    app = ApplicationBuilder().token(str(TELEGRAM_TOKEN_API)).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))

    app.add_handler(CallbackQueryHandler(on_button))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(filters.COMMAND, on_unknown_command))

    app.add_error_handler(on_error)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
