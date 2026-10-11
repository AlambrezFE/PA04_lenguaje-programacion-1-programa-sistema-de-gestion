"""Carga de datos de ejemplo desde un archivo JSON externo."""

from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Any, Dict

from biblioteca import Biblioteca
from estudiante import Estudiante
from excepciones import DatosInvalidosError
from material import Libro, Revista

# El archivo se busca junto a este módulo, sin importar desde qué carpeta

RUTA_DATOS: Path = Path(__file__).resolve().parent / "datos.json"


def cargar_datos(biblioteca: Biblioteca, ruta: Path = RUTA_DATOS) -> str:
    
    """Lee el JSON y registra libros, revistas, estudiantes y préstamos.

    Los préstamos usan "dias_atras" (días antes de hoy) para que el
    ejemplo siga siendo válido sin importar cuándo se ejecute.
    Devuelve un texto con el resumen de lo cargado.
    """
    
    with open(ruta, encoding="utf-8") as archivo:
        datos: Dict[str, Any] = json.load(archivo)

    for item in datos.get("libros", []):
        biblioteca.registrar_material(Libro(
            item["titulo"], item["autor"], item["isbn"], item["cantidad"]))

    for item in datos.get("revistas", []):
        biblioteca.registrar_material(Revista(
            item["titulo"], item["editorial"], item["numero"],
            item["issn"], item["cantidad"]))

    for item in datos.get("estudiantes", []):
        biblioteca.registrar_estudiante(Estudiante(
            item["codigo"], item["nombre"], item["carrera"]))

    for item in datos.get("prestamos", []):
        material = biblioteca.buscar_material(item["material"])
        estudiante = biblioteca.buscar_estudiante(item["estudiante"])
        fecha = datetime.now() - timedelta(days=item["dias_atras"])
        if not biblioteca.procesar_prestamo(material, estudiante, fecha):
            raise DatosInvalidosError(
                f"Préstamo inválido en el dataset: "
                f"{biblioteca.ultimo_mensaje}"
            )
        if item.get("devuelto", False):
            biblioteca.procesar_devolucion(material, estudiante)

    total_materiales = len(datos.get("libros", [])) + len(
        datos.get("revistas", []))
    return (f"Datos de ejemplo cargados: {total_materiales} materiales, "
            f"{len(datos.get('estudiantes', []))} estudiantes, "
            f"{len(datos.get('prestamos', []))} préstamos.")

# Eduardo Andre Flores Enao | grupo C