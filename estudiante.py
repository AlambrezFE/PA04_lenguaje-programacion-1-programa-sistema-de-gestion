"""Clase Estudiante."""

from typing import TYPE_CHECKING, List

from validaciones import validar_texto

# Solo se importa para los type hints; así se evita una importación
# circular con prestamo.py (que a su vez importa este módulo).
if TYPE_CHECKING:
    from prestamo import Prestamo


class Estudiante:
    #Estudiante registrado. Su _id es el código de estudiante.

    def __init__(self, id_estudiante: str, nombre: str,
                 carrera: str) -> None:
        self._id: str = validar_texto(id_estudiante, "código")
        self._nombre: str = validar_texto(nombre, "nombre")
        self._carrera: str = validar_texto(carrera, "carrera")
        self._prestamos: List["Prestamo"] = []      # historial

    @property
    def id(self) -> str:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "nombre")

    @property
    def carrera(self) -> str:
        return self._carrera

    @carrera.setter
    def carrera(self, valor: str) -> None:
        self._carrera = validar_texto(valor, "carrera")

    @property
    def prestamos(self) -> List["Prestamo"]:
        # Se devuelve una copia para proteger la lista original
        return list(self._prestamos)

    def agregar_prestamo(self, prestamo: "Prestamo") -> None:
        self._prestamos.append(prestamo)

    def tiene_prestamos_pendientes(self) -> bool:
        #True si tiene algún préstamo sin devolver (vencido o no).
        for prestamo in self._prestamos:
            if prestamo.esta_activo():
                return True
        return False

    def __str__(self) -> str:
        return f"[{self._id}] {self._nombre} - Carrera: {self._carrera}"
