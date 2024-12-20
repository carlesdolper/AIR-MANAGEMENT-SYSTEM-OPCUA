from opcua import Client
from tags import tag_list
import time
import keyboard
import sqlite3
from datetime import datetime
import csv
from pathlib import Path
from config import DB_PATH, CSV_PATH, OPC_UA_CONFIG, SAMPLING_TIME, PUBLISHING_TIME

# Crear un subdirectorio llamado "data"
data_dir = Path(__file__).parent
data_dir.mkdir(exist_ok=True)

# Rutas para la base de datos y csv
#db_path = DB_PATH
#csv_path = CSV_PATH

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect(DB_PATH)

# Crear un cursor
cursor = conn.cursor()

# Crear la tabla
cursor.execute('''
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    valor REAL,
    fecha_hora TEXT NOT NULL,
    CHECK (datetime(fecha_hora) IS NOT NULL)
)''')

# Crear el índice en una sentencia separada
cursor.execute('''
CREATE INDEX IF NOT EXISTS idx_tags_fecha ON tags(fecha_hora)
''')


# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

def conectar_servidor_opcua(url, nombre_usuario, contrasena):
    cliente = Client(url)
    try:
        cliente.set_user(nombre_usuario)
        cliente.set_password(contrasena)
        cliente.connect()
        #print("Conectado al servidor OPC UA")
        return cliente
    except Exception as e:
        print(f"Error al conectar al servidor OPC UA: {e}")
        return None

def leer_tags_opcua(cliente, tags):
    try:
        start_time = time.time()
        
        # Lectura en bloque optimizada
        nodes = [cliente.get_node(f"ns={tag.namespace};i={tag.nodeid}") for tag in tags]
        values = cliente.get_values(nodes)
        
        # Actualizar valores
        for tag, value in zip(tags, values):
            tag.value = value * tag.scale_factor
        
        # Ajuste dinámico del tiempo de espera
        elapsed_time = time.time() - start_time
        sleep_time = max(0, SAMPLING_TIME - elapsed_time)
        time.sleep(sleep_time)
        
        return tags
    except Exception as e:
        print(f"Error durante la lectura: {e}")
        return []

def insertar_datos(datos_tags):
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Insertar los datos en la tabla
        cursor.executemany(
            "INSERT INTO tags (nombre, valor, fecha_hora) VALUES (?, ?, ?)",
            datos_tags
        )

        # Guardar los cambios y cerrar la conexión
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error al insertar datos en la base de datos: {e}")

# Conectar al servidor OPC UA
cliente = conectar_servidor_opcua(OPC_UA_CONFIG['url'], OPC_UA_CONFIG['username'], OPC_UA_CONFIG['password'])

if cliente:
    try:
        #Create CSV file and write header
        with open(CSV_PATH, 'w', newline='') as csvfile:
            fieldnames =['Timestamp'] + [tag.tag_name for tag in tag_list]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

        while True:
            try:
                cycle_start = time.time()
                # Leer los datos del servidor OPC UA
                tags_actualizados = leer_tags_opcua(cliente, tag_list)
                if tags_actualizados:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                # Inicializar estructuras para CSV y SQL
                row_csv = {'Timestamp': timestamp}  # Diccionario para CSV
                datos_sql = []  # Lista de tuplas para SQL

                # Procesar cada tag
                for tag in tags_actualizados:
                    row_csv[tag.tag_name] = tag.value  # Agregar al diccionario del CSV
                    datos_sql.append((tag.tag_name, tag.value, timestamp))  # Agregar a la lista para SQL
            
                cycle_time = time.time() - cycle_start
                wait_time = max(0, PUBLISHING_TIME - cycle_time)
                time.sleep(wait_time)
        
            except Exception as e:
                print(f"Error en el ciclo principal: {e}")

            # Escribir al archivo CSV (una fila por lectura)
            with open(CSV_PATH, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=row_csv.keys())
                writer.writerow(row_csv)

            # Insertar los datos en la base de datos (en bloque)
            insertar_datos(datos_sql)
            
            # Salir si se presiona la tecla 'Esc'
            if keyboard.is_pressed('esc'):
                break

    except KeyboardInterrupt:
        print("Interrupción por teclado.")
    
    finally:
        cliente.disconnect()
