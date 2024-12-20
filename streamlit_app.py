import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Título de la aplicación Streamlit
st.title("Visualización de Datos OPC UA")

# Función para obtener los datos desde la base de datos SQLite
def obtener_datos():
    conn = sqlite3.connect('data/datos_opcua.db')  # Ruta a tu base de datos
    query = "SELECT * FROM tags ORDER BY fecha_hora DESC LIMIT 100"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Mostrar los datos en una tabla interactiva
st.subheader("Datos Recientes")
df = obtener_datos()
st.dataframe(df)

# Crear un gráfico interactivo con Plotly si hay datos disponibles
if not df.empty:
    fig = px.line(df, x='fecha_hora', y='valor', color='nombre', title="Datos en Tiempo Real")
    st.plotly_chart(fig)
else:
    st.write("No hay datos disponibles.")
