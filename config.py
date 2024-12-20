from pathlib import Path

# Rutas de archivos
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'datos_opcua.db'
CSV_PATH = BASE_DIR / 'opcua_data.csv'

# Configuración OPC UA
OPC_UA_CONFIG = {
    'url': 'opc.tcp://172.19.89.154:4840',
    'username': 'admin',
    'password': 'admin'
}

# Tiempos de muestreo
SAMPLING_TIME = 0.3  # 300ms
PUBLISHING_TIME = 0.5  # 500ms

# Configuración de base de datos
DB_CONFIG = {
    'table_name': 'tags',
    'index_name': 'idx_tags_fecha'
}

# Configuración del dashboard
DASH_CONFIG = {
    'update_interval': 2500,  # ms
    'default_limit': 100
}
