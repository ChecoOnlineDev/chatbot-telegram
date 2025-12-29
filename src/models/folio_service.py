import re

DASH_TRANSLATION_TABLE = str.maketrans({
    "–": "-",  # en dash
    "—": "-",  # em dash
    "−": "-",  # signo menos
    "-": "-",  # non-breaking hyphen (ojo: distinto a '-')
})

FOLIO_PATTERN = re.compile(
    r"\b"                             # límite de palabra para evitar capturas dentro de otras palabras
    r"X\s*R\s*O\s*M"                  # XROM permitiendo espacios internos
    r"\s*[-]?\s*"                     # guion opcional, con espacios alrededor
    r"((?:\s*[A-Za-z0-9]){1,5})"      # sufijo 1..5 alfanuméricos tolerando espacios
    r"\b",                            # cierra en límite de palabra (evita el bug del lookahead)
    re.IGNORECASE
)


class FolioValidatorService:
    # extrae el folio del mensaje del usuario buscando el patron dado
    @staticmethod
    def extract_and_validate_folio(text: str) -> str | None:
        if not text:
            return None
        normalized_text = text.translate(DASH_TRANSLATION_TABLE)
        match = FOLIO_PATTERN.search(normalized_text)
        if not match:
            return None  # si no hay coincidencias de xrom, retornamos None

        # contiene el sufijo (lo que va despues de XROM-) con posibles espacios, normalizamos
        raw_suffix = match.group(1)
        suffix = re.sub(r"\s+", "", raw_suffix).upper()  # normalizamos y convertimos a mayusculas

        # construimos el folio completo
        normalized_folio = f"XROM-{suffix}"

        if len(normalized_folio) < 6 or len(normalized_folio) > 10:
            return None
        return normalized_folio

    #Consulta el folio en la base de datos, ahorita anda simulada
    @staticmethod
    def consult_folio_in_database(folio: str) -> dict | None:
        mock_database = {
            "XROM-12345": {
                "folio": "XROM-12345",
                "service_type": "Instalación de Software",
                "status": "Completado",
                "assigned_to": "Juan Pérez",
                "completion_date": "2024-08-15",
            },
            "XROM-ABCDE": {
                "folio": "XROM-ABCDE",
                "service_type": "Mantenimiento de Hardware",
                "status": "En Proceso",
                "assigned_to": "María López",
                "completion_date": None,
            },
        }
        return mock_database.get(folio)