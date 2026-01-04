from pydantic import BaseModel


#estadarizando las respuestas del bot
class BotResponse(BaseModel):
    text: str
    buttons: list[str] = []

#Modelo de mensajes estandar que recibira el bot (lo que ocuparemos)
class HandleMessageDto(BaseModel):
    user_id: int
    message_text: str
    user_name: str