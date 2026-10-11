"""Sistema de gestión para biblioteca universitaria - Versión 2.0.

Requiere Python 3.8+ y solo usa la librería estándar.
Ejecutar con:  python biblioteca.py

Novedades de la versión 2:
    * MaterialBibliografico: clase abstracta (interfaz) creada con ABC.
    * Libro y Revista heredan de ella (plazos de 7 y 3 días).
    * Biblioteca.procesar_prestamo() funciona con cualquier material
      (polimorfismo).
    * Excepciones personalizadas y manejo con try-except.

Estructura:
    MaterialBibliografico (ABC)
        |-- Libro     (plazo: 7 días)
        |-- Revista   (plazo: 3 días)
    Estudiante   -> usuario de la biblioteca y su historial.
    Prestamo     -> relaciona un Estudiante con un material.
    Biblioteca   -> guarda los datos y aplica las reglas del sistema.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid


# ======================================================================
# EXCEPCIONES PERSONALIZADAS
# ======================================================================
class MaterialYaPrestadoError(Exception):
    """El material no tiene ejemplares disponibles para prestar."""


class DatosInvalidosError(Exception):
    """Datos vacíos, None, duplicados o inexistentes."""


class EstudianteConPendientesError(Exception):
    """El estudiante tiene préstamos vencidos o sin devolver."""


def _validar_texto(valor: str, campo: str) -> str:
    """Devuelve el texto sin espacios sobrantes o lanza un error si
    está vacío (validación compartida por todas las clases)."""
    if not isinstance(valor, str) or valor.strip() == "":
        raise DatosInvalidosError(f"El campo '{campo}' es obligatorio.")
    return valor.strip()


# ======================================================================
# CLASE ABSTRACTA (INTERFAZ)
# ======================================================================
class MaterialBibliografico(ABC):
    """Contrato que deben cumplir todos los materiales de la biblioteca.

    No se puede instanciar directamente: obliga a las clases hijas a
    implementar prestar(), devolver(), esta_prestado(), plazo_dias y tipo.
    Aquí también se guardan los datos y la lógica de stock que comparten
    Libro y Revista, para no repetir código.
    """

    def __init__(self, titulo: str, codigo: str, cantidad: int) -> None:
        if not isinstance(cantidad, int) or cantidad < 1:
            raise DatosInvalidosError(
                "La cantidad de ejemplares debe ser un entero mayor a 0."
            )
        self._id: str = uuid.uuid4().hex[:8]    # identificador interno
        self._titulo: str = _validar_texto(titulo, "título")
        self._codigo: str = _validar_texto(codigo, "código")
        self._stock_total: int = cantidad       # ejemplares que existen
        self._stock_disponible: int = cantidad  # ejemplares en estante
        self._prestado: bool = False            # True si no queda ninguno

    # ---------- Properties ----------
    @property
    def id(self) -> str:
        return self._id

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        self._titulo = _validar_texto(valor, "título")

    @property
    def codigo(self) -> str:
        """Identificador único (ISBN en libros, ISSN en revistas)."""
        return self._codigo

    @property
    def stock_total(self) -> int:
        return self._stock_total

    @property
    def stock_disponible(self) -> int:
        return self._stock_disponible

    @property
    def prestado(self) -> bool:
        return self._prestado

    # ---------- Parte abstracta: cada hijo debe implementarla ----------
    @property
    @abstractmethod
    def plazo_dias(self) -> int:
        """Días de plazo de devolución según el tipo de material."""

    @property
    @abstractmethod
    def tipo(self) -> str:
        """Nombre del tipo de material ('Libro', 'Revista')."""

    @abstractmethod
    def prestar(self) -> bool:
        """Descuenta un ejemplar. True si se pudo prestar."""

    @abstractmethod
    def devolver(self) -> bool:
        """Repone un ejemplar. True si se pudo devolver."""

    @abstractmethod
    def esta_prestado(self) -> bool:
        """True si no queda ningún ejemplar disponible."""

    # ---------- Lógica común (protegida: solo para las clases hijas) ----
    def _descontar_stock(self) -> bool:
        if self._stock_disponible <= 0:     # restricción: stock en cero
            return False
        self._stock_disponible -= 1
        if self._stock_disponible == 0:     # era el último ejemplar
            self._prestado = True
        return True

    def _reponer_stock(self) -> bool:
        # No se pueden devolver más ejemplares de los que existen
        if self._stock_disponible >= self._stock_total:
            return False
        self._stock_disponible += 1
        self._prestado = False
        return True

    def estado(self) -> str:
        """Texto con el estado actual del material."""
        if self._prestado:
            return "PRESTADO (sin ejemplares disponibles)"
        return (f"DISPONIBLE ({self._stock_disponible} de "
                f"{self._stock_total} ejemplares)")


# ======================================================================
# CLASES HIJAS: LIBRO Y REVISTA
# ======================================================================
class Libro(MaterialBibliografico):
    """Libro del catálogo. Plazo de préstamo: 7 días."""

    PLAZO_DIAS: int = 7

    def __init__(self, titulo: str, autor: str, isbn: str,
                 cantidad: int) -> None:
        super().__init__(titulo, isbn, cantidad)    # el ISBN es el código
        self._autor: str = _validar_texto(autor, "autor")

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        self._autor = _validar_texto(valor, "autor")

    @property
    def isbn(self) -> str:
        return self._codigo

    @property
    def plazo_dias(self) -> int:
        return self.PLAZO_DIAS

    @property
    def tipo(self) -> str:
        return "Libro"

    def prestar(self) -> bool:
        return self._descontar_stock()

    def devolver(self) -> bool:
        return self._reponer_stock()

    def esta_prestado(self) -> bool:
        return self._prestado

    def __str__(self) -> str:
        return (f"[Libro {self._id}] '{self._titulo}' - {self._autor} | "
                f"ISBN: {self._codigo} | {self.estado()}")


class Revista(MaterialBibliografico):
    """Revista del catálogo. Plazo de préstamo: 3 días."""

    PLAZO_DIAS: int = 3

    def __init__(self, titulo: str, editorial: str, numero: int,
                 issn: str, cantidad: int) -> None:
        super().__init__(titulo, issn, cantidad)    # el ISSN es el código
        if not isinstance(numero, int) or numero < 1:
            raise DatosInvalidosError(
                "El número de edición debe ser un entero mayor a 0."
            )
        self._editorial: str = _validar_texto(editorial, "editorial")
        self._numero: int = numero

    @property
    def editorial(self) -> str:
        return self._editorial

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def issn(self) -> str:
        return self._codigo

    @property
    def plazo_dias(self) -> int:
        return self.PLAZO_DIAS

    @property
    def tipo(self) -> str:
        return "Revista"

    def prestar(self) -> bool:
        return self._descontar_stock()

    def devolver(self) -> bool:
        return self._reponer_stock()

    def esta_prestado(self) -> bool:
        return self._prestado

    def __str__(self) -> str:
        return (f"[Revista {self._id}] '{self._titulo}' N.º {self._numero}"
                f" - {self._editorial} | ISSN: {self._codigo} | "
                f"{self.estado()}")


# ======================================================================
# CLASE ESTUDIANTE
# ======================================================================
class Estudiante:
    """Estudiante registrado. Su _id es el código de estudiante."""

    def __init__(self, id_estudiante: str, nombre: str,
                 carrera: str) -> None:
        self._id: str = _validar_texto(id_estudiante, "código")
        self._nombre: str = _validar_texto(nombre, "nombre")
        self._carrera: str = _validar_texto(carrera, "carrera")
        self._prestamos: List["Prestamo"] = []      # historial

    @property
    def id(self) -> str:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = _validar_texto(valor, "nombre")

    @property
    def carrera(self) -> str:
        return self._carrera

    @carrera.setter
    def carrera(self, valor: str) -> None:
        self._carrera = _validar_texto(valor, "carrera")

    @property
    def prestamos(self) -> List["Prestamo"]:
        # Se devuelve una copia para proteger la lista original
        return list(self._prestamos)

    def agregar_prestamo(self, prestamo: "Prestamo") -> None:
        self._prestamos.append(prestamo)

    def tiene_prestamos_pendientes(self) -> bool:
        """True si tiene algún préstamo sin devolver (vencido o no)."""
        for prestamo in self._prestamos:
            if prestamo.estado == Prestamo.ACTIVO:
                return True
        return False

    def __str__(self) -> str:
        return f"[{self._id}] {self._nombre} - Carrera: {self._carrera}"


# ======================================================================
# CLASE PRESTAMO
# ======================================================================
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

    def esta_vencido(self) -> bool:
        """Vencido = sigue activo y ya pasó la fecha estimada."""
        return (self._estado == Prestamo.ACTIVO
                and datetime.now() > self._fecha_estimada)

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
        if self._estado == Prestamo.FINALIZADO:
            raise DatosInvalidosError("Este préstamo ya fue finalizado.")
        self._material.devolver()
        self._fecha_devolucion = datetime.now()
        self._estado = Prestamo.FINALIZADO
        return True

    def __str__(self) -> str:
        salida = self._fecha_prestamo.strftime("%d/%m/%Y")
        estimada = self._fecha_estimada.strftime("%d/%m/%Y")
        if self._estado == Prestamo.FINALIZADO and self._fecha_devolucion:
            detalle = ("devuelto el "
                       + self._fecha_devolucion.strftime("%d/%m/%Y"))
        elif self.esta_vencido():
            detalle = "VENCIDO"
        else:
            detalle = "en curso"
        return (f"[{self._material.tipo}] '{self._material.titulo}' | "
                f"salida: {salida} | devolver antes de: {estimada} | "
                f"{self._estado} ({detalle})")


# ======================================================================
# CLASE BIBLIOTECA
# ======================================================================
class Biblioteca:
    """Coordina el catálogo, los estudiantes y los préstamos."""

    def __init__(self) -> None:
        self._materiales: Dict[str, MaterialBibliografico] = {}
        self._estudiantes: Dict[str, Estudiante] = {}
        self._prestamos: List[Prestamo] = []
        self._ultimo_mensaje: str = ""

    @property
    def ultimo_mensaje(self) -> str:
        """Resultado en texto de la última operación realizada."""
        return self._ultimo_mensaje

    # ---------- Registros ----------
    def registrar_material(self, material: MaterialBibliografico) -> None:
        """Agrega un Libro o Revista. El código (ISBN/ISSN) es único."""
        if material is None:
            raise DatosInvalidosError("No se puede registrar material None.")
        if material.codigo in self._materiales:
            raise DatosInvalidosError(
                f"Ya existe un material con el código {material.codigo}."
            )
        self._materiales[material.codigo] = material

    def registrar_estudiante(self, estudiante: Estudiante) -> None:
        """Agrega un estudiante. El código de estudiante es único."""
        if estudiante is None:
            raise DatosInvalidosError("No se puede registrar estudiante None.")
        if estudiante.id in self._estudiantes:
            raise DatosInvalidosError(
                f"Ya existe un estudiante con el código {estudiante.id}."
            )
        self._estudiantes[estudiante.id] = estudiante

    # ---------- Búsquedas ----------
    def buscar_material(self, codigo: str) -> Optional[MaterialBibliografico]:
        return self._materiales.get(codigo)

    def buscar_estudiante(self, codigo: str) -> Optional[Estudiante]:
        return self._estudiantes.get(codigo)

    # ---------- Operaciones ----------
    def procesar_prestamo(self, material: MaterialBibliografico,
                          estudiante: Estudiante) -> bool:
        """Presta cualquier tipo de material a un estudiante.

        POLIMORFISMO: solo usa la interfaz de MaterialBibliografico, por
        lo que funciona igual con Libro, Revista o futuros materiales.
        Devuelve True si se realizó; si no, False y el motivo queda en
        ultimo_mensaje.
        """
        try:
            # Material None o estudiante None
            if material is None or estudiante is None:
                raise DatosInvalidosError(
                    "El material o el estudiante no existe (None)."
                )
            # Ambos deben estar registrados en esta biblioteca
            if self._materiales.get(material.codigo) is not material:
                raise DatosInvalidosError("El material no está registrado.")
            if self._estudiantes.get(estudiante.id) is not estudiante:
                raise DatosInvalidosError("El estudiante no está registrado.")

            prestamo = Prestamo(material, estudiante)
            prestamo.realizar_prestamo()    # puede lanzar excepciones
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
        """Cierra el préstamo activo de ese estudiante para ese material."""
        try:
            if material is None or estudiante is None:
                raise DatosInvalidosError(
                    "El material o el estudiante no existe (None)."
                )
            for prestamo in self._prestamos:
                if (prestamo.material is material
                        and prestamo.estudiante is estudiante
                        and prestamo.estado == Prestamo.ACTIVO):
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

    # ---------- Consultas ----------
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


# ======================================================================
# MENÚ DE CONSOLA
# ======================================================================
def leer_entero(mensaje: str) -> int:
    """Pide un entero y repite hasta que el valor sea válido."""
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("  Ingrese un número entero válido.")


def menu() -> None:
    biblioteca = Biblioteca()
    while True:
        print("\n===== BIBLIOTECA UNIVERSITARIA =====")
        print("1. Registrar libro")
        print("2. Registrar revista")
        print("3. Registrar estudiante")
        print("4. Prestar material")
        print("5. Devolver material")
        print("6. Consultar estado de un material")
        print("7. Historial de un estudiante")
        print("8. Listar catálogo")
        print("0. Salir")
        opcion = input("Elija una opción: ").strip()

        try:
            if opcion == "1":
                libro = Libro(input("Título: "), input("Autor: "),
                              input("ISBN: "),
                              leer_entero("Cantidad de ejemplares: "))
                biblioteca.registrar_material(libro)
                print("Libro registrado.")
            elif opcion == "2":
                revista = Revista(input("Título: "), input("Editorial: "),
                                  leer_entero("Número de edición: "),
                                  input("ISSN: "),
                                  leer_entero("Cantidad de ejemplares: "))
                biblioteca.registrar_material(revista)
                print("Revista registrada.")
            elif opcion == "3":
                estudiante = Estudiante(input("Código de estudiante: "),
                                        input("Nombre completo: "),
                                        input("Carrera: "))
                biblioteca.registrar_estudiante(estudiante)
                print("Estudiante registrado.")
            elif opcion in ("4", "5"):
                est = biblioteca.buscar_estudiante(
                    input("Código de estudiante: ").strip())
                mat = biblioteca.buscar_material(
                    input("ISBN/ISSN del material: ").strip())
                # Si algo no existe llega None y el método lo maneja
                if opcion == "4":
                    biblioteca.procesar_prestamo(mat, est)
                else:
                    biblioteca.procesar_devolucion(mat, est)
                print(biblioteca.ultimo_mensaje)
            elif opcion == "6":
                print(biblioteca.estado_material(
                    input("ISBN/ISSN del material: ").strip()))
            elif opcion == "7":
                print(biblioteca.historial_estudiante(
                    input("Código de estudiante: ").strip()))
            elif opcion == "8":
                print(biblioteca.listar_materiales())
            elif opcion == "0":
                print("Hasta pronto.")
                break
            else:
                print("Opción no válida.")
        except DatosInvalidosError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    menu()