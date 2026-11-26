import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard de Control de Churn",
    layout="wide",
)

st.title("Dashboard de Control de Churn")
st.caption("Corte: 31-May-2026")

# Barra lateral 
with st.sidebar:
    st.header("Filtros")
    periodo = st.selectbox(
        "Periodo de Análisis",
        ["Últimos 30 días (Mayo)", "Últimos 60 días", "Trimestre Actual"],
    )
    segmento = st.selectbox("Segmento de Cuenta", ["Todos", "WAPI", "Basic"])
    asignado_cs = st.selectbox(
        "Asignado a CS (SAMU)", ["Todos", "Equipo A", "Equipo B"]
    )

# Contenedor visual
with st.container(border=True):
    f_col1, f_col2, f_col3, _ = st.columns([1.2, 1.2, 1.2, 1.4])
    with f_col1:
        st.selectbox(
            "Periodo de Análisis",
            ["Últimos 30 días (Mayo)", "Últimos 60 días", "Trimestre Actual"],
            key="top_periodo",
        )
    with f_col2:
        segmento_top = st.selectbox(
            "Segmento de Cuenta",
            ["Todos", "WAPI", "Basic"],
            key="top_segmento",
        )
    with f_col3:
        st.selectbox(
            "Asignado a CS (SAMU)",
            ["Todos", "Equipo A", "Equipo B"],
            key="top_cs",
        )

# Prioriza el filtro superior
filtro_seg = segmento_top if segmento_top != "Todos" else segmento

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.metric(
            label="Tasa Churn Mensual (K01)",
            value="7.8%",
            delta="0.7% vs mes anterior",
            delta_color="inverse",
        )

with col2:
    with st.container(border=True):
        st.metric(
            label="MRR en Riesgo (Y04)",
            value="$4,520",
            delta="$310 USD vs mes anterior",
            delta_color="inverse",
        )

with col3:
    with st.container(border=True):
        st.metric(
            label="Cuentas Inactivas (Zombie)",
            value="197",
            delta="8% del total de cartera",
            delta_color="off",
        )

with col4:
    with st.container(border=True):
        st.metric(
            label="Retención (Observacional)",
            value="82%",
            delta="Cuentas retenidas post-SAMU",
            delta_color="normal",
        )

st.write("")

#graficas
graf_col1, graf_col2 = st.columns(2)

with graf_col1:
    st.subheader("Distribución de Adopción de Cuentas (Frecuencia)")
    df_adopcion = pd.DataFrame({
        "Rango": [
            "[0d] Zombie",
            "[1-7d] Baja",
            "[8-14d] Med",
            "[15-21d] Alt",
            "[22-31d] Int",
        ],
        "Cuentas": [197, 65, 310, 390, 280],
        "Color": ["Rojo", "Gris", "Azul", "Azul", "Azul"],
    })

    fig_adopcion = px.bar(
        df_adopcion,
        x="Rango",
        y="Cuentas",
        color="Color",
        color_discrete_map={
            "Rojo": "#E74C3C",
            "Gris": "#5D6D7E",
            "Azul": "#4A77B5",
        },
        labels={
            "Rango": "Eje X: Días Activos del Mes (F01)",
            "Cuentas": "# Cuentas",
        },
    )
    fig_adopcion.update_layout(
        showlegend=False, height=320, margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_adopcion, use_container_width=True)

with graf_col2:
    st.subheader("Causa Probable de Churn (En Riesgo)")
    df_causas = pd.DataFrame({
        "Causa": [
            "Intención Declarada",
            "Downgrade de Plan",
            "Falta de Resultados",
            "Problema Técnico",
        ],
        "Valor": [45, 85, 130, 185],
        "Detalle": ["(F18/F19)", "(F30)", "(F03 leads ↓)", "(F15 bug)"],
        "Color": ["Rojo", "Gris", "Gris", "Azul"],
    })

    fig_causas = px.bar(
        df_causas,
        x="Valor",
        y="Causa",
        orientation="h",
        text="Detalle",
        color="Color",
        color_discrete_map={
            "Rojo": "#C0392B",
            "Gris": "#616A6B",
            "Azul": "#3B69B1",
        },
        labels={"Valor": "", "Causa": ""},
    )
    fig_causas.update_traces(textposition="outside")
    fig_causas.update_layout(
        showlegend=False,
        height=320,
        margin=dict(t=20, b=20, r=80),
        xaxis=dict(showticklabels=False, showgrid=False, range=[0, 240]),
    )
    st.plotly_chart(fig_causas, use_container_width=True)

#tabla
st.subheader("Top Cuentas Priorizadas para Intervención (PRS-01)")

df_cuentas = pd.DataFrame({
    "Cuenta (account_id)": [
        "PyME Textil (WS-03115)",
        "Restaurante Don J. (WS-00112)",
        "Clínica Dental (WS-03234)",
    ],
    "Segmento": ["WAPI", "Basic", "WAPI"],
    "Pérdida Esperada": ["$315 USD", "$117 USD", "$195 USD"],
    "Probabilidad Churn": [
        "62% (Alta)",
        "45% (Zombie F09)",
        "80% (Intención F18)",
    ],
    "Causa Probable": [
        "Técnica (F15 + Sentim ↓)",
        "Falta de Resultados",
        "Precio o Plan",
    ],
    "Acción Sugerida (D3)": [
        "Escalar Soporte",
        "Agendar Capacitación",
        "Ofrecer Descuento",
    ],
})

if filtro_seg != "Todos":
    df_cuentas = df_cuentas[df_cuentas["Segmento"] == filtro_seg]

# Agrupación del detalle usando st.tabs (requisito de la tabla)
tab_todas, tab_wapi, tab_basic = st.tabs(
    ["Todas las cuentas", "Segmento WAPI", "Segmento Basic"]
)

with tab_todas:
    st.dataframe(df_cuentas, use_container_width=True, hide_index=True)

with tab_wapi:
    st.dataframe(
        df_cuentas[df_cuentas["Segmento"] == "WAPI"],
        use_container_width=True,
        hide_index=True,
    )

with tab_basic:
    st.dataframe(
        df_cuentas[df_cuentas["Segmento"] == "Basic"],
        use_container_width=True,
        hide_index=True,
    )