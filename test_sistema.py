"""Pruebas de funcionalidad del sistema de biblioteca."""

from datetime import datetime, timedelta
import unittest

from biblioteca import Biblioteca
from datos import cargar_datos
from estudiante import Estudiante
from excepciones import (
    DatosInvalidosError,
    EstudianteConPendientesError,
    MaterialYaPrestadoError,
)
from material import Libro, MaterialBibliografico, Revista
from prestamo import Prestamo


class BaseTest(unittest.TestCase):
    #Prepara una biblioteca con datos de ejemplo antes de cada prueba.

    def setUp(self) -> None:
        self.biblioteca = Biblioteca()
        self.libro = Libro("Python Básico", "Ana Pérez", "ISBN-1", 1)
        self.revista = Revista("Ciencia Hoy", "Editorial X", 12, "ISSN-1", 1)
        self.ana = Estudiante("E001", "Ana Torres", "Sistemas")
        self.luis = Estudiante("E002", "Luis Rojas", "Civil")
        self.biblioteca.registrar_material(self.libro)
        self.biblioteca.registrar_material(self.revista)
        self.biblioteca.registrar_estudiante(self.ana)
        self.biblioteca.registrar_estudiante(self.luis)


class TestJerarquia(BaseTest):
    def test_clase_abstracta_no_se_puede_instanciar(self) -> None:
        with self.assertRaises(TypeError):
            MaterialBibliografico("Titulo", "COD", 1)  # type: ignore

    def test_herencia(self) -> None:
        self.assertIsInstance(self.libro, MaterialBibliografico)
        self.assertIsInstance(self.revista, MaterialBibliografico)

    def test_plazos_distintos(self) -> None:
        plazo_libro = Prestamo(self.libro, self.ana)
        plazo_revista = Prestamo(self.revista, self.ana)
        self.assertEqual(
            plazo_libro.fecha_estimada - plazo_libro.fecha_prestamo,
            timedelta(days=7))
        self.assertEqual(
            plazo_revista.fecha_estimada - plazo_revista.fecha_prestamo,
            timedelta(days=3))


class TestStock(BaseTest):
    def test_prestar_y_devolver_libro(self) -> None:
        self.assertTrue(self.libro.prestar())
        self.assertTrue(self.libro.esta_prestado())
        self.assertEqual(self.libro.stock_disponible, 0)
        self.assertTrue(self.libro.devolver())
        self.assertFalse(self.libro.esta_prestado())

    def test_no_prestar_sin_stock(self) -> None:
        self.libro.prestar()
        self.assertFalse(self.libro.prestar())

    def test_no_devolver_mas_de_lo_existente(self) -> None:
        self.assertFalse(self.revista.devolver())

    def test_varios_ejemplares(self) -> None:
        libro = Libro("Redes", "B. Autor", "ISBN-2", 2)
        self.biblioteca.registrar_material(libro)
        julia = Estudiante("E003", "Julia Paz", "Industrial")
        self.biblioteca.registrar_estudiante(julia)
        self.assertTrue(self.biblioteca.procesar_prestamo(libro, self.ana))
        self.assertTrue(self.biblioteca.procesar_prestamo(libro, self.luis))
        
        # El tercer estudiante ya no encuentra ejemplares
        self.assertFalse(self.biblioteca.procesar_prestamo(libro, julia))


class TestPolimorfismo(BaseTest):
    def test_procesar_prestamo_funciona_con_ambos_materiales(self) -> None:
        casos = [(self.libro, self.ana), (self.revista, self.luis)]
        for material, estudiante in casos:
            with self.subTest(tipo=material.tipo):
                self.assertTrue(
                    self.biblioteca.procesar_prestamo(material, estudiante))
                self.assertTrue(material.esta_prestado())


class TestExcepciones(BaseTest):
    def test_material_ya_prestado_lanza_excepcion(self) -> None:
        self.biblioteca.procesar_prestamo(self.libro, self.ana)
        with self.assertRaises(MaterialYaPrestadoError):
            Prestamo(self.libro, self.luis).realizar_prestamo()

    def test_material_ya_prestado_devuelve_false(self) -> None:
        self.biblioteca.procesar_prestamo(self.libro, self.ana)
        self.assertFalse(
            self.biblioteca.procesar_prestamo(self.libro, self.luis))
        self.assertIn("ya está prestado", self.biblioteca.ultimo_mensaje)

    def test_material_none(self) -> None:
        self.assertFalse(self.biblioteca.procesar_prestamo(None, self.ana))
        self.assertIn("None", self.biblioteca.ultimo_mensaje)

    def test_estudiante_none(self) -> None:
        self.assertFalse(self.biblioteca.procesar_prestamo(self.libro, None))
        self.assertIn("None", self.biblioteca.ultimo_mensaje)

    def test_prestamo_con_none_lanza_excepcion(self) -> None:
        with self.assertRaises(DatosInvalidosError):
            Prestamo(None, self.ana)  # type: ignore
        with self.assertRaises(DatosInvalidosError):
            Prestamo(self.libro, None)  # type: ignore

    def test_material_o_estudiante_no_registrado(self) -> None:
        otro = Libro("Otro", "Autor", "ISBN-9", 1)
        self.assertFalse(self.biblioteca.procesar_prestamo(otro, self.ana))
        intruso = Estudiante("E999", "Intruso", "Ninguna")
        self.assertFalse(
            self.biblioteca.procesar_prestamo(self.libro, intruso))

    def test_datos_invalidos_en_constructores(self) -> None:
        with self.assertRaises(DatosInvalidosError):
            Libro("", "Autor", "ISBN-3", 1)
        with self.assertRaises(DatosInvalidosError):
            Libro("Titulo", "Autor", "ISBN-3", 0)
        with self.assertRaises(DatosInvalidosError):
            Revista("Titulo", "Editorial", 0, "ISSN-3", 1)
        with self.assertRaises(DatosInvalidosError):
            Estudiante("E010", "", "Carrera")

    def test_codigos_duplicados(self) -> None:
        with self.assertRaises(DatosInvalidosError):
            self.biblioteca.registrar_material(
                Libro("Copia", "Autor", "ISBN-1", 1))
        with self.assertRaises(DatosInvalidosError):
            self.biblioteca.registrar_estudiante(
                Estudiante("E001", "Otro Nombre", "Otra"))


class TestRestricciones(BaseTest):
    def test_prestamo_en_curso_no_bloquea(self) -> None:
        # Dentro del plazo, el estudiante puede pedir otro material
        self.assertTrue(
            self.biblioteca.procesar_prestamo(self.libro, self.ana))
        self.assertTrue(
            self.biblioteca.procesar_prestamo(self.revista, self.ana))

    def test_prestamo_vencido_bloquea(self) -> None:
        hace_10_dias = datetime.now() - timedelta(days=10)
        prestamo = Prestamo(self.libro, self.ana, hace_10_dias)
        prestamo.realizar_prestamo()
        self.assertTrue(prestamo.esta_vencido())
        self.assertFalse(
            self.biblioteca.procesar_prestamo(self.revista, self.ana))
        with self.assertRaises(EstudianteConPendientesError):
            Prestamo(self.revista, self.ana).realizar_prestamo()


class TestDevolucion(BaseTest):
    def test_devolucion_repone_stock_y_finaliza(self) -> None:
        self.biblioteca.procesar_prestamo(self.libro, self.ana)
        self.assertTrue(
            self.biblioteca.procesar_devolucion(self.libro, self.ana))
        self.assertEqual(self.libro.stock_disponible, 1)
        self.assertEqual(self.ana.prestamos[0].estado, Prestamo.FINALIZADO)
        self.assertFalse(self.ana.tiene_prestamos_pendientes())

    def test_devolver_dos_veces_falla(self) -> None:
        self.biblioteca.procesar_prestamo(self.libro, self.ana)
        self.biblioteca.procesar_devolucion(self.libro, self.ana)
        self.assertFalse(
            self.biblioteca.procesar_devolucion(self.libro, self.ana))

    def test_devolver_sin_prestamo_falla(self) -> None:
        self.assertFalse(
            self.biblioteca.procesar_devolucion(self.libro, self.luis))

    def test_estudiante_puede_pedir_otro_tras_devolver(self) -> None:
        self.biblioteca.procesar_prestamo(self.libro, self.ana)
        self.biblioteca.procesar_devolucion(self.libro, self.ana)
        self.assertTrue(
            self.biblioteca.procesar_prestamo(self.revista, self.ana))

    def test_devolucion_con_retraso(self) -> None:
        hace_10_dias = datetime.now() - timedelta(days=10)
        prestamo = Prestamo(self.libro, self.ana, hace_10_dias)
        prestamo.realizar_prestamo()
        prestamo.finalizar()
        self.assertEqual(prestamo.dias_retraso(), 3)   # 10 días - 7 de plazo

    def test_finalizar_dos_veces_lanza_excepcion(self) -> None:
        prestamo = Prestamo(self.libro, self.ana)
        prestamo.realizar_prestamo()
        prestamo.finalizar()
        with self.assertRaises(DatosInvalidosError):
            prestamo.finalizar()


class TestEncapsulacionYConsultas(BaseTest):
    def test_properties_de_solo_lectura(self) -> None:
        with self.assertRaises(AttributeError):
            self.libro.stock_disponible = 99  # type: ignore
        with self.assertRaises(AttributeError):
            self.libro.isbn = "OTRO"  # type: ignore

    def test_setter_valida_datos(self) -> None:
        with self.assertRaises(DatosInvalidosError):
            self.libro.titulo = "   "
        self.libro.titulo = "Nuevo título"
        self.assertEqual(self.libro.titulo, "Nuevo título")

    def test_consultas(self) -> None:
        self.assertIn("DISPONIBLE", self.biblioteca.estado_material("ISBN-1"))
        self.biblioteca.procesar_prestamo(self.libro, self.ana)
        self.assertIn("PRESTADO", self.biblioteca.estado_material("ISBN-1"))
        self.assertIn("Python Básico",
                      self.biblioteca.historial_estudiante("E001"))
        self.assertEqual(self.biblioteca.estado_material("XXX"),
                         "Material no encontrado.")
        self.assertEqual(self.biblioteca.historial_estudiante("XXX"),
                         "Estudiante no registrado.")


class TestListarEstudiantes(BaseTest):
    def test_lista_vacia(self) -> None:
        self.assertEqual(Biblioteca().listar_estudiantes(),
                         "No hay estudiantes registrados.")

    def test_lista_todos_los_estudiantes(self) -> None:
        texto = self.biblioteca.listar_estudiantes()
        self.assertIn("E001", texto)
        self.assertIn("Luis Rojas", texto)
        self.assertNotIn("PENDIENTES", texto)

    def test_marca_estudiantes_con_pendientes(self) -> None:
        self.biblioteca.procesar_prestamo(self.libro, self.ana)
        lineas = self.biblioteca.listar_estudiantes().splitlines()
        self.assertIn("PENDIENTES", lineas[0])      # Ana
        self.assertNotIn("PENDIENTES", lineas[1])   # Luis


class TestDataset(unittest.TestCase):
    def setUp(self) -> None:
        self.biblioteca = Biblioteca()
        self.resumen = cargar_datos(self.biblioteca)

    def test_resumen_y_cantidades(self) -> None:
        self.assertIn("6 materiales", self.resumen)
        self.assertIn("4 estudiantes", self.resumen)
        self.assertEqual(len(self.biblioteca.listar_estudiantes()
                             .splitlines()), 4)

    def test_tipos_de_material_cargados(self) -> None:
        self.assertIsInstance(self.biblioteca.buscar_material("ISBN-001"),
                              Libro)
        self.assertIsInstance(self.biblioteca.buscar_material("ISSN-1001"),
                              Revista)

    def test_prestamos_del_dataset(self) -> None:
        ana = self.biblioteca.buscar_estudiante("E001")
        luis = self.biblioteca.buscar_estudiante("E002")
        marta = self.biblioteca.buscar_estudiante("E003")
        carlos = self.biblioteca.buscar_estudiante("E004")
        self.assertTrue(ana.tiene_prestamos_pendientes())
        self.assertTrue(luis.prestamos[0].esta_vencido())
        self.assertFalse(marta.tiene_prestamos_pendientes())
        self.assertEqual(len(marta.prestamos), 1)       # historial
        self.assertFalse(carlos.tiene_prestamos_pendientes())
        self.assertTrue(self.biblioteca.buscar_material("ISBN-002")
                        .esta_prestado())

    def test_dataset_permite_probar_restricciones(self) -> None:
        carlos = self.biblioteca.buscar_estudiante("E004")
        luis = self.biblioteca.buscar_estudiante("E002")
        calculo = self.biblioteca.buscar_material("ISBN-002")
        derecho = self.biblioteca.buscar_material("ISBN-004")
        estructuras = self.biblioteca.buscar_material("ISBN-003")
        ana = self.biblioteca.buscar_estudiante("E001")
        # Material ya prestado
        self.assertFalse(self.biblioteca.procesar_prestamo(calculo, carlos))
        # Estudiante con préstamo vencido
        self.assertFalse(self.biblioteca.procesar_prestamo(derecho, luis))
        # Préstamo en curso (no vencido): puede pedir otro material
        self.assertTrue(
            self.biblioteca.procesar_prestamo(estructuras, ana))
        # Caso válido
        self.assertTrue(self.biblioteca.procesar_prestamo(derecho, carlos))


if __name__ == "__main__":
    unittest.main(verbosity=2)