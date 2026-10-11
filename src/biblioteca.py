"""Clase Biblioteca: coordina catálogo, estudiantes y préstamos."""

from datetime import datetime
from typing import Dict, List, Optional

from src.estudiante import Estudiante
from src.excepciones import (
    DatosInvalidosError,
    EstudianteConPendientesError,
    MaterialYaPrestadoError,
)
from src.material import MaterialBibliografico
from src.prestamo import Prestamo


class Biblioteca:
    #Guarda los datos y aplica las reglas del sistema

    def __init__(self) -> None:
        self._materiales: Dict[str, MaterialBibliografico] = {}
        self._estudiantes: Dict[str, Estudiante] = {}
        self._prestamos: List[Prestamo] = []
        self._ultimo_mensaje: str = ""

    @property
    def ultimo_mensaje(self) -> str:
        # Resultado en texto de la última operación realizada.
        return self._ultimo_mensaje

    # Registros 
    def registrar_material(self, material: MaterialBibliografico) -> None:
        # Agrega un Libro o Revista. El código (ISBN/ISSN) es único.
        if material is None:
            raise DatosInvalidosError("No se puede registrar material None.")
        if material.codigo in self._materiales:
            raise DatosInvalidosError(
                f"Ya existe un material con el código {material.codigo}."
            )
        self._materiales[material.codigo] = material

    def registrar_estudiante(self, estudiante: Estudiante) -> None:
        # Agrega un estudiante. El código de estudiante es único.
        if estudiante is None:
            raise DatosInvalidosError("No se puede registrar estudiante None.")
        if estudiante.id in self._estudiantes:
            raise DatosInvalidosError(
                f"Ya existe un estudiante con el código {estudiante.id}."
            )
        self._estudiantes[estudiante.id] = estudiante

    # Búsquedas
    def buscar_material(self, codigo: str) -> Optional[MaterialBibliografico]:
        return self._materiales.get(codigo)

    def buscar_estudiante(self, codigo: str) -> Optional[Estudiante]:
        return self._estudiantes.get(codigo)

    # Operaciones
    def procesar_prestamo(self, material: MaterialBibliografico,
                          estudiante: Estudiante,
                          fecha_prestamo: Optional[datetime] = None) -> bool:
        """
        POLIMORFISMO: solo usa la interfaz de MaterialBibliografico, por
        lo que funciona igual con Libro, Revista o futuros materiales.
        Devuelve True si se realizó; si no, False y el motivo queda en
        ultimo_mensaje. fecha_prestamo es opcional (útil para cargar
        datos de ejemplo con fechas pasadas).
        """
        try:
            # Material None o estudiante None
            if material is None or estudiante is None:
                raise DatosInvalidosError(
                    "El material o el estudiante no existe (None)."
                )

            if self._materiales.get(material.codigo) is not material:
                raise DatosInvalidosError("El material no está registrado.")
            if self._estudiantes.get(estudiante.id) is not estudiante:
                raise DatosInvalidosError("El estudiante no está registrado.")

            prestamo = Prestamo(material, estudiante, fecha_prestamo)
            prestamo.realizar_prestamo()
            self._prestamos.append(prestamo)
            self._ultimo_mensaje = (
                f"Préstamo registrado ({material.tipo}). Devolver antes "
                f"del {prestamo.fecha_estimada.strftime('%d/%m/%Y')}."
            )
            return True
        except MaterialYaPrestadoError as error:
            self._ultimo_mensaje = f"Material no disponible: {error}"
        except EstudianteConPendientesError as error:
            self._ultimo_mensaje = f"Préstamo rechazado: {error}"
        except DatosInvalidosError as error:
            self._ultimo_mensaje = f"Datos inválidos: {error}"
        return False

    def procesar_devolucion(self, material: MaterialBibliografico,
                            estudiante: Estudiante) -> bool:
        # Cierra el préstamo activo de ese estudiante para ese material.
        try:
            if material is None or estudiante is None:
                raise DatosInvalidosError(
                    "El material o el estudiante no existe (None)."
                )
            for prestamo in self._prestamos:
                if (prestamo.material is material
                        and prestamo.estudiante is estudiante
                        and prestamo.esta_activo()):
                    prestamo.finalizar()
                    retraso = prestamo.dias_retraso()
                    if retraso > 0:
                        self._ultimo_mensaje = (
                            f"Devolución registrada con {retraso} día(s) "
                            "de retraso."
                        )
                    else:
                        self._ultimo_mensaje = (
                            "Devolución registrada a tiempo."
                        )
                    return True
            raise DatosInvalidosError(
                "No hay un préstamo activo de ese material para el "
                "estudiante."
            )
        except DatosInvalidosError as error:
            self._ultimo_mensaje = f"Datos inválidos: {error}"
        return False

    # Consultas
    def estado_material(self, codigo: str) -> str:
        material = self.buscar_material(codigo)
        if material is None:
            return "Material no encontrado."
        return str(material)

    def historial_estudiante(self, codigo: str) -> str:
        estudiante = self.buscar_estudiante(codigo)
        if estudiante is None:
            return "Estudiante no registrado."
        lineas = [str(estudiante), "Historial de préstamos:"]
        if len(estudiante.prestamos) == 0:
            lineas.append("  (sin préstamos)")
        for prestamo in estudiante.prestamos:
            lineas.append("  - " + str(prestamo))
        return "\n".join(lineas)

    def listar_materiales(self) -> str:
        if len(self._materiales) == 0:
            return "No hay materiales registrados."
        return "\n".join(str(m) for m in self._materiales.values())

    def listar_estudiantes(self) -> str:
        # Lista todos los estudiantes e indica si tienen pendientes.
        if len(self._estudiantes) == 0:
            return "No hay estudiantes registrados."
        lineas: List[str] = []
        for estudiante in self._estudiantes.values():
            marca = ""
            if estudiante.tiene_prestamos_pendientes():
                marca = " | CON PRÉSTAMOS PENDIENTES"
            lineas.append(str(estudiante) + marca)
        return "\n".join(lineas)

# Eduardo Andre Flores Enao | grupo C