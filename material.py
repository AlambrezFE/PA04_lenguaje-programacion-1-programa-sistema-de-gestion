"""
Jerarquía de materiales bibliográficos.

MaterialBibliografico (ABC)
    |-- Libro     (plazo: 7 días)
    |-- Revista   (plazo: 3 días)
"""

from abc import ABC, abstractmethod
import uuid

from excepciones import DatosInvalidosError
from validaciones import validar_texto


class MaterialBibliografico(ABC):

    def __init__(self, titulo: str, codigo: str, cantidad: int) -> None:
        if not isinstance(cantidad, int) or cantidad < 1:
            raise DatosInvalidosError(
                "La cantidad de ejemplares debe ser un entero mayor a 0."
            )
        self._id: str = uuid.uuid4().hex[:8]    # identificador interno
        self._titulo: str = validar_texto(titulo, "título")
        self._codigo: str = validar_texto(codigo, "código")
        self._stock_total: int = cantidad       # ejemplares que existen
        self._stock_disponible: int = cantidad  # ejemplares en estante
        self._prestado: bool = False            # True si no queda ninguno

    # Properties 
    @property
    def id(self) -> str:
        return self._id

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        self._titulo = validar_texto(valor, "título")

    @property
    def codigo(self) -> str:
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

    # Parte abstracta: cada hijo debe implementarla
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

    # Lógica común (protegida: solo para las clases hijas)
    
    def _descontar_stock(self) -> bool:
        if self._stock_disponible <= 0: 
            return False
        self._stock_disponible -= 1
        if self._stock_disponible == 0:    
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
        if self._prestado:
            return "PRESTADO (sin ejemplares disponibles)"
        return (f"DISPONIBLE ({self._stock_disponible} de "
                f"{self._stock_total} ejemplares)")


class Libro(MaterialBibliografico):
    # Libro del catálogo. Plazo de préstamo: 7 días.

    PLAZO_DIAS: int = 7

    def __init__(self, titulo: str, autor: str, isbn: str,
                 cantidad: int) -> None:
        super().__init__(titulo, isbn, cantidad)    # el ISBN es el código
        self._autor: str = validar_texto(autor, "autor")

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        self._autor = validar_texto(valor, "autor")

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
        return (f"[Libro] '{self._titulo}' - {self._autor} | "
                f"ISBN: {self._codigo} | {self.estado()}")


class Revista(MaterialBibliografico):
    # Revista del catálogo. Plazo de préstamo: 3 días.

    PLAZO_DIAS: int = 3

    def __init__(self, titulo: str, editorial: str, numero: int,
                 issn: str, cantidad: int) -> None:
        super().__init__(titulo, issn, cantidad)    # el ISSN es el código
        if not isinstance(numero, int) or numero < 1:
            raise DatosInvalidosError(
                "El número de edición debe ser un entero mayor a 0."
            )
        self._editorial: str = validar_texto(editorial, "editorial")
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
        return (f"[Revista] '{self._titulo}' N.º {self._numero} - "
                f"{self._editorial} | ISSN: {self._codigo} | "
                f"{self.estado()}")

# Eduardo Andre Flores Enao | grupo C
