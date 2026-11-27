from dash import Dash, Input, Output, dcc, html
from pathlib import Path
import pandas as pd
import plotly.express as px

app = Dash(__name__)

# Colores
FONDO = "#F4F6F9"
TINTA = "#243247"
GRIS = "#68778D"
BLANCO = "#FFFFFF"

# Estilos
ESTILO_PAGINA = {
    "backgroundColor": FONDO,
    "minHeight": "100vh",
    "padding": "30px",
    "fontFamily": "Arial"
}

ESTILO_FILA = {
    "display": "flex",
    "gap": "20px",
    "marginBottom": "25px",
    "flexWrap": "wrap"
}

ESTILO_TARJETA = {
    "backgroundColor": BLANCO,
    "padding": "20px",
    "borderRadius": "10px",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
    "flex": "1",
    "minWidth": "180px"
}

ESTILO_FILTRO = {"flex": "1", "minWidth": "220px"}

# Cargar datos
RUTA = Path(__file__).parent.parent / "datos" / "ventas.csv"
datos = pd.read_csv(RUTA, parse_dates=["fecha"])

SUCURSALES = sorted(datos["sucursal"].unique())
CATEGORIAS = sorted(datos["categoria"].unique())
FECHA_MIN = datos["fecha"].min().date()
FECHA_MAX = datos["fecha"].max().date()


# Tarjeta KPI: solo tiene id, el callback le pone el valor
def tarjeta(titulo, id_valor):
    return html.Div([
        html.P(titulo, style={"color": GRIS, "margin": "0"}),
        html.H2(id=id_valor, style={"color": TINTA, "marginBottom": "0"})
    ], style=ESTILO_TARJETA)


# Layout
app.layout = html.Div([

    html.H1("Tablero de ventas", style={"color": TINTA}),

    html.P(
        "Abarrotera del Bajío - enero a octubre 2026",
        style={"color": GRIS}
    ),

    # Filtros
    html.Div([

        html.Div([
            html.Label("Sucursal", style={"fontWeight": "600"}),
            dcc.Dropdown(
                id="filtro-sucursal",
                options=SUCURSALES,
                value=SUCURSALES,
                multi=True,
            ),
        ], style=ESTILO_FILTRO),

        html.Div([
            html.Label("Categoría", style={"fontWeight": "600"}),
            dcc.Dropdown(
                id="filtro-categoria",
                options=CATEGORIAS,
                value=CATEGORIAS,
                multi=True,
            ),
        ], style=ESTILO_FILTRO),

        html.Div([
            html.Label("Período", style={"fontWeight": "600"}),
            html.Div(
                dcc.DatePickerRange(
                    id="filtro-periodo",
                    min_date_allowed=FECHA_MIN,
                    max_date_allowed=FECHA_MAX,
                    start_date=FECHA_MIN,
                    end_date=FECHA_MAX,
                    display_format="DD/MM/YYYY",
                ),
            ),
        ], style=ESTILO_FILTRO),

    ], style=ESTILO_FILA),

    # Aviso de selección vacía (lo llena el callback solo cuando hace falta)
    html.Div(id="aviso-vacio"),

    # Indicadores
    html.Div([
        tarjeta("Ingresos totales", "kpi-ingresos"),
        tarjeta("Unidades vendidas", "kpi-unidades"),
        tarjeta("Importe promedio", "kpi-promedio"),
        tarjeta("Días con venta", "kpi-dias"),
    ], style=ESTILO_FILA),

    # Gráfica ancha
    html.Div(
        dcc.Graph(id="grafica-linea"),
        style={**ESTILO_TARJETA, "marginBottom": "25px"}
    ),

    # Dos gráficas lado a lado
    html.Div([
        html.Div(dcc.Graph(id="grafica-categoria"), style=ESTILO_TARJETA),
        html.Div(dcc.Graph(id="grafica-sucursal"), style=ESTILO_TARJETA),
    ], style=ESTILO_FILA),

], style=ESTILO_PAGINA)


# Un solo callback para todo el tablero.
# Orden de los Input = orden de los argumentos de la función.
# Orden de los Output = orden de los valores del return.
@app.callback(
    Output("kpi-ingresos", "children"),
    Output("kpi-unidades", "children"),
    Output("kpi-promedio", "children"),
    Output("kpi-dias", "children"),
    Output("grafica-linea", "figure"),
    Output("grafica-categoria", "figure"),
    Output("grafica-sucursal", "figure"),
    Output("aviso-vacio", "children"),
    Input("filtro-sucursal", "value"),
    Input("filtro-categoria", "value"),
    Input("filtro-periodo", "start_date"),
    Input("filtro-periodo", "end_date"),
)
def actualizar(sucursales, categorias, inicio, fin):
    # Si el usuario borra todo, el value puede llegar vacío o como None
    sucursales = sucursales or []
    categorias = categorias or []
    inicio = pd.to_datetime(inicio) if inicio else pd.Timestamp(FECHA_MIN)
    fin = pd.to_datetime(fin) if fin else pd.Timestamp(FECHA_MAX)

    filtrados = datos[
        datos["sucursal"].isin(sucursales)
        & datos["categoria"].isin(categorias)
        & datos["fecha"].between(inicio, fin)
    ]

    # Salida anticipada: mismos 8 valores que el return normal
    if filtrados.empty:
        vacia = px.scatter(title="Sin datos para los filtros seleccionados")
        aviso = html.Div(
            "No hay datos con esos filtros. Amplía la selección.",
            style={"backgroundColor": "#FFF4E0", "color": "#A35E00",
                   "padding": "12px 16px", "borderRadius": "6px",
                   "marginBottom": "16px", "fontWeight": "600"},
        )
        return "—", "—", "—", "—", vacia, vacia, vacia, aviso

    # Indicadores
    ingresos = filtrados["importe"].sum()
    unidades = int(filtrados["unidades"].sum())
    promedio = ingresos / len(filtrados)
    dias = filtrados["fecha"].nunique()

    # Gráficas
    por_dia = filtrados.groupby("fecha", as_index=False)["importe"].sum()
    fig_linea = px.line(
        por_dia, x="fecha", y="importe",
        title="Ingresos por día",
        labels={"fecha": "Fecha", "importe": "Ingresos ($)"}
    )

    por_cat = filtrados.groupby("categoria", as_index=False)["importe"].sum()
    fig_cat = px.bar(
        por_cat, x="categoria", y="importe",
        title="Ingresos por categoría",
        labels={"categoria": "Categoría", "importe": "Ingresos ($)"}
    )

    por_suc = filtrados.groupby("sucursal", as_index=False)["importe"].sum()
    fig_suc = px.bar(
        por_suc, x="sucursal", y="importe",
        title="Ingresos por sucursal",
        labels={"sucursal": "Sucursal", "importe": "Ingresos ($)"}
    )

    for f in (fig_linea, fig_cat, fig_suc):
        f.update_layout(margin=dict(l=10, r=10, t=50, b=10))

    return (
        f"${ingresos:,.2f}",
        f"{unidades:,}",
        f"${promedio:,.2f}",
        f"{dias}",
        fig_linea,
        fig_cat,
        fig_suc,
        None,  # sin aviso cuando sí hay datos
    )


if __name__ == "__main__":
    app.run(debug=True, port=8050)