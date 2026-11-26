from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard de Control Cobros Patidas",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta de colores Leadsales
COLOR_NAVY = "#180E3E"
COLOR_PURPLE = "#6B35FF"
COLOR_LAVENDER = "#9D7BFF"
COLOR_SOFT_BG = "#F8F7FC"
COLOR_CARD_BORDER = "#E6E0FA"
PALETA_LEADSALES = ["#6B35FF", "#180E3E", "#9D7BFF", "#4318FF", "#C4B5FD"]

# Estilos CSS personalizados (identidad Leadsales)
st.markdown(
    f"""
    <style>
        /* Fondo general */
        .stApp {{
            background-color: {COLOR_SOFT_BG};
            color: {COLOR_NAVY};
        }}

        /* Títulos */
        h1, h2, h3 {{
            color: {COLOR_NAVY} !important;
        }}

        /* Barra lateral estilo hero oscuro de Leadsales */
        section[data-testid="stSidebar"] {{
            background-color: {COLOR_NAVY};
        }}
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {{
            color: #FFFFFF !important;
        }}

        /* Etiquetas de los multiselect en morado Leadsales */
        span[data-baseweb="tag"] {{
            background-color: {COLOR_PURPLE} !important;
            color: #FFFFFF !important;
        }}

        /* Tarjetas de KPIs */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: #FFFFFF;
            border: 1px solid {COLOR_CARD_BORDER} !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(24, 14, 62, 0.05);
        }}
        div[data-testid="stMetricValue"] {{
            color: {COLOR_PURPLE} !important;
            font-weight: 700;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {COLOR_NAVY} !important;
            font-weight: 600;
        }}

        /* Pestañas (tabs) */
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {COLOR_PURPLE} !important;
            border-bottom-color: {COLOR_PURPLE} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Cargar datos del CSV
RUTA = Path(__file__).parent.parent / "datos" / "cobros_partidas.csv"



@st.cache_data
def cargar_datos(ruta: Path) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    df["fecha_factura"] = pd.to_datetime(df["fecha_factura"]).dt.date
    return df


datos = cargar_datos(RUTA)

st.title("Dashboard de Control Cobros Patidas")
st.caption("Corte: 31-May-2026")

# Barra lateral con filtros dinámicos basados en cobros_partidas.csv
with st.sidebar:
    st.header("Filtros")

    estados = st.multiselect(
        "Estado de Factura",
        options=sorted(datos["estado_factura"].dropna().unique()),
        default=sorted(datos["estado_factura"].dropna().unique()),
    )

    monedas = st.multiselect(
        "Moneda",
        options=sorted(datos["moneda"].dropna().unique()),
        default=sorted(datos["moneda"].dropna().unique()),
    )

    conceptos = st.multiselect(
        "Concepto",
        options=sorted(datos["concepto"].dropna().unique()),
        default=sorted(datos["concepto"].dropna().unique()),
    )

    fecha_min = datos["fecha_factura"].min()
    fecha_max = datos["fecha_factura"].max()

    rango_fechas = st.date_input(
        "Periodo",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
    )

# Aplicar filtros al DataFrame
if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
    inicio, fin = rango_fechas
else:
    inicio, fin = fecha_min, fecha_max

datos_filtrados = datos[
    (datos["estado_factura"].isin(estados))
    & (datos["moneda"].isin(monedas))
    & (datos["concepto"].isin(conceptos))
    & (datos["fecha_factura"] >= inicio)
    & (datos["fecha_factura"] <= fin)
]

if datos_filtrados.empty:
    st.warning("No hay datos con esos filtros. Amplia la seleccion.")
    st.stop()

# KPIs calculados con datos reales
ingresos = datos_filtrados["monto_partida"].sum()
unidades = int(datos_filtrados["cantidad"].sum())
promedio = ingresos / len(datos_filtrados)
dias = datos_filtrados["fecha_factura"].nunique()

c1, c2, c3, c4 = st.columns(4)
with c1:
    with st.container(border=True):
        st.metric("Ingresos (partidas)", f"${ingresos:,.0f}")
with c2:
    with st.container(border=True):
        st.metric("Cantidad", f"{unidades:,}")
with c3:
    with st.container(border=True):
        st.metric("Monto promedio", f"${promedio:,.0f}")
with c4:
    with st.container(border=True):
        st.metric("Días con cobro", f"{dias}")

st.write("")

# Estilo común para gráficas de Plotly
estilo_grafica = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(255,255,255,1)",
    font=dict(color=COLOR_NAVY),
    title_font=dict(color=COLOR_NAVY, size=18),
    margin=dict(t=50, b=30, l=20, r=20),
)

# Gráficas basadas en datos_filtrados
por_dia = datos_filtrados.groupby("fecha_factura", as_index=False)["monto_partida"].sum()
fig_dia = px.line(
    por_dia,
    x="fecha_factura",
    y="monto_partida",
    title="Ingresos por día",
    labels={"fecha_factura": "Fecha", "monto_partida": "Monto"},
    color_discrete_sequence=[COLOR_PURPLE],
)
fig_dia.update_traces(line=dict(width=3))
fig_dia.update_layout(**estilo_grafica)
st.plotly_chart(fig_dia, use_container_width=True)

izq, der = st.columns(2)

por_concepto = datos_filtrados.groupby("concepto", as_index=False)["monto_partida"].sum()
fig_concepto = px.bar(
    por_concepto,
    x="concepto",
    y="monto_partida",
    title="Ingresos por concepto",
    labels={"concepto": "Concepto", "monto_partida": "Monto"},
    color_discrete_sequence=[COLOR_PURPLE],
)
fig_concepto.update_layout(**estilo_grafica)
izq.plotly_chart(fig_concepto, use_container_width=True)

por_estado = datos_filtrados.groupby("estado_factura", as_index=False)["monto_partida"].sum()
fig_estado = px.bar(
    por_estado,
    x="estado_factura",
    y="monto_partida",
    title="Ingresos por estado de factura",
    labels={"estado_factura": "Estado", "monto_partida": "Monto"},
    color="estado_factura",
    color_discrete_map={
        "paid": COLOR_PURPLE,
        "open": COLOR_LAVENDER,
        "uncollectible": "#E74C3C",
        "void": "#94A3B8",
    },
)
fig_estado.update_layout(**estilo_grafica, showlegend=False)
der.plotly_chart(fig_estado, use_container_width=True)

# Tabla dinámica basada en datos_filtrados
st.subheader("Top Cuentas por Monto Facturado")

resumen_cuentas = (
    datos_filtrados.groupby(["account_id", "moneda"], as_index=False)
    .agg(
        Facturas=("factura_id", "nunique"),
        Partidas=("concepto", "count"),
        Monto_Total=("monto_partida", "sum"),
        Ultima_Factura=("fecha_factura", "max"),
    )
    .sort_values("Monto_Total", ascending=False)
)

df_pagadas = datos_filtrados[datos_filtrados["estado_factura"] == "paid"]
resumen_pagadas = (
    df_pagadas.groupby(["account_id", "moneda"], as_index=False)
    .agg(
        Facturas=("factura_id", "nunique"),
        Monto_Total=("monto_partida", "sum"),
        Ultima_Factura=("fecha_factura", "max"),
    )
    .sort_values("Monto_Total", ascending=False)
)

df_riesgo = datos_filtrados[
    datos_filtrados["estado_factura"].isin(["open", "uncollectible"])
]
resumen_riesgo = (
    df_riesgo.groupby(["account_id", "moneda"], as_index=False)
    .agg(
        Facturas=("factura_id", "nunique"),
        Monto_Total=("monto_partida", "sum"),
        Ultima_Factura=("fecha_factura", "max"),
    )
    .sort_values("Monto_Total", ascending=False)
)

formato_tabla = {
    "account_id": "Cuenta",
    "moneda": "Moneda",
    "Monto_Total": st.column_config.NumberColumn("Monto Total", format="$%.2f"),
    "Ultima_Factura": "Última Factura",
}

tab_todas, tab_pagadas, tab_riesgo = st.tabs(
    ["Todas las cuentas", "Pagadas (paid)", "En riesgo (open / uncollectible)"]
)

with tab_todas:
    st.dataframe(
        resumen_cuentas.head(50),
        use_container_width=True,
        hide_index=True,
        column_config=formato_tabla,
    )

with tab_pagadas:
    st.dataframe(
        resumen_pagadas.head(50),
        use_container_width=True,
        hide_index=True,
        column_config=formato_tabla,
    )

with tab_riesgo:
    st.dataframe(
        resumen_riesgo.head(50),
        use_container_width=True,
        hide_index=True,
        column_config=formato_tabla,
    )