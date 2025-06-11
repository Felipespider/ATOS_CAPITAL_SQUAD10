import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc
from PIL import Image

st.set_page_config(layout="wide")
st.title("📊 Dashboard de Vendas por Filial")

@st.cache_data
def carregar_dados():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=aquidaba.infonet.com.br;"
        f"DATABASE=dbproinfo;"
        f"UID=leituraVendas;"
        f"PWD=KRphDP65BM"
    )
    conn = pyodbc.connect(conn_str)
    query = "SELECT * FROM tbVendasDashboard"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Carregamento e preparação
df = carregar_dados()
df.rename(columns={"nmFilial": "FILIAL", "vlVenda": "VENDAS_2024"}, inplace=True)
df["dtVenda"] = pd.to_datetime(df["dtVenda"])
df["MES"] = df["dtVenda"].dt.to_period("M").astype(str)

# Agrupando por mês e filial
df_agg = df.groupby(["FILIAL", "MES"], as_index=False).agg({
    "VENDAS_2024": "sum"
})
df_agg["META_MES"] = df_agg["VENDAS_2024"] * 0.05
df_agg["PREVISAO"] = df_agg["VENDAS_2024"] * 1.05
df_agg["ACUM_2024"] = df_agg["VENDAS_2024"] * 0.85
df_agg["ACUM_META"] = df_agg["META_MES"] * 0.9
df_agg["ACUM_VENDAS"] = df_agg["VENDAS_2024"] * 0.92
df_agg["VENDAS_DO_DIA"] = df_agg["VENDAS_2024"] * 0.03
df_agg["CRESC_2025"] = 5 + (df_agg["VENDAS_2024"] % 10)
df_agg["CRESC_META"] = 3 + (df_agg["META_MES"] % 5)

logo = Image.open("ATOS CAPITAL BRANCO.png")
st.sidebar.image(logo, use_container_width=True)
# Sidebar com seleção da filial
filiais = sorted(df_agg["FILIAL"].unique())
filial_selecionada = st.sidebar.selectbox("🏬 Selecione a filial", filiais)

df_filial = df_agg[df_agg["FILIAL"] == filial_selecionada]

# Gráficos
st.subheader(f"📆 Evolução Mensal – {filial_selecionada}")

tab1, tab2, tab3 = st.tabs(["📈 Vendas vs Meta", "📊 Acumulados", "📉 Crescimento"])

with tab1:
    fig1 = px.bar(df_filial, x="MES", y=["VENDAS_2024", "META_MES", "PREVISAO"],
                  barmode="group", title="Vendas x Meta x Previsão",
                  labels={"value": "R$", "MES": "Mês"})
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = px.bar(
    df_filial,
    x="MES",
    y=["ACUM_2024", "ACUM_META", "ACUM_VENDAS"],
    barmode="group",
    title="Acumulados Mensais",
    labels={"value": "R$", "MES": "Mês"},
    color_discrete_sequence=["#FF7F0E", "#1F77B4", "#2CA02C"]  # Laranja, Azul, Verde
)
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.line(df_filial, x="MES", y="VENDAS_DO_DIA",
                   title="Média de Vendas Diárias no Mês",
                   labels={"VENDAS_DO_DIA": "R$", "MES": "Mês"})
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    fig4 = px.bar(df_filial, x="MES", y="CRESC_2025",
                  title="Crescimento 2025 vs 2024",
                  labels={"CRESC_2025": "%", "MES": "Mês"},
                  color_discrete_sequence=["#1f77b4"])
                
    st.plotly_chart(fig4, use_container_width=True)

    fig5 = px.bar(df_filial, x="MES", y="CRESC_META",
                  title="Crescimento da Meta",
                  labels={"CRESC_META": "%", "MES": "Mês"},
                  color_discrete_sequence=["#ff7f0e"])
    st.plotly_chart(fig5, use_container_width=True)



# df.rename(columns={"nmFilial": "FILIAL", "vlVenda": "VENDAS_2024"}, inplace=True)