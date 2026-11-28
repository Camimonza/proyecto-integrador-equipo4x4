from dash import (Dash, Input, Output, State, dash_table, dcc, html,
                  no_update)
from dash.dash_table import FormatTemplate
from dash.exceptions import PreventUpdate
from collections import OrderedDict
import base64
import io
import uuid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

ESTILO_UPLOAD = {
    "border": f"2px dashed {LAVENDER}",
    "borderRadius": "10px",
    "padding": "18px 10px",
    "textAlign": "center",
    "color": BLANCO,
    "cursor": "pointer",
}

ESTILO_BOTON = {
    "backgroundColor": PURPLE,
    "color": BLANCO,
    "border": "none",
    "borderRadius": "8px",
    "padding": "10px 14px",
    "fontWeight": "600",
    "cursor": "pointer",
    "width": "100%",
    "marginTop": "12px",
}

# Estilo común para las gráficas de Plotly
ESTILO_GRAFICA = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(255,255,255,1)",
    font=dict(color=NAVY),
    title_font=dict(color=NAVY, size=18),
    margin=dict(t=50, b=30, l=20, r=20),
)

# ---------------------------------------------------------------------
# Datos: el tablero arranca VACÍO y el usuario sube su CSV.
# Cada fila del CSV es una PARTIDA (renglón) de una factura.
# ---------------------------------------------------------------------

# Columnas que el tablero necesita
COLUMNAS_REQUERIDAS = [
    "account_id", "factura_id", "fecha_factura", "estado_factura",
    "moneda", "concepto", "cantidad", "monto_partida",
    "es_prorrateo", "descuento_factura",
]

# Encabezado completo de cobros_partidas.csv, para la plantilla
PLANTILLA_CSV = (
    "account_id,factura_id,fecha_factura,mes,estado_factura,moneda,"
    "concepto,cantidad,monto_partida,es_prorrateo,subtotal_factura,"
    "descuento_factura,impuesto_factura,total_factura,pagado_factura\n"
    "WS-00001,FA-000001,2026-03-01,2026-03,paid,MXN,plan_base,1,"
    "1000.00,False,1000.00,0.0,0.0,1000.00,1000.00\n"
)

# Los DataFrames se guardan en el servidor (no en el navegador) para no
# mandar miles de filas en cada cambio de filtro. El navegador solo
# guarda un identificador de sesión. Se conservan las últimas sesiones.
CACHE = OrderedDict()
MAX_SESIONES = 8


def guardar_datos(df, sesion_anterior=None):
    if sesion_anterior:
        CACHE.pop(sesion_anterior, None)
    sesion = uuid.uuid4().hex
    CACHE[sesion] = df
    while len(CACHE) > MAX_SESIONES:
        CACHE.popitem(last=False)
    return sesion


def leer_csv(raw):
    """Convierte los bytes subidos en un DataFrame."""
    for codificacion in ("utf-8-sig", "latin-1"):
        try:
            texto = raw.decode(codificacion)
            break
        except UnicodeDecodeError:
            continue
    df = pd.read_csv(io.StringIO(texto))
    # Si todo quedó en una sola columna, probablemente separa con ;
    if df.shape[1] == 1 and ";" in str(df.columns[0]):
        df = pd.read_csv(io.StringIO(texto), sep=";")
    return df


def preparar_datos(df):
    """Valida columnas y limpia tipos. Regresa (df, filas_descartadas)."""
    df.columns = [str(c).strip() for c in df.columns]
    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
    if faltantes:
        raise ValueError("Faltan columnas: " + ", ".join(faltantes))

    df = df.copy()
    df["fecha_factura"] = pd.to_datetime(
        df["fecha_factura"], errors="coerce").dt.normalize()
    for c in ("cantidad", "monto_partida", "descuento_factura"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["descuento_factura"] = df["descuento_factura"].fillna(0)

    antes = len(df)
    df = df.dropna(subset=[
        "account_id", "factura_id", "fecha_factura", "estado_factura",
        "moneda", "concepto", "cantidad", "monto_partida",
    ])
    if df.empty:
        raise ValueError("El archivo no tiene filas válidas "
                         "(revisa fechas, montos y cantidades).")

    for c in ("account_id", "factura_id", "estado_factura",
              "moneda", "concepto"):
        df[c] = df[c].astype(str).str.strip()

    df["es_prorrateo"] = (
        df["es_prorrateo"].astype(str).str.strip().str.lower()
        .isin(["true", "1", "si", "sí", "yes", "verdadero"])
    )
    return df, antes - len(df)


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


# ---------------------------------------------------------------------
# Churn: cuentas activas, nuevas, bajas y retención por cohorte.
# Los datos no traen fecha de cancelación, así que una cuenta se
# considera DADA DE BAJA cuando ya no vuelve a tener facturas.
# ---------------------------------------------------------------------
def etiqueta_mes(i):
    """Convierte un índice numérico de mes (año*12 + mes) en 'AAAA-MM'."""
    return f"{i // 12}-{i % 12 + 1:02d}"


def calcular_churn(datos):
    """Calcula las series de churn con todo el archivo (sin filtros).

    Regresa None si hay menos de 2 meses de datos.
    """
    facturas = datos.drop_duplicates("factura_id")[
        ["account_id", "fecha_factura"]].copy()
    facturas["mes_i"] = (facturas["fecha_factura"].dt.year * 12
                         + facturas["fecha_factura"].dt.month - 1)

    # Primer y último mes en que cada cuenta tuvo factura
    por_cuenta = facturas.groupby("account_id")["mes_i"].agg(
        primero="min", ultimo="max")
    mes_ini, mes_fin = facturas["mes_i"].min(), facturas["mes_i"].max()
    if mes_fin == mes_ini:
        return None
    meses = range(mes_ini, mes_fin + 1)

    # Activas: cuentas con factura en el mes
    activas = (facturas.groupby("mes_i")["account_id"].nunique()
               .reindex(meses, fill_value=0))
    # Nuevas: primera factura en ese mes (el primer mes es toda la base)
    nuevas = (por_cuenta[por_cuenta["primero"] > mes_ini]
              .groupby("primero").size().reindex(meses, fill_value=0))
    # Bajas: no vuelven a facturar; se cuentan en el primer mes sin factura
    bajas = (por_cuenta[por_cuenta["ultimo"] < mes_fin]
             .assign(mes_baja=lambda t: t["ultimo"] + 1)
             .groupby("mes_baja").size().reindex(meses, fill_value=0))

    # Retención por cohorte (mes de la primera factura)
    cohorte = facturas.merge(por_cuenta["primero"], left_on="account_id",
                             right_index=True)
    cohorte["n"] = cohorte["mes_i"] - cohorte["primero"]
    tabla_coh = cohorte.pivot_table(index="primero", columns="n",
                                    values="account_id", aggfunc="nunique")
    retencion = tabla_coh.div(tabla_coh[0], axis=0)

    return {
        "etiquetas": [etiqueta_mes(m) for m in meses],
        "activas": activas, "nuevas": nuevas, "bajas": bajas,
        "retencion": retencion,
    }


def vista_cobranza():
    """Contenido de la pestaña Cobranza (responde a los filtros)."""
    return [
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
            colors={"border": BORDE, "primary": PURPLE,
                    "background": FONDO},
            children=[
                dcc.Tab(label="Todas las cuentas",
                        children=tabla("tabla-todas")),
                dcc.Tab(label="Pagadas (paid)",
                        children=tabla("tabla-pagadas")),
                dcc.Tab(label="En riesgo (open / uncollectible)",
                        children=tabla("tabla-riesgo")),
            ],
        ),
    ]


def vista_churn():
    """Contenido de la pestaña Churn (usa todo el archivo, sin filtros)."""
    return [
        html.P(
            "Esta vista usa todo el archivo y no cambia con los filtros. "
            "Una cuenta se considera dada de baja cuando ya no vuelve a "
            "tener facturas. Es una aproximación: las bajas del último mes "
            "pueden estar sobrestimadas si aún faltan facturas por emitir.",
            style={"color": "#68778D", "marginTop": "0"}),

        html.Div(id="churn-aviso"),

        # Indicadores de churn
        html.Div([
            tarjeta("Cuentas activas (último mes)", "churn-kpi-activas"),
            tarjeta("Cambio vs. el mes con más cuentas",
                    "churn-kpi-variacion"),
            tarjeta("Bajas por mes (promedio)", "churn-kpi-bajas"),
            tarjeta("Churn mensual (aprox.)", "churn-kpi-tasa"),
        ], style=ESTILO_FILA),

        # Activas y nuevas/bajas lado a lado
        html.Div([
            html.Div(dcc.Graph(id="grafica-activas"), style=ESTILO_TARJETA),
            html.Div(dcc.Graph(id="grafica-nuevas-bajas"),
                     style=ESTILO_TARJETA),
        ], style=ESTILO_FILA),

        # Retención por cohorte
        html.Div(dcc.Graph(id="grafica-cohorte"),
                 style={**ESTILO_TARJETA, "marginBottom": "25px"}),
    ]


# Layout
app.layout = html.Div([

    # Identificador de la sesión (los datos viven en el servidor)
    dcc.Store(id="almacen-sesion", storage_type="memory"),
    dcc.Download(id="descarga-plantilla"),

    # Barra lateral
    html.Div([

        html.H2("Datos", style={"color": BLANCO, "marginTop": "0"}),

        dcc.Upload(
            id="subir-csv",
            children=html.Div([
                "Arrastra tu CSV aquí o ",
                html.A("selecciónalo",
                       style={"color": LAVENDER, "fontWeight": "600",
                              "textDecoration": "underline"}),
            ]),
            style=ESTILO_UPLOAD,
            multiple=False,
            max_size=50 * 1024 * 1024,
        ),

        html.Div(id="mensaje-carga",
                 style={"color": BLANCO, "fontSize": "13px",
                        "marginTop": "10px"}),

        html.Button("Descargar plantilla CSV", id="boton-plantilla",
                    n_clicks=0, style=ESTILO_BOTON),

        html.H2("Filtros", style={"color": BLANCO, "marginTop": "30px"}),

        filtro("Estado de Factura", dcc.Dropdown(
            id="filtro-estado", options=[], value=[], multi=True,
        )),

        filtro("Moneda", dcc.Dropdown(
            id="filtro-moneda", options=[], value=[], multi=True,
        )),

        filtro("Concepto", dcc.Dropdown(
            id="filtro-concepto", options=[], value=[], multi=True,
        )),

        filtro("Cuenta (vacío = todas)", dcc.Dropdown(
            id="filtro-cuenta", options=[], value=[], multi=True,
            placeholder="Buscar cuenta...",
        )),

        filtro("Prorrateo", dcc.Dropdown(
            id="filtro-prorrateo", options=OPCIONES_PRORRATEO,
            value="todas", clearable=False,
        )),

        filtro("Descuento", dcc.Dropdown(
            id="filtro-descuento", options=OPCIONES_DESCUENTO,
            value="todas", clearable=False,
        )),

        filtro("Partidas en $0", dcc.Dropdown(
            id="filtro-ceros", options=OPCIONES_CEROS,
            value="mostrar", clearable=False,
        )),

        filtro("Periodo", dcc.DatePickerRange(
            id="filtro-periodo",
            display_format="DD/MM/YYYY",
        )),

    ], style=ESTILO_SIDEBAR),

    # Contenido principal
    html.Div([

        html.H1("Dashboard de Control Cobros Partidas",
                style={"color": NAVY, "marginTop": "0"}),

        # Pantalla de bienvenida (se oculta al cargar datos)
        html.Div(id="bienvenida", children=[
            html.H3("Sube tu archivo para ver el dashboard",
                    style={"color": NAVY, "marginTop": "0"}),
            html.P("Usa el cuadro «Datos» de la barra lateral para subir un "
                   "CSV con el mismo formato que cobros_partidas.csv. "
                   "Si no tienes el formato, descarga la plantilla."),
            html.P("Columnas necesarias:", style={"fontWeight": "600",
                                                   "marginBottom": "4px"}),
            html.Code(", ".join(COLUMNAS_REQUERIDAS)),
        ], style={**ESTILO_TARJETA, "display": "block"}),

        # Todo el dashboard (se muestra al cargar datos)
        html.Div(id="contenido-dashboard", style={"display": "none"},
                 children=[

            html.P(id="subtitulo-datos", style={"color": "#68778D"}),

            # Dos vistas: Cobranza (con filtros) y Churn
            dcc.Tabs(
                id="vista",
                value="cobranza",
                colors={"border": BORDE, "primary": PURPLE,
                        "background": FONDO},
                style={"marginBottom": "24px"},
                children=[
                    dcc.Tab(label="Cobranza", value="cobranza",
                            children=html.Div(
                                vista_cobranza(),
                                style={"paddingTop": "24px"})),
                    dcc.Tab(label="Churn", value="churn",
                            children=html.Div(
                                vista_churn(),
                                style={"paddingTop": "24px"})),
                ],
            ),
        ]),

    ], style=ESTILO_CONTENIDO),

], style=ESTILO_PAGINA)


# ---------------------------------------------------------------------
# Callback 1: recibir el CSV, validarlo y preparar los filtros
# ---------------------------------------------------------------------
@app.callback(
    Output("almacen-sesion", "data"),
    Output("mensaje-carga", "children"),
    Output("filtro-estado", "options"),
    Output("filtro-estado", "value"),
    Output("filtro-moneda", "options"),
    Output("filtro-moneda", "value"),
    Output("filtro-concepto", "options"),
    Output("filtro-concepto", "value"),
    Output("filtro-cuenta", "options"),
    Output("filtro-cuenta", "value"),
    Output("filtro-periodo", "min_date_allowed"),
    Output("filtro-periodo", "max_date_allowed"),
    Output("filtro-periodo", "start_date"),
    Output("filtro-periodo", "end_date"),
    Output("contenido-dashboard", "style"),
    Output("bienvenida", "style"),
    Output("subtitulo-datos", "children"),
    Input("subir-csv", "contents"),
    State("subir-csv", "filename"),
    State("almacen-sesion", "data"),
    prevent_initial_call=True,
)
def cargar_csv(contenido, nombre, sesion_anterior):
    if contenido is None:
        raise PreventUpdate

    # Si algo sale mal, solo se muestra el mensaje y no cambia nada más
    def error(texto):
        return (no_update, html.Span(texto, style={"color": "#FFB4B4"}),
                *([no_update] * 15))

    try:
        _, codificado = contenido.split(",", 1)
        raw = base64.b64decode(codificado)
        df = leer_csv(raw)
        df, descartadas = preparar_datos(df)
    except pd.errors.EmptyDataError:
        return error(f"{nombre}: el archivo está vacío.")
    except ValueError as e:
        return error(f"{nombre}: {e}")
    except Exception:
        return error(f"{nombre}: no se pudo leer como CSV. "
                     "Revisa que sea un archivo de texto separado por comas.")

    sesion = guardar_datos(df, sesion_anterior)

    estados = sorted(df["estado_factura"].unique())
    monedas = sorted(df["moneda"].unique())
    conceptos = sorted(df["concepto"].unique())
    cuentas = sorted(df["account_id"].unique())
    fecha_min = df["fecha_factura"].min().date()
    fecha_max = df["fecha_factura"].max().date()

    # Por defecto una sola moneda: MXN y USD no se pueden sumar
    monedas_iniciales = ["MXN"] if "MXN" in monedas else monedas[:1]

    texto = f"{nombre}: {len(df):,} partidas cargadas."
    if descartadas:
        texto += f" Se descartaron {descartadas:,} filas con datos inválidos."

    return (
        sesion,
        texto,
        estados, estados,
        monedas, monedas_iniciales,
        conceptos, conceptos,
        cuentas, [],
        fecha_min, fecha_max, fecha_min, fecha_max,
        {"display": "block"},
        {"display": "none"},
        f"Datos del {fecha_min:%d-%b-%Y} al {fecha_max:%d-%b-%Y}",
    )


# ---------------------------------------------------------------------
# Callback 2: un solo callback para todo el tablero.
# Orden de los Input = orden de los argumentos de la función.
# Orden de los Output = orden de los valores del return.
# ---------------------------------------------------------------------
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
    Input("almacen-sesion", "data"),
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
def actualizar(sesion, estados, monedas, conceptos, cuentas, prorrateo,
               descuento, ceros, inicio, fin):

    def vacio(titulo, aviso=None):
        fig = px.scatter(title=titulo)
        return "—", "—", "—", "—", fig, fig, fig, [], [], [], aviso

    # Todavía no se sube ningún archivo
    if not sesion:
        return vacio("Sube un archivo CSV para ver el dashboard")

    datos = CACHE.get(sesion)
    if datos is None:
        return vacio("Sin datos", html.Div(
            "Los datos de esta sesión ya no están disponibles. "
            "Vuelve a subir el archivo.",
            style={"backgroundColor": "#FFF4E0", "color": "#A35E00",
                   "padding": "12px 16px", "borderRadius": "6px",
                   "marginBottom": "16px", "fontWeight": "600"},
        ))

    estados = estados or []
    monedas = monedas or []
    conceptos = conceptos or []
    inicio = (pd.to_datetime(inicio) if inicio
              else datos["fecha_factura"].min())
    fin = pd.to_datetime(fin) if fin else datos["fecha_factura"].max()

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
        return vacio(
            "Sin datos para los filtros seleccionados",
            html.Div(
                "No hay datos con esos filtros. Amplía la selección.",
                style={"backgroundColor": "#FFF4E0", "color": "#A35E00",
                       "padding": "12px 16px", "borderRadius": "6px",
                       "marginBottom": "16px", "fontWeight": "600"},
            ),
        )

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


# ---------------------------------------------------------------------
# Callback 3: vista de churn. Solo depende del archivo cargado (no de los
# filtros), por eso se calcula una vez por archivo y no en cada filtro.
# ---------------------------------------------------------------------
@app.callback(
    Output("churn-kpi-activas", "children"),
    Output("churn-kpi-variacion", "children"),
    Output("churn-kpi-bajas", "children"),
    Output("churn-kpi-tasa", "children"),
    Output("grafica-activas", "figure"),
    Output("grafica-nuevas-bajas", "figure"),
    Output("grafica-cohorte", "figure"),
    Output("churn-aviso", "children"),
    Input("almacen-sesion", "data"),
)
def actualizar_churn(sesion):

    def vacio(titulo, aviso=None):
        fig = px.scatter(title=titulo)
        return "—", "—", "—", "—", fig, fig, fig, aviso

    datos = CACHE.get(sesion) if sesion else None
    if datos is None:
        return vacio("Sube un archivo CSV para ver el churn")

    churn = calcular_churn(datos)
    if churn is None:
        return vacio("Sin datos suficientes", html.Div(
            "La vista de churn necesita facturas de al menos 2 meses.",
            style={"backgroundColor": "#FFF4E0", "color": "#A35E00",
                   "padding": "12px 16px", "borderRadius": "6px",
                   "marginBottom": "16px", "fontWeight": "600"},
        ))

    etiquetas = churn["etiquetas"]
    activas, nuevas, bajas = churn["activas"], churn["nuevas"], churn["bajas"]
    retencion = churn["retencion"]

    # Indicadores
    ultimo = int(activas.iloc[-1])
    variacion = ultimo / activas.max() - 1
    bajas_prom = bajas.iloc[1:].mean()
    tasa = (bajas.iloc[1:].values / activas.iloc[:-1].values).mean()

    # Cuentas activas por mes
    fig_activas = px.line(
        x=etiquetas, y=activas.values, markers=True,
        title="Cuentas activas por mes",
        labels={"x": "Mes", "y": "Cuentas con factura"},
        color_discrete_sequence=[PURPLE],
    )
    fig_activas.update_traces(line=dict(width=3))

    # Cuentas nuevas (arriba) y bajas (abajo)
    fig_nb = go.Figure()
    fig_nb.add_bar(x=etiquetas, y=nuevas.values, name="Nuevas",
                   marker_color=LAVENDER)
    fig_nb.add_bar(x=etiquetas, y=-bajas.values, name="Bajas",
                   marker_color="#E74C3C")
    fig_nb.update_layout(barmode="relative",
                         title="Cuentas nuevas y bajas por mes",
                         yaxis_title="Cuentas")

    # Retención por cohorte
    fig_coh = go.Figure(go.Heatmap(
        z=retencion.values,
        x=[f"Mes {n}" for n in retencion.columns],
        y=[etiqueta_mes(i) for i in retencion.index],
        colorscale=[[0, FONDO], [1, PURPLE]], zmin=0, zmax=1,
        texttemplate="%{z:.0%}", hoverongaps=False,
    ))
    fig_coh.update_layout(
        title="Retención por cohorte de alta (mes de la primera factura)",
        xaxis_title="Meses desde la primera factura",
        yaxis_title="Cohorte")
    fig_coh.update_yaxes(autorange="reversed")

    for f in (fig_activas, fig_nb, fig_coh):
        f.update_layout(**ESTILO_GRAFICA)

    return (
        f"{ultimo:,}",
        f"{variacion:+.0%}",
        f"{bajas_prom:,.0f}",
        f"{tasa:.1%}",
        fig_activas, fig_nb, fig_coh,
        None,
    )


# ---------------------------------------------------------------------
# Callback 4: descargar la plantilla vacía
# ---------------------------------------------------------------------
@app.callback(
    Output("descarga-plantilla", "data"),
    Input("boton-plantilla", "n_clicks"),
    prevent_initial_call=True,
)
def descargar_plantilla(n_clicks):
    return dcc.send_string(PLANTILLA_CSV, "plantilla_cobros_partidas.csv")


if __name__ == "__main__":
    app.run(debug=True, port=8052)