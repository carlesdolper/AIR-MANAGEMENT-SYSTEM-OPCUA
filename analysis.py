import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

class Analyzer:
    def __init__(self):
        # Usar Path para manejar rutas de manera segura
        self.db_path = Path(__file__).parent / 'data' / 'datos_opcua.db'
        
        # Asegurarse de que el directorio data existe
        data_dir = Path(__file__).parent / 'data'
        data_dir.mkdir(exist_ok=True)
        
        # Verificar si la base de datos existe
        if not self.db_path.exists():
            print(f"Error: Base de datos no encontrada en {self.db_path}")
            return

    def get_data(self, variable, limit=2000):
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
                SELECT 
                    datetime(fecha_hora) as fecha_hora,
                    valor 
                FROM tags 
                WHERE nombre = ? 
                ORDER BY fecha_hora ASC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(variable, limit))
            df['timestamp'] = pd.to_datetime(df['fecha_hora'])
            conn.close()
            return df
        except sqlite3.OperationalError as e:
            print(f"Error al conectar con la base de datos: {e}")
            return pd.DataFrame()

    def analyze_cycle_pattern(self, window_size=2000, max_gap=300):
        try:
            # Obtener datos de flujo
            df = self.get_data("AMS00_PF3A_Flow", limit=window_size)
            if df.empty:
                print("\nNo hay datos disponibles para analizar")
                return []
                
            print(f"\nAnalizando {len(df)} puntos de datos")
            df['timestamp'] = pd.to_datetime(df['fecha_hora'])
            df = df.sort_values('timestamp')
            
            # Detectar gaps temporales
            df['time_diff'] = df['timestamp'].diff().dt.total_seconds()
            df['is_gap'] = df['time_diff'] > max_gap
            
            # Calcular estadísticas base excluyendo gaps
            mean_flow = df[~df['is_gap']]['valor'].mean()
            std_flow = df[~df['is_gap']]['valor'].std()
            
            # Detectar cambios significativos en el flujo
            df['flow_change'] = df['valor'].diff()
            df['is_significant'] = abs(df['flow_change']) > std_flow/2
            
            # Identificar secuencias de operaciones
            cycle_data = []
            current_sequence = []
            sequence_start = None
            has_gap = False
            
            for idx, row in df.iterrows():
                if row['is_gap'] and sequence_start is not None:
                    has_gap = True
                    continue
                    
                if row['is_significant']:
                    if sequence_start is None:
                        sequence_start = row['timestamp']
                        has_gap = False
                    current_sequence.append({
                        'timestamp': row['timestamp'],
                        'flow': row['valor'],
                        'change': row['flow_change'],
                        'has_gap': has_gap
                    })
                elif len(current_sequence) > 0 and row['valor'] < mean_flow/4:
                    if len(current_sequence) >= 3:  # Mínimo 3 cambios para considerar un ciclo
                        cycle_data.append({
                            'start_time': sequence_start,
                            'end_time': row['timestamp'],
                            'duration': (row['timestamp'] - sequence_start).total_seconds(),
                            'sequence': current_sequence,
                            'peak_flow': max(point['flow'] for point in current_sequence),
                            'has_interruption': has_gap
                        })
                    current_sequence = []
                    sequence_start = None
                    has_gap = False
            
            if cycle_data:
                print("\nAnálisis de Ciclos:")
                for i, cycle in enumerate(cycle_data[:5], 1):
                    print(f"\nCiclo {i}:")
                    print(f"Duración: {cycle['duration']:.2f} segundos")
                    print(f"Flujo máximo: {cycle['peak_flow']:.2f}")
                    print(f"Cambios significativos: {len(cycle['sequence'])}")
                    if cycle['has_interruption']:
                        print("¡Ciclo con interrupción detectada!")
                print(f"\nTotal de ciclos detectados: {len(cycle_data)}")
                print(f"Ciclos con interrupciones: {sum(1 for c in cycle_data if c['has_interruption'])}")
            else:
                print("\nNo se detectaron ciclos en los datos analizados")
            
            return cycle_data
            
        except Exception as e:
            print(f"Error en análisis de ciclos: {e}")
            return []

    def analyze_efficiency(self, flow_var="AMS00_PF3A_Flow", pressure_var="AMS00_PF3A_Pressure", limit=1000):
        flow_df = self.get_data(flow_var, limit=limit)
        pressure_df = self.get_data(pressure_var, limit=limit)
        
        # Combinar datos de flujo y presión
        merged_df = pd.merge(
            flow_df, 
            pressure_df, 
            on='fecha_hora', 
            suffixes=('_flow', '_pressure')
        )
        
        # Calcular eficiencia
        merged_df['efficiency'] = merged_df['valor_flow'] / merged_df['valor_pressure']
        return merged_df

    def detect_anomalies(self, variable, threshold=2):
        df = self.get_data(variable)
        mean = df['valor'].mean()
        std = df['valor'].std()
        anomalies = df[abs(df['valor'] - mean) > threshold * std]
        
        if not anomalies.empty:
            print(f"\nAnomalías detectadas para {variable}:")
            for _, row in anomalies.iterrows():
                print(f"Tiempo: {row['fecha_hora']}, Valor: {row['valor']:.3f}")

    def visualize_patterns(self, window_size=2000):
        try:
            # Obtener datos de flujo
            df = self.get_data("AMS00_PF3A_Flow", limit=window_size)
            df['timestamp'] = pd.to_datetime(df['fecha_hora'])
            df = df.sort_values('timestamp')
            
            # Detectar cambios significativos
            df['flow_change'] = df['valor'].diff()
            mean_flow = df['valor'].mean()
            std_flow = df['valor'].std()
            
            # Identificar ciclos
            cycles = []
            current_cycle = []
            cycle_start = None
            
            for idx, row in df.iterrows():
                if row['valor'] > mean_flow + std_flow/2 and cycle_start is None:
                    cycle_start = row['timestamp']
                    current_cycle = [(row['timestamp'], row['valor'])]
                elif cycle_start is not None:
                    current_cycle.append((row['timestamp'], row['valor']))
                    if row['valor'] < mean_flow/4:
                        if len(current_cycle) > 10:  # Mínimo de puntos para considerar un ciclo
                            cycles.append(current_cycle)
                        current_cycle = []
                        cycle_start = None
            #
            if cycles:
                        print("\nPatrones de Ciclos Detectados:")
                        for i, cycle in enumerate(cycles[:5], 1):
                            times, values = zip(*cycle)
                            duration = (times[-1] - times[0]).total_seconds()
                            max_flow = max(values)
                            print(f"\nCiclo {i}:")
                            print(f"Duración: {duration:.2f} segundos")
                            print(f"Flujo máximo: {max_flow:.2f}")
                            print(f"Número de cambios significativos: {sum(abs(np.diff(values)) > std_flow)}")
                        print(f"\nTotal de ciclos detectados: {len(cycles)}")
            else:
                print("\nNo se detectaron patrones de ciclos en los datos analizados")
                    
            return cycles
        
        except Exception as e:
            print(f"Error en visualización de patrones: {e}")
            return []

if __name__ == "__main__":
    analyzer = Analyzer()
    print("\nAnalizando patrones de ciclos...")
    # Usar ambos métodos para comparar
    patterns = analyzer.analyze_cycle_pattern()
    cycles = analyzer.visualize_patterns()

    
    # Análisis de variables
    variables = [
        "AMS00_PF3A_AccumFlow",
        "AMS00_PF3A_Flow", 
        "AMS00_PF3A_Temperature",
        "AMS00_PF3A_Pressure",
        "AMS00_ITV_Value"
    ]
    
    for var in variables:
        analyzer.detect_anomalies(var)


