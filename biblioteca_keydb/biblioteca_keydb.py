import redis
import json
import uuid
from dotenv import load_dotenv
import os

# -------------------------------------------
# CARGAR VARIABLES DE ENTORNO (.env)
# -------------------------------------------
load_dotenv()

REDIS_HOST = os.getenv("KEYDB_HOST", "localhost")
REDIS_PORT = int(os.getenv("KEYDB_PORT", 6379))
REDIS_PASSWORD = os.getenv("KEYDB_PASSWORD", None)

# -------------------------------------------
# CONEXIÓN A KEYDB/REDIS
# -------------------------------------------
try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True  # Para que devuelva strings
    )

    # Probar conexión
    r.ping()
    print("✔ Conectado correctamente a KeyDB/Redis.\n")

except Exception as e:
    print("❌ Error de conexión:", e)
    exit()


# -------------------------------------------
# CRUD OPERATIONS
# -------------------------------------------

def generar_id():
    """Genera un ID único para cada libro."""
    return str(uuid.uuid4())


def agregar_libro():
    titulo = input("Ingrese el título del libro: ")
    autor = input("Ingrese el autor del libro: ")
    genero = input("Ingrese el género del libro: ")
    estado = input("Estado del libro (leído/no leído): ")

    libro_id = generar_id()

    libro = {
        "id": libro_id,
        "titulo": titulo,
        "autor": autor,
        "genero": genero,
        "estado": estado
    }

    try:
        r.set(f"libro:{libro_id}", json.dumps(libro))
        print("📌 Libro agregado exitosamente.\n")
    except Exception as e:
        print("❌ Error al guardar:", e)


def listar_libros():
    try:
        keys = r.scan_iter("libro:*")
        encontrados = False

        print("\n📚 Lista de libros registrados:")
        for key in keys:
            libro = json.loads(r.get(key))
            print(f"ID: {libro['id']} | Título: {libro['titulo']} | Autor: {libro['autor']} | Género: {libro['genero']} | Estado: {libro['estado']}")
            encontrados = True
        
        if not encontrados:
            print("⚠ No hay libros registrados.\n")
        else:
            print()

    except Exception as e:
        print("❌ Error al listar:", e)


def buscar_libros():
    criterio = input("Buscar por (titulo/autor/genero): ").lower()
    valor = input(f"Ingrese el {criterio}: ")

    if criterio not in ["titulo", "autor", "genero"]:
        print("❌ Criterio inválido.\n")
        return

    encontrados = False

    for key in r.scan_iter("libro:*"):
        libro = json.loads(r.get(key))
        if valor.lower() in libro[criterio].lower():
            print(f"ID: {libro['id']} | Título: {libro['titulo']} | Autor: {libro['autor']} | Género: {libro['genero']} | Estado: {libro['estado']}")
            encontrados = True
    
    if not encontrados:
        print("⚠ No se encontraron coincidencias.\n")
    else:
        print()


def actualizar_libro():
    listar_libros()
    
    id_libro = input("Ingrese el ID del libro a actualizar: ")
    key = f"libro:{id_libro}"

    if not r.exists(key):
        print("❌ Libro no encontrado.\n")
        return

    libro = json.loads(r.get(key))

    print("Deje en blanco si no desea modificar un campo.")
    nuevo_titulo = input("Nuevo título: ")
    nuevo_autor = input("Nuevo autor: ")
    nuevo_genero = input("Nuevo género: ")
    nuevo_estado = input("Nuevo estado (leído/no leído): ")

    if nuevo_titulo: libro["titulo"] = nuevo_titulo
    if nuevo_autor: libro["autor"] = nuevo_autor
    if nuevo_genero: libro["genero"] = nuevo_genero
    if nuevo_estado: libro["estado"] = nuevo_estado

    try:
        r.set(key, json.dumps(libro))
        print("✔ Libro actualizado correctamente.\n")
    except Exception as e:
        print("❌ Error al actualizar:", e)


def eliminar_libro():
    listar_libros()
    
    id_libro = input("Ingrese el ID del libro a eliminar: ")
    key = f"libro:{id_libro}"

    if not r.exists(key):
        print("❌ Libro no encontrado.\n")
        return

    try:
        r.delete(key)
        print("🗑 Libro eliminado correctamente.\n")
    except Exception as e:
        print("❌ Error al eliminar:", e)


# -------------------------------------------
# MENÚ PRINCIPAL
# -------------------------------------------
def menu():
    while True:
        print("📌 Menú de Biblioteca KeyDB/Redis")
        print("1. Agregar libro")
        print("2. Listar libros")
        print("3. Buscar libros")
        print("4. Actualizar libro")
        print("5. Eliminar libro")
        print("6. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            agregar_libro()
        elif opcion == "2":
            listar_libros()
        elif opcion == "3":
            buscar_libros()
        elif opcion == "4":
            actualizar_libro()
        elif opcion == "5":
            eliminar_libro()
        elif opcion == "6":
            print("👋 Saliendo del sistema...")
            break
        else:
            print("⚠ Opción inválida. Intente nuevamente.\n")


menu()
