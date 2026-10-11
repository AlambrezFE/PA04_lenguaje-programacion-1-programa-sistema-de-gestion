"""Funciones de validación reutilizables por varias clases."""

from excepciones import DatosInvalidosError


def validar_texto(valor: str, campo: str) -> str:
    """
    Devuelve el texto sin espacios sobrantes.

    Lanza DatosInvalidosError si no es texto o está vacío.
    """
    if not isinstance(valor, str) or valor.strip() == "":
        raise DatosInvalidosError(f"El campo '{campo}' es obligatorio.")
    return valor.strip()

# Eduardo Andre Flores Enao | grupo C
