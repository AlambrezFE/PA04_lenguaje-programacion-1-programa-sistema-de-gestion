"""Menú de consola: interacción con el usuario."""

from typing import Callable, Dict, Optional, Tuple

from biblioteca import Biblioteca
from estudiante import Estudiante
from excepciones import DatosInvalidosError
from material import Libro, MaterialBibliografico, Revista


def leer_entero(mensaje: str) -> int:
    """Pide un entero y repite hasta que el valor sea válido."""
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("  Ingrese un número entero válido.")


def _pedir_estudiante_y_material(
    biblioteca: Biblioteca,
) -> Tuple[Optional[Estudiante], Optional[MaterialBibliografico]]:
    """Pide los códigos y busca ambos objetos (None si no existen)."""
    estudiante = biblioteca.buscar_estudiante(
        input("Código de estudiante: ").strip())
    material = biblioteca.buscar_material(
        input("ISBN/ISSN del material: ").strip())
    return estudiante, material


# ---------- Una función por cada opción del menú ----------
def registrar_libro(biblioteca: Biblioteca) -> None:
    libro = Libro(input("Título: "), input("Autor: "), input("ISBN: "),
                  leer_entero("Cantidad de ejemplares: "))
    biblioteca.registrar_material(libro)
    print("Libro registrado.")


def registrar_revista(biblioteca: Biblioteca) -> None:
    revista = Revista(input("Título: "), input("Editorial: "),
                      leer_entero("Número de edición: "), input("ISSN: "),
                      leer_entero("Cantidad de ejemplares: "))
    biblioteca.registrar_material(revista)
    print("Revista registrada.")


def registrar_estudiante(biblioteca: Biblioteca) -> None:
    estudiante = Estudiante(input("Código de estudiante: "),
                            input("Nombre completo: "), input("Carrera: "))
    biblioteca.registrar_estudiante(estudiante)
    print("Estudiante registrado.")


def prestar_material(biblioteca: Biblioteca) -> None:
    estudiante, material = _pedir_estudiante_y_material(biblioteca)
    # Si algo no existe llega None y procesar_prestamo lo maneja
    biblioteca.procesar_prestamo(material, estudiante)
    print(biblioteca.ultimo_mensaje)


def devolver_material(biblioteca: Biblioteca) -> None:
    estudiante, material = _pedir_estudiante_y_material(biblioteca)
    biblioteca.procesar_devolucion(material, estudiante)
    print(biblioteca.ultimo_mensaje)


def consultar_material(biblioteca: Biblioteca) -> None:
    print(biblioteca.estado_material(
        input("ISBN/ISSN del material: ").strip()))


def historial_estudiante(biblioteca: Biblioteca) -> None:
    print(biblioteca.historial_estudiante(
        input("Código de estudiante: ").strip()))


def listar_materiales(biblioteca: Biblioteca) -> None:
    print(biblioteca.listar_materiales())


def listar_estudiantes(biblioteca: Biblioteca) -> None:
    print(biblioteca.listar_estudiantes())


# Tabla de opciones: número -> (texto, función que la ejecuta)
OPCIONES: Dict[str, Tuple[str, Callable[[Biblioteca], None]]] = {
    "1": ("Registrar libro", registrar_libro),
    "2": ("Registrar revista", registrar_revista),
    "3": ("Registrar estudiante", registrar_estudiante),
    "4": ("Prestar material", prestar_material),
    "5": ("Devolver material", devolver_material),
    "6": ("Consultar estado de un material", consultar_material),
    "7": ("Historial de un estudiante", historial_estudiante),
    "8": ("Listar catálogo", listar_materiales),
    "9": ("Listar estudiantes", listar_estudiantes),
}


def mostrar_menu() -> None:
    print("\n===== BIBLIOTECA UNIVERSITARIA =====")
    for numero, (texto, _) in OPCIONES.items():
        print(f"{numero}. {texto}")
    print("0. Salir")


def ejecutar_menu(biblioteca: Biblioteca) -> None:
    """Bucle principal: muestra el menú hasta que el usuario sale."""
    while True:
        mostrar_menu()
        opcion = input("Elija una opción: ").strip()
        if opcion == "0":
            print("Hasta pronto.")
            break
        if opcion not in OPCIONES:
            print("Opción no válida.")
            continue
        try:
            OPCIONES[opcion][1](biblioteca)
        except DatosInvalidosError as error:
            print(f"Error: {error}")
