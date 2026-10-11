"""Punto de entrada del sistema. Ejecutar con:  python main.py"""

from biblioteca import Biblioteca
from src.datos import cargar_datos
from src.excepciones import DatosInvalidosError
from src.menu import ejecutar_menu


def main() -> None:
    biblioteca = Biblioteca()
    # Se cargan los datos ficticios desde datos.json; si falla, el programa arranca igualmente con la biblioteca vacía.
    try:
        print(cargar_datos(biblioteca))
    except FileNotFoundError:
        print("Aviso: no se encontró datos.json. Se inicia sin datos.")
    except (ValueError, KeyError, DatosInvalidosError) as error:
        print(f"Aviso: datos.json es inválido ({error}). Se inicia sin datos.")
        biblioteca = Biblioteca()
    ejecutar_menu(biblioteca)


if __name__ == "__main__":
    main()

# Eduardo Andre Flores Enao | grupo C
