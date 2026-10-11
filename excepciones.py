"""Excepciones personalizadas del sistema de biblioteca."""


class MaterialYaPrestadoError(Exception):
    """El material no tiene ejemplares disponibles para prestar."""


class DatosInvalidosError(Exception):
    """Datos vacíos, None, duplicados o inexistentes."""


class EstudianteConPendientesError(Exception):
    """El estudiante tiene préstamos vencidos sin devolver."""

# Eduardo Andre Flores Enao | grupo C
