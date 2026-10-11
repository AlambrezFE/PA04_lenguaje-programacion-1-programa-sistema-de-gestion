"""Clase Prestamo: relaciona un estudiante con un material."""

from datetime import datetime, timedelta
from typing import Optional

from estudiante import Estudiante
from excepciones import (
    DatosInvalidosError,
    EstudianteConPendientesError,
    MaterialYaPrestadoError,
)
from material import MaterialBibliografico


class Prestamo:
    """Relaciona un Estudiante con un material (Libro o Revista)."""

    ACTIVO: str = "ACTIVO"
    FINALIZADO: str = "FINALIZADO"

    def __init__(self, material: MaterialBibliografico,
                 estudiante: Estudiante,
                 fecha_prestamo: Optional[datetime] = None) -> None:
        if material is None or estudiante is None:
            raise DatosInvalidosError(
                "El material y el estudiante son obligatorios."
            )
        self._material: MaterialBibliografico = material
        self._estudiante: Estudiante = estudiante
        self._fecha_prestamo: datetime = fecha_prestamo or datetime.now()
        # POLIMORFISMO: cada material aporta su propio plazo
        self._fecha_estimada: datetime = self._fecha_prestamo + timedelta(
            days=material.plazo_dias
        )
        self._fecha_devolucion: Optional[datetime] = None
        self._estado: str = Prestamo.ACTIVO

    @property
    def material(self) -> MaterialBibliografico:
        return self._material

    @property
    def estudiante(self) -> Estudiante:
        return self._estudiante

    @property
    def fecha_prestamo(self) -> datetime:
        return self._fecha_prestamo

    @property
    def fecha_estimada(self) -> datetime:
        return self._fecha_estimada

    @property
    def fecha_devolucion(self) -> Optional[datetime]:
        return self._fecha_devolucion

    @property
    def estado(self) -> str:
        return self._estado

    def esta_activo(self) -> bool:
        """True si el préstamo aún no fue devuelto."""
        return self._estado == Prestamo.ACTIVO

    def esta_vencido(self) -> bool:
        """Vencido = sigue activo y ya pasó la fecha estimada."""
        return self.esta_activo() and datetime.now() > self._fecha_estimada

    def dias_retraso(self) -> int:
        """Días de retraso (0 si no hay retraso)."""
        fin = self._fecha_devolucion or datetime.now()
        if fin > self._fecha_estimada:
            return (fin - self._fecha_estimada).days
        return 0

    def realizar_prestamo(self) -> bool:
        """Valida las reglas y ejecuta el préstamo.

        Lanza EstudianteConPendientesError o MaterialYaPrestadoError si
        alguna regla no se cumple.
        """
        # Regla: no prestar a quien tiene préstamos vencidos o pendientes
        if self._estudiante.tiene_prestamos_pendientes():
            raise EstudianteConPendientesError(
                f"{self._estudiante.nombre} tiene préstamos pendientes "
                "de devolución."
            )
        # Regla: no prestar un material sin ejemplares disponibles
        if self._material.esta_prestado():
            raise MaterialYaPrestadoError(
                f"'{self._material.titulo}' ya está prestado."
            )
        self._material.prestar()                    # descuenta el stock
        self._estudiante.agregar_prestamo(self)     # queda en el historial
        return True

    def finalizar(self) -> bool:
        """Procesa la devolución: repone el stock y cierra el préstamo."""
        if not self.esta_activo():
            raise DatosInvalidosError("Este préstamo ya fue finalizado.")
        self._material.devolver()
        self._fecha_devolucion = datetime.now()
        self._estado = Prestamo.FINALIZADO
        return True

    def __str__(self) -> str:
        salida = self._fecha_prestamo.strftime("%d/%m/%Y")
        estimada = self._fecha_estimada.strftime("%d/%m/%Y")
        if self._fecha_devolucion is not None:
            detalle = ("devuelto el "
                       + self._fecha_devolucion.strftime("%d/%m/%Y"))
        elif self.esta_vencido():
            detalle = "VENCIDO"
        else:
            detalle = "en curso"
        return (f"[{self._material.tipo}] '{self._material.titulo}' | "
                f"salida: {salida} | devolver antes de: {estimada} | "
                f"{self._estado} ({detalle})")
