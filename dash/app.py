
from dash import Dash, dcc, html
from pathlib import Path
import pandas as pd
import plotly.express as px

app = Dash(__name__)

# Colores
FONDO = "#F4F6F9"
TINTA = "#243247"
AZUL = "#2878B5"
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

# Cargar datos
RUTA = Path(__file__).parent.parent / "datos" / "ventas.csv"
datos = pd.read_csv(RUTA, parse_dates=["fecha"])


# Crear tarjetas KPI
def tarjeta(titulo, valor):
    return html.Div([
        html.P(titulo, style={"color": "#68778D", "margin": "0"}),
        html.H2(valor, style={"color": TINTA, "marginBottom": "0"})
    ], style=ESTILO_TARJETA)


# Layout
app.layout = html.Div([

    html.H1(
        "Tablero de ventas",
        style={"color": TINTA}
    ),

    html.P(
        "Abarrotera del Bajío - enero a octubre 2026",
        style={"color": "#68778D"}
    ),

    html.H3("Filtrar por sucursal", style={"color": TINTA}),

    dcc.Dropdown(
        id="filtro-sucursal",
        options=[
            {"label": "Todas las sucursales", "value": "Todas"}
        ] + [
            {"label": sucursal, "value": sucursal}
            for sucursal in sorted(datos["sucursal"].unique())
        ],
        value="Todas",
        clearable=False,
        style={"maxWidth": "400px", "marginBottom": "25px"}
    ),

    # Indicadores
    html.Div([
        tarjeta("Ingresos totales", f"${datos['importe'].sum():,.2f}"),
        tarjeta("Unidades vendidas", f"{datos['unidades'].sum():,.0f}"),
        tarjeta(
            "Importe promedio",
            f"${datos['importe'].mean():,.2f}"
        ),
        tarjeta(
            "Días con venta",
            f"{datos['fecha'].nunique():,.0f}"
        )
    ], style=ESTILO_FILA),

    # Gráfica de ingresos diarios
    html.Div([
        dcc.Graph(
            id="grafica-diaria",
            figure=px.line(
                datos.groupby("fecha", as_index=False)["importe"].sum(),
                x="fecha",
                y="importe",
                title="Ingresos por día",
                labels={
                    "fecha": "Fecha",
                    "importe": "Ingresos ($)"
                }
            )
        )
    ], style=ESTILO_TARJETA),

    # Gráficas por categoría y sucursal
    html.Div([

        html.Div([
            dcc.Graph(
                id="grafica-categoria",
                figure=px.bar(
                    datos.groupby("categoria", as_index=False)["importe"].sum(),
                    x="categoria",
                    y="importe",
                    title="Ingresos por categoría",
                    labels={
                        "categoria": "Categoría",
                        "importe": "Ingresos ($)"
                    }
                )
            )
        ], style={"flex": "1", "minWidth": "300px"}),

        html.Div([
            dcc.Graph(
                id="grafica-sucursal",
                figure=px.bar(
                    datos.groupby("sucursal", as_index=False)["importe"].sum(),
                    x="sucursal",
                    y="importe",
                    title="Ingresos por sucursal",
                    labels={
                        "sucursal": "Sucursal",
                        "importe": "Ingresos ($)"
                    }
                )
            )
        ], style={"flex": "1", "minWidth": "300px"})

    ], style=ESTILO_FILA)

], style=ESTILO_PAGINA)


if __name__ == "__main__":
    app.run(debug=True, port=8050)
