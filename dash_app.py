import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import sqlite3
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# Crear la aplicación Dash con Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Función para obtener las variables disponibles en la base de datos
def obtener_variables():
    try:
        conn = sqlite3.connect('datos_opcua.db')  # Ruta a tu base de datos
        query = "SELECT DISTINCT nombre FROM tags"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df['nombre'].tolist()
    except Exception as e:
        print(f"Error al obtener variables: {e}")
        return []

# Función para obtener los datos de una variable específica dentro de un rango de fechas y horas
def obtener_datos(variable, fecha_inicio=None, fecha_fin=None, limite=100):
    try:
        conn = sqlite3.connect('datos_opcua.db')
        query = """
            SELECT 
                fecha_hora,
                valor 
            FROM tags 
            WHERE nombre = ? 
            AND datetime(fecha_hora) IS NOT NULL
        """
        if fecha_inicio and fecha_fin:
            query += " AND fecha_hora BETWEEN ? AND ?"
            params = (variable, fecha_inicio, fecha_fin)
        else:
            params = (variable,)
        
        query += f" ORDER BY fecha_hora DESC LIMIT {limite}"
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return pd.DataFrame()


# Layout del dashboard
app.layout = dbc.Container([
    #Titulo
    dbc.Row([
        dbc.Col(html.H1("Dashboard OPC UA BASE EXA1-40-EN : AIR MANAGEMENT SYSTEM (AMS)", className="text-center bg-primary text-white p-2"), width=12)
    ]),
    #Seleccionar Variables y estadisiticas / Fechas y limites
    dbc.Row([
        dbc.Col([
            html.Label("Selecciona una variable:", className="mt-3"),
            dcc.Dropdown(
                id='dropdown-variable',
                options=[{'label': var, 'value': var} for var in obtener_variables()],
                value=None,
                placeholder="Selecciona una variable"
            ),
            html.Label("Selecciona una segunda variable (opcional):", className="mt-3"),
            dcc.Dropdown(
                id='dropdown-variable2',
                options=[{'label': var, 'value': var} for var in obtener_variables()],
                value=None,
                placeholder="Selecciona otra variable"
            ),
            html.Div(id='estadisticas-resumen', className="mt-4")
        ], width=6),
        dbc.Col([
            html.Label("Selecciona el rango de fechas y horas:", className="mt-3"),
            html.Div([
                dbc.Input(id='datetime-inicio', type='datetime-local', className="mb-2"),
                dbc.Input(id='datetime-fin', type='datetime-local')
            ]),
            html.Label("Límite de puntos:", className="mt-3"),
            dbc.Input(id='limite-puntos', type='number', value=100, min=1)  # Valor por defecto: 100
        ], width=6)
    ]),
    #Grafico
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-lineal'), width=12)
    ]),
    #Pausar/Reanudar
    dbc.Row([
        dbc.Col(dbc.Button("Pausar Actualización", id="boton-pausa", color="danger", className="mt-4"), width=12)
    ]),
    
    dcc.Interval(id='intervalo-actualizacion', interval=2500, n_intervals=0)  # Actualización cada 2 segundos
], fluid=True)

# Callback para actualizar el gráfico lineal basado en la selección del dropdown y el rango de fechas/horas
@app.callback(
    Output('grafico-lineal', 'figure'),
    [Input('dropdown-variable', 'value'),
     Input('dropdown-variable2', 'value'),
     Input('datetime-inicio', 'value'),
     Input('datetime-fin', 'value'),
     Input('limite-puntos', 'value'),
     Input('intervalo-actualizacion', 'n_intervals')]
)
def actualizar_grafico_lineal(variable_seleccionada, variable_seleccionada2, datetime_inicio, datetime_fin, limite_puntos, n):
    fig = go.Figure()

    if variable_seleccionada:
        df = obtener_datos(variable_seleccionada, datetime_inicio, datetime_fin, limite_puntos)
        if not df.empty:
            fig.add_trace(go.Scatter(x=df['fecha_hora'], y=df['valor'], mode='lines+markers', name=variable_seleccionada))

    if variable_seleccionada2:  #  Condición separada para la segunda variable
        df2 = obtener_datos(variable_seleccionada2, datetime_inicio, datetime_fin, limite_puntos)
        if not df2.empty:
            fig.add_trace(go.Scatter(x=df2['fecha_hora'], y=df2['valor'], mode='lines+markers', name=variable_seleccionada2, yaxis='y2'))

    fig.update_layout(
        xaxis_title="Fecha y Hora",
        yaxis_title="Valor Variable 1",
        yaxis2=dict(
            title="Valor Variable 2",
            overlaying='y',
            side='right'
        )
    )

    return fig

# Callback para mostrar estadísticas resumen
@app.callback(
    Output('estadisticas-resumen', 'children'),
    [Input('dropdown-variable', 'value'),
     Input('dropdown-variable2', 'value'),
     Input('datetime-inicio', 'value'),
     Input('datetime-fin', 'value'),
     Input('limite-puntos', 'value')]
)
def calcular_estadisticas(variable_seleccionada, variable_seleccionada2, datetime_inicio, datetime_fin, limite_puntos):
    resultados = dbc.Row([])  # Usar dbc.Row

    if variable_seleccionada:
        df = obtener_datos(variable_seleccionada, datetime_inicio, datetime_fin, limite_puntos)
        if not df.empty:
            resultados.children.append(dbc.Col([  # Envolver en dbc.Col
                html.H5(f"Estadísticas para {variable_seleccionada}:"),
                html.P(f"Promedio: {df['valor'].mean():.2f}", className="small"),
                html.P(f"Máximo: {df['valor'].max():.2f}", className="small"),
                html.P(f"Mínimo: {df['valor'].min():.2f}", className="small"),
                html.P(f"Desviación estándar: {df['valor'].std():.2f}", className="small")
            ], width=6))

    if variable_seleccionada2:
        df2 = obtener_datos(variable_seleccionada2, datetime_inicio, datetime_fin, limite_puntos)
        if not df2.empty:
            resultados.children.append(dbc.Col([  # Envolver en dbc.Col
                html.H5(f"Estadísticas para {variable_seleccionada2}:"),
                html.P(f"Promedio: {df2['valor'].mean():.2f}", className="small"),
                html.P(f"Máximo: {df2['valor'].max():.2f}", className="small"),
                html.P(f"Mínimo: {df2['valor'].min():.2f}", className="small"),
                html.P(f"Desviación estándar: {df2['valor'].std():.2f}", className="small")
            ], width=6))

    return resultados

# Callback para pausar/reanudar el refresco de datos con cambio de color y texto del botón
@app.callback(
    [Output('intervalo-actualizacion', 'disabled'),
     Output('boton-pausa', 'children'),
     Output('boton-pausa', 'color')],
    [Input('boton-pausa', 'n_clicks')],
    [State('intervalo-actualizacion', 'disabled')]
)
def pausar_reanudar_refresco(n_clicks, esta_pausado):
    if n_clicks is None or n_clicks == 0:
        raise dash.exceptions.PreventUpdate
    
    nuevo_estado = not esta_pausado  # Cambiar el estado actual
    texto_boton = "Reanudar Actualización" if nuevo_estado else "Pausar Actualización"
    color_boton = "success" if nuevo_estado else "danger"
    
    return nuevo_estado, texto_boton, color_boton

# Ejecutar la aplicación Dash
if __name__ == '__main__':
    app.run_server(debug=True)