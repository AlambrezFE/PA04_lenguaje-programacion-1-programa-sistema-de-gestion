# Sistema de Gestión para Biblioteca Universitaria

Programa de consola en Python para gestionar libros, revistas, estudiantes y
préstamos.

## Requisitos

- Python 3.8 o superior
- No necesita instalar librerías externas (por eso no hay `requirements.txt`)

## Ejecución

1. Descargue todos los archivos en una misma carpeta.
2. Abra una terminal en esa carpeta.
3. Ejecute:

```bash
python main.py
```

(En Linux/macOS puede ser `python3 main.py`.)

Al iniciar, el programa carga automáticamente los datos de ejemplo de
`datos.json` y muestra el menú.

## Menú

| Opción | Acción |
|--------|--------|
| 1 | Registrar libro |
| 2 | Registrar revista |
| 3 | Registrar estudiante |
| 4 | Prestar material |
| 5 | Devolver material |
| 6 | Consultar estado de un material |
| 7 | Historial de un estudiante |
| 8 | Listar catálogo |
| 9 | Listar estudiantes |
| 0 | Salir |

## Datos de ejemplo para probar

- Estudiantes: `E001` a `E004`
- Libros: `ISBN-001` a `ISBN-004`; revistas: `ISSN-1001` y `ISSN-1002`
- `E001` tiene un préstamo en curso, `E002` tiene uno **vencido** y `E003`
  solo tiene historial. `E004` no tiene préstamos.
- `ISBN-002` (Cálculo I) ya está prestado.
- Pruebe prestar `ISBN-004` a `E004` (válido) y a `E002` (rechazado).

Para empezar sin datos, borre o renombre `datos.json`.

## Estructura

| Archivo | Contenido |
|---------|-----------|
| `main.py` | Único archivo que se ejecuta |
| `menu.py` | Menú e interacción con el usuario |
| `biblioteca.py` | Clase `Biblioteca` (reglas del sistema) |
| `material.py` | `MaterialBibliografico` (abstracta), `Libro`, `Revista` |
| `estudiante.py` | Clase `Estudiante` |
| `prestamo.py` | Clase `Prestamo` |
| `excepciones.py` | Excepciones personalizadas |
| `validaciones.py` | Validación de textos |
| `datos.py` / `datos.json` | Carga y contenido del dataset de ejemplo |
| `test_sistema.py` | Pruebas automáticas |
| `[invalido]_prueba_sistema_biblioteca_ver1` | Prueba del programa de la parte 2 de la evaluacion |
| `[invalido]_prueba_sistema_biblioteca_ver2` | Pruebas del programa de la parte 3 de la evaluacion |


## Pruebas

```bash
python test_sistema.py
```

## Postdata
para modificar algun dato de prueba que viene por defecto, puede hacerlo en `datos.json` y poner los datos que le sean comodos, `datos.py` solo estructura los datos que estan en formato json para que el programa pueda leerlos.