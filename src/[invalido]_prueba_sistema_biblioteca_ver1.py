"""
SISTEMA DE GESTIÓN PARA BIBLIOTECA UNIVERSITARIA - Versión 1.0
================================================================

Estructura:
    Libro       -> representa un título del catálogo y controla su stock.
    Estudiante  -> representa a un usuario de la biblioteca y su historial.
    Prestamo    -> relaciona un Estudiante con un Libro y maneja las fechas.
    Biblioteca  -> clase "coordinadora": guarda los datos y aplica las reglas
                   del sistema (unicidad de ISBN/código, restricciones, etc.).
"""

from datetime import datetime, timedelta

DIAS_PRESTAMO = 7



class Libro:

    def __init__(self, id_libro, titulo, autor, isbn, cantidad):
        self._id = id_libro
        self._titulo = titulo
        self._autor = autor
        self._isbn = isbn
        self._stock_total = cantidad        # ejemplares que posee la biblioteca
        self._stock_disponible = cantidad   # ejemplares que están en estante
        self._prestado = (cantidad == 0)

    @property
    def id(self):
        return self._id

    @property
    def titulo(self):
        return self._titulo

    @titulo.setter
    def titulo(self, valor):
        if valor.strip() != "":
            self._titulo = valor.strip()

    @property
    def autor(self):
        return self._autor

    @autor.setter
    def autor(self, valor):
        if valor.strip() != "":
            self._autor = valor.strip()

    @property
    def isbn(self):
        return self._isbn

    @property
    def stock_total(self):
        return self._stock_total

    @property
    def stock_disponible(self):
        return self._stock_disponible

    @property
    def prestado(self):
        return self._prestado

    def prestar(self):
        """Reduce el stock en 1. Devuelve True si pudo prestar."""
        if self._stock_disponible <= 0:    
            return False
        self._stock_disponible -= 1
        if self._stock_disponible == 0:
            self._prestado = True
        return True

    def devolver(self):
        """Repone el stock en 1. Devuelve True si pudo devolver."""
        # No se puede devolver más ejemplares de los que existen
        if self._stock_disponible >= self._stock_total:
            return False
        self._stock_disponible += 1
        self._prestado = False              # vuelve a haber al menos uno
        return True

    def estado(self):
        """Texto con el estado actual del libro."""
        if self._prestado:
            return "PRESTADO (sin ejemplares disponibles)"
        return f"DISPONIBLE ({self._stock_disponible} de {self._stock_total} ejemplares)"

    def __str__(self):
        return (f"[{self._id}] '{self._titulo}' - {self._autor} | "
                f"ISBN: {self._isbn} | {self.estado()}")



class Estudiante:
    """Un estudiante registrado. Su _id es el código de estudiante."""

    def __init__(self, id_estudiante, nombre, carrera):
        self._id = id_estudiante
        self._nombre = nombre
        self._carrera = carrera
        self._prestamos = []    # historial de objetos Prestamo

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if valor.strip() != "":
            self._nombre = valor.strip()

    @property
    def carrera(self):
        return self._carrera

    @carrera.setter
    def carrera(self, valor):
        if valor.strip() != "":
            self._carrera = valor.strip()

    @property
    def prestamos(self):
        return list(self._prestamos)

    def agregar_prestamo(self, prestamo):
        self._prestamos.append(prestamo)

    def tiene_prestamos_pendientes(self):
        """True si tiene algún préstamo sin devolver (vencido o no)."""
        for p in self._prestamos:
            if p.estado == Prestamo.ACTIVO:
                return True
        return False

    def __str__(self):
        return f"[{self._id}] {self._nombre} - Carrera: {self._carrera}"



class Prestamo:
    """Relaciona un Estudiante con un Libro y guarda las fechas."""

    ACTIVO = "ACTIVO"
    FINALIZADO = "FINALIZADO"

    def __init__(self, libro, estudiante, fecha_prestamo=None):
        self._libro = libro
        self._estudiante = estudiante
        # Si no se indica fecha, se usa el momento actual (módulo datetime)
        self._fecha_prestamo = fecha_prestamo or datetime.now()
        # Fecha estimada = fecha de salida + días de plazo
        self._fecha_estimada = self._fecha_prestamo + timedelta(days=DIAS_PRESTAMO)
        self._fecha_devolucion = None       # se llena al devolver
        self._estado = Prestamo.ACTIVO

    @property
    def libro(self):
        return self._libro

    @property
    def estudiante(self):
        return self._estudiante

    @property
    def fecha_prestamo(self):
        return self._fecha_prestamo

    @property
    def fecha_estimada(self):
        return self._fecha_estimada

    @property
    def fecha_devolucion(self):
        return self._fecha_devolucion

    @property
    def estado(self):
        return self._estado

    def esta_vencido(self):
        """Un préstamo está vencido si sigue activo y pasó la fecha estimada."""
        return self._estado == Prestamo.ACTIVO and datetime.now() > self._fecha_estimada

    def realizar_prestamo(self):
        """Valida las reglas y ejecuta el préstamo.
        Devuelve (True/False, mensaje)."""
        if self._estudiante.tiene_prestamos_pendientes():
            return False, "El estudiante tiene préstamos pendientes de devolución."

        if self._libro.prestado or self._libro.stock_disponible == 0:
            return False, "El libro no tiene ejemplares disponibles."

        self._libro.prestar()
        self._estudiante.agregar_prestamo(self)
        return True, (f"Préstamo registrado. Devolver antes del "
                      f"{self._fecha_estimada.strftime('%d/%m/%Y')}.")

    def finalizar(self):
        if self._estado == Prestamo.FINALIZADO:
            return False, "Este préstamo ya fue finalizado."

        self._libro.devolver()                  # repone el stock
        self._fecha_devolucion = datetime.now()
        self._estado = Prestamo.FINALIZADO

        if self._fecha_devolucion > self._fecha_estimada:
            dias = (self._fecha_devolucion - self._fecha_estimada).days
            return True, f"Devolución registrada con {dias} día(s) de retraso."
        return True, "Devolución registrada a tiempo."

    def __str__(self):
        salida = self._fecha_prestamo.strftime("%d/%m/%Y")
        estimada = self._fecha_estimada.strftime("%d/%m/%Y")
        if self._estado == Prestamo.FINALIZADO:
            fin = self._fecha_devolucion.strftime("%d/%m/%Y")
            detalle = f"devuelto el {fin}"
        elif self.esta_vencido():
            detalle = "VENCIDO"
        else:
            detalle = "en curso"
        return (f"'{self._libro.titulo}' | salida: {salida} | "
                f"devolver antes de: {estimada} | {self._estado} ({detalle})")


class Biblioteca:
    def __init__(self):
        self._libros = {}         # clave: ISBN       -> Libro
        self._estudiantes = {}    # clave: código     -> Estudiante
        self._prestamos = []      # todos los préstamos
        self._siguiente_id = 1    # contador para ids de libros

    # ---------- Registros ----------
    def registrar_libro(self, titulo, autor, isbn, cantidad):
        if titulo.strip() == "" or autor.strip() == "" or isbn.strip() == "":
            return False, "Título, autor e ISBN son obligatorios."
        if isbn in self._libros:                       
            return False, "Ya existe un libro con ese ISBN."
        if cantidad < 1:
            return False, "La cantidad debe ser al menos 1."

        libro = Libro(self._siguiente_id, titulo.strip(), autor.strip(),
                      isbn.strip(), cantidad)
        self._libros[isbn] = libro
        self._siguiente_id += 1
        return True, f"Libro registrado: {libro.titulo}"

    def registrar_estudiante(self, codigo, nombre, carrera):
        if codigo.strip() == "" or nombre.strip() == "" or carrera.strip() == "":
            return False, "Código, nombre y carrera son obligatorios."
        if codigo in self._estudiantes:                
            return False, "Ya existe un estudiante con ese código."

        self._estudiantes[codigo] = Estudiante(codigo, nombre.strip(), carrera.strip())
        return True, f"Estudiante registrado: {nombre.strip()}"

    def prestar_libro(self, codigo, isbn):
        if codigo not in self._estudiantes:
            return False, "Estudiante no registrado."
        if isbn not in self._libros:
            return False, "Libro no encontrado."

        prestamo = Prestamo(self._libros[isbn], self._estudiantes[codigo])
        ok, mensaje = prestamo.realizar_prestamo()
        if ok:
            self._prestamos.append(prestamo)
        return ok, mensaje

    def devolver_libro(self, codigo, isbn):
        if codigo not in self._estudiantes:
            return False, "Estudiante no registrado."
        if isbn not in self._libros:
            return False, "Libro no encontrado."

        for p in self._prestamos:
            if (p.estudiante.id == codigo and p.libro.isbn == isbn
                    and p.estado == Prestamo.ACTIVO):
                return p.finalizar()
        return False, "No hay un préstamo activo de ese libro para el estudiante."

    def estado_libro(self, isbn):
        if isbn not in self._libros:
            return "Libro no encontrado."
        return str(self._libros[isbn])

    def historial_estudiante(self, codigo):
        if codigo not in self._estudiantes:
            return "Estudiante no registrado."
        est = self._estudiantes[codigo]
        lineas = [str(est), "Historial de préstamos:"]
        if len(est.prestamos) == 0:
            lineas.append("  (sin préstamos)")
        for p in est.prestamos:
            lineas.append("  - " + str(p))
        return "\n".join(lineas)

    def listar_libros(self):
        if len(self._libros) == 0:
            return "No hay libros registrados."
        return "\n".join(str(l) for l in self._libros.values())


def leer_entero(mensaje):
    """Pide un número entero; repite hasta que el usuario escriba uno válido."""
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("  Ingrese un número entero válido.")


def menu():
    biblioteca = Biblioteca()
    while True:
        print("\n===== BIBLIOTECA UNIVERSITARIA =====")
        print("1. Registrar libro")
        print("2. Registrar estudiante")
        print("3. Prestar libro")
        print("4. Devolver libro")
        print("5. Consultar estado de un libro")
        print("6. Historial de un estudiante")
        print("7. Listar catálogo")
        print("0. Salir")
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            titulo = input("Título: ")
            autor = input("Autor: ")
            isbn = input("ISBN: ").strip()
            cantidad = leer_entero("Cantidad de ejemplares: ")
            print(biblioteca.registrar_libro(titulo, autor, isbn, cantidad)[1])
        elif opcion == "2":
            codigo = input("Código de estudiante: ").strip()
            nombre = input("Nombre completo: ")
            carrera = input("Carrera: ")
            print(biblioteca.registrar_estudiante(codigo, nombre, carrera)[1])
        elif opcion == "3":
            codigo = input("Código de estudiante: ").strip()
            isbn = input("ISBN del libro: ").strip()
            print(biblioteca.prestar_libro(codigo, isbn)[1])
        elif opcion == "4":
            codigo = input("Código de estudiante: ").strip()
            isbn = input("ISBN del libro: ").strip()
            print(biblioteca.devolver_libro(codigo, isbn)[1])
        elif opcion == "5":
            print(biblioteca.estado_libro(input("ISBN del libro: ").strip()))
        elif opcion == "6":
            print(biblioteca.historial_estudiante(input("Código de estudiante: ").strip()))
        elif opcion == "7":
            print(biblioteca.listar_libros())
        elif opcion == "0":
            print("Hasta pronto.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu()

# Eduardo Andre Flores Enao | grupo C