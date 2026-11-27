from dash import Dash, Input, Output, dash_table, dcc, html
from dash.dash_table import FormatTemplate
from pathlib import Path
import pandas as pd
import plotly.express as px

app = Dash(__name__)

# Paleta de colores Leadsales
NAVY = "#180E3E"
PURPLE = "#6B35FF"
LAVENDER = "#9D7BFF"
FONDO = "#F8F7FC"
BORDE = "#E6E0FA"
BLANCO = "#FFFFFF"

# Estilos
ESTILO_PAGINA = {
    "display": "flex",
    "alignItems": "flex-start",
    "minHeight": "100vh",
    "backgroundColor": FONDO,
    "color": NAVY,
    "fontFamily": "Arial",
}

ESTILO_SIDEBAR = {
    "width": "280px",
    "flexShrink": "0",
    "backgroundColor": NAVY,
    "padding": "24px",
    "boxSizing": "border-box",
    "position": "sticky",
    "top": "0",
    "height": "100vh",
    "overflowY": "auto",
}

ESTILO_CONTENIDO = {
    "flex": "1",
    "minWidth": "0",
    "padding": "30px",
}

ESTILO_ETIQUETA = {
    "display": "block",
    "color": BLANCO,
    "fontWeight": "600",
    "marginTop": "20px",
    "marginBottom": "6px",
}

ESTILO_FILA = {
    "display": "flex",
    "gap": "20px",
    "marginBottom": "25px",
    "flexWrap": "wrap",
}

ESTILO_TARJETA = {
    "backgroundColor": BLANCO,
    "padding": "20px",
    "borderRadius": "12px",
    "border": f"1px solid {BORDE}",
    "boxShadow": "0 2px 8px rgba(24, 14, 62, 0.05)",
    "flex": "1",
    "minWidth": "180px",
}

# Estilo común para las gráficas de Plotly
ESTILO_GRAFICA = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(255,255,255,1)",
    font=dict(color=NAVY),
    title_font=dict(color=NAVY, size=18),
    margin=dict(t=50, b=30, l=20, r=20),
)

# Cargar datos
# Cada fila es una PARTIDA (renglón) de una factura.
RUTA = Path(__file__).parent.parent / "datos" / "cobros_partidas.csv"
datos = pd.read_csv(RUTA, parse_dates=["fecha_factura"])

ESTADOS = sorted(datos["estado_factura"].dropna().unique())
MONEDAS = sorted(datos["moneda"].dropna().unique())
CONCEPTOS = sorted(datos["concepto"].dropna().unique())
CUENTAS = sorted(datos["account_id"].dropna().unique())
FECHA_MIN = datos["fecha_factura"].min().date()
FECHA_MAX = datos["fecha_factura"].max().date()

# Los montos en MXN y USD no se pueden sumar entre sí,
# por eso la moneda arranca solo en MXN.
MONEDAS_INICIALES = ["MXN"] if "MXN" in MONEDAS else MONEDAS[:1]


OPCIONES_PRORRATEO = [
    {"label": "Todas las partidas", "value": "todas"},
    {"label": "Solo prorrateos", "value": "si"},
    {"label": "Sin prorrateos", "value": "no"},
]

OPCIONES_DESCUENTO = [
    {"label": "Todas las facturas", "value": "todas"},
    {"label": "Con descuento", "value": "con"},
    {"label": "Sin descuento", "value": "sin"},
]

OPCIONES_CEROS = [
    {"label": "Mostrar partidas en $0", "value": "mostrar"},
    {"label": "Ocultar partidas en $0", "value": "ocultar"},
]


# Tarjeta KPI: solo tiene id, el callback le pone el valor
def tarjeta(titulo, id_valor):
    return html.Div([
        html.P(titulo, style={"fontWeight": "600", "color": NAVY,
                              "margin": "0"}),
        html.H2(id=id_valor, style={"color": PURPLE, "fontWeight": "700",
                                    "marginBottom": "0"}),
    ], style=ESTILO_TARJETA)


# Filtro de la barra lateral: etiqueta + componente
def filtro(etiqueta, componente):
    return html.Div([
        html.Label(etiqueta, style=ESTILO_ETIQUETA),
        componente,
    ])


# Tablas de cuentas
COLUMNAS_TABLA = [
    {"name": "Cuenta", "id": "account_id"},
    {"name": "Moneda", "id": "moneda"},
    {"name": "Facturas", "id": "Facturas", "type": "numeric"},
    {"name": "Partidas", "id": "Partidas", "type": "numeric"},
    {"name": "Monto Total", "id": "Monto_Total", "type": "numeric",
     "format": FormatTemplate.money(2)},
    {"name": "Última Factura", "id": "Ultima_Factura"},
]


def tabla(id_tabla):
    return dash_table.DataTable(
        id=id_tabla,
        columns=COLUMNAS_TABLA,
        data=[],
        page_size=10,
        sort_action="native",
        style_header={"backgroundColor": NAVY, "color": BLANCO,
                      "fontWeight": "600", "border": "none"},
        style_cell={"fontFamily": "Arial", "padding": "8px",
                    "textAlign": "left", "border": f"1px solid {BORDE}"},
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": FONDO},
        ],
    )


def resumen_cuentas(df):
    """Top 50 cuentas por monto, a partir de las partidas filtradas."""
    resumen = (
        df.groupby(["account_id", "moneda"], as_index=False)
        .agg(
            Facturas=("factura_id", "nunique"),
            Partidas=("concepto", "count"),
            Monto_Total=("monto_partida", "sum"),
            Ultima_Factura=("fecha_factura", "max"),
        )
        .sort_values("Monto_Total", ascending=False)
        .head(50)
    )
    resumen["Monto_Total"] = resumen["Monto_Total"].round(2)
    resumen["Ultima_Factura"] = resumen["Ultima_Factura"].dt.strftime(
        "%Y-%m-%d")
    return resumen.to_dict("records")


# Layout
app.layout = html.Div([

    # Barra lateral con los filtros
    html.Div([
        html.H2("Filtros", style={"color": BLANCO, "marginTop": "0"}),

        filtro("Estado de Factura", dcc.Dropdown(
            id="filtro-estado",
            options=ESTADOS,
            value=ESTADOS,
            multi=True,
        )),

        filtro("Moneda", dcc.Dropdown(
            id="filtro-moneda",
            options=MONEDAS,
            value=MONEDAS_INICIALES,
            multi=True,
        )),

        filtro("Concepto", dcc.Dropdown(
            id="filtro-concepto",
            options=CONCEPTOS,
            value=CONCEPTOS,
            multi=True,
        )),

        filtro("Cuenta (vacío = todas)", dcc.Dropdown(
            id="filtro-cuenta",
            options=CUENTAS,
            value=[],
            multi=True,
            placeholder="Buscar cuenta...",
        )),

        filtro("Prorrateo", dcc.Dropdown(
            id="filtro-prorrateo",
            options=OPCIONES_PRORRATEO,
            value="todas",
            clearable=False,
        )),

        filtro("Descuento", dcc.Dropdown(
            id="filtro-descuento",
            options=OPCIONES_DESCUENTO,
            value="todas",
            clearable=False,
        )),

        filtro("Partidas en $0", dcc.Dropdown(
            id="filtro-ceros",
            options=OPCIONES_CEROS,
            value="mostrar",
            clearable=False,
        )),

        filtro("Periodo", dcc.DatePickerRange(
            id="filtro-periodo",
            min_date_allowed=FECHA_MIN,
            max_date_allowed=FECHA_MAX,
            start_date=FECHA_MIN,
            end_date=FECHA_MAX,
            display_format="DD/MM/YYYY",
        )),

    ], style=ESTILO_SIDEBAR),

    # Contenido principal
    html.Div([

        html.H1("Dashboard de Control Cobros Partidas",
                style={"color": NAVY, "marginTop": "0"}),

        html.P(
            f"Datos del {FECHA_MIN:%d-%b-%Y} al {FECHA_MAX:%d-%b-%Y}",
            style={"color": "#68778D"}
        ),

        # Aviso de selección vacía
        html.Div(id="aviso-vacio"),

        # Indicadores
        html.Div([
            tarjeta("Ingresos (partidas)", "kpi-ingresos"),
            tarjeta("Cantidad", "kpi-cantidad"),
            tarjeta("Monto promedio", "kpi-promedio"),
            tarjeta("Días con cobro", "kpi-dias"),
        ], style=ESTILO_FILA),

        # Gráfica ancha
        html.Div(
            dcc.Graph(id="grafica-dia"),
            style={**ESTILO_TARJETA, "marginBottom": "25px"}
        ),

        # Dos gráficas lado a lado
        html.Div([
            html.Div(dcc.Graph(id="grafica-concepto"),
                     style=ESTILO_TARJETA),
            html.Div(dcc.Graph(id="grafica-estado"),
                     style=ESTILO_TARJETA),
        ], style=ESTILO_FILA),

        # Tablas de cuentas
        html.H3("Top Cuentas por Monto Facturado", style={"color": NAVY}),

        dcc.Tabs(
            colors={"border": BORDE, "primary": PURPLE, "background": FONDO},
            children=[
                dcc.Tab(label="Todas las cuentas",
                        children=tabla("tabla-todas")),
                dcc.Tab(label="Pagadas (paid)",
                        children=tabla("tabla-pagadas")),
                dcc.Tab(label="En riesgo (open / uncollectible)",
                        children=tabla("tabla-riesgo")),
            ],
        ),

    ], style=ESTILO_CONTENIDO),

], style=ESTILO_PAGINA)


# Un solo callback para todo el tablero.
# Orden de los Input = orden de los argumentos de la función.
# Orden de los Output = orden de los valores del return.
@app.callback(
    Output("kpi-ingresos", "children"),
    Output("kpi-cantidad", "children"),
    Output("kpi-promedio", "children"),
    Output("kpi-dias", "children"),
    Output("grafica-dia", "figure"),
    Output("grafica-concepto", "figure"),
    Output("grafica-estado", "figure"),
    Output("tabla-todas", "data"),
    Output("tabla-pagadas", "data"),
    Output("tabla-riesgo", "data"),
    Output("aviso-vacio", "children"),
    Input("filtro-estado", "value"),
    Input("filtro-moneda", "value"),
    Input("filtro-concepto", "value"),
    Input("filtro-cuenta", "value"),
    Input("filtro-prorrateo", "value"),
    Input("filtro-descuento", "value"),
    Input("filtro-ceros", "value"),
    Input("filtro-periodo", "start_date"),
    Input("filtro-periodo", "end_date"),
)
def actualizar(estados, monedas, conceptos, cuentas, prorrateo, descuento,
               ceros, inicio, fin):
    estados = estados or []
    monedas = monedas or []
    conceptos = conceptos or []
    inicio = pd.to_datetime(inicio) if inicio else pd.Timestamp(FECHA_MIN)
    fin = pd.to_datetime(fin) if fin else pd.Timestamp(FECHA_MAX)

    mascara = (
        datos["estado_factura"].isin(estados)
        & datos["moneda"].isin(monedas)
        & datos["concepto"].isin(conceptos)
        & datos["fecha_factura"].between(inicio, fin)
    )

    # Filtros opcionales: si no se eligió nada, no filtran
    if cuentas:
        mascara &= datos["account_id"].isin(cuentas)

    if prorrateo == "si":
        mascara &= datos["es_prorrateo"]
    elif prorrateo == "no":
        mascara &= ~datos["es_prorrateo"]

    if descuento == "con":
        mascara &= datos["descuento_factura"] > 0
    elif descuento == "sin":
        mascara &= datos["descuento_factura"] == 0

    if ceros == "ocultar":
        mascara &= datos["monto_partida"] != 0

    filtrados = datos[mascara]

    # Salida anticipada: mismos 11 valores que el return normal
    if filtrados.empty:
        vacia = px.scatter(title="Sin datos para los filtros seleccionados")
        aviso = html.Div(
            "No hay datos con esos filtros. Amplía la selección.",
            style={"backgroundColor": "#FFF4E0", "color": "#A35E00",
                   "padding": "12px 16px", "borderRadius": "6px",
                   "marginBottom": "16px", "fontWeight": "600"},
        )
        return ("—", "—", "—", "—", vacia, vacia, vacia,
                [], [], [], aviso)

    # Indicadores
    ingresos = filtrados["monto_partida"].sum()
    cantidad = int(filtrados["cantidad"].sum())
    promedio = ingresos / len(filtrados)
    dias = filtrados["fecha_factura"].nunique()

    # Ingresos por día
    por_dia = filtrados.groupby("fecha_factura", as_index=False)[
        "monto_partida"].sum()
    fig_dia = px.line(
        por_dia, x="fecha_factura", y="monto_partida",
        title="Ingresos por día",
        labels={"fecha_factura": "Fecha", "monto_partida": "Monto"},
        color_discrete_sequence=[PURPLE],
    )
    fig_dia.update_traces(line=dict(width=3))

    # Ingresos por concepto
    por_concepto = filtrados.groupby("concepto", as_index=False)[
        "monto_partida"].sum()
    fig_concepto = px.bar(
        por_concepto, x="concepto", y="monto_partida",
        title="Ingresos por concepto",
        labels={"concepto": "Concepto", "monto_partida": "Monto"},
        color_discrete_sequence=[PURPLE],
    )

    # Ingresos por estado de factura
    por_estado = filtrados.groupby("estado_factura", as_index=False)[
        "monto_partida"].sum()
    fig_estado = px.bar(
        por_estado, x="estado_factura", y="monto_partida",
        title="Ingresos por estado de factura",
        labels={"estado_factura": "Estado", "monto_partida": "Monto"},
        color="estado_factura",
        color_discrete_map={
            "paid": PURPLE,
            "open": LAVENDER,
            "uncollectible": "#E74C3C",
            "void": "#94A3B8",
        },
    )

    for f in (fig_dia, fig_concepto, fig_estado):
        f.update_layout(**ESTILO_GRAFICA)
    fig_estado.update_layout(showlegend=False)

    # Tablas de cuentas
    pagadas = filtrados[filtrados["estado_factura"] == "paid"]
    riesgo = filtrados[
        filtrados["estado_factura"].isin(["open", "uncollectible"])
    ]

    return (
        f"${ingresos:,.0f}",
        f"{cantidad:,}",
        f"${promedio:,.0f}",
        f"{dias}",
        fig_dia,
        fig_concepto,
        fig_estado,
        resumen_cuentas(filtrados),
        resumen_cuentas(pagadas),
        resumen_cuentas(riesgo),
        None,  # sin aviso cuando sí hay datos
    )


if __name__ == "__main__":
    app.run(debug=True, port=8052)