import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc

st.set_page_config(layout="wide")
st.title("📊 Dashboard de Vendas por Filial")

# Função de conexão ao banco
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

# Carregando dados
df = carregar_dados()
df.rename(columns={"nmFilial": "FILIAL", "vlVenda": "VENDAS_2024"}, inplace=True)

# Garantindo tipo datetime na data da venda
df["dtVenda"] = pd.to_datetime(df["dtVenda"])

# Criando coluna de mês (ex: "2025-03")
df["MES"] = df["dtVenda"].dt.to_period("M").astype(str)

# Sidebar para escolha do mês
meses_disponiveis = sorted(df["MES"].unique())
mes_selecionado = st.sidebar.selectbox("🗓️ Selecione o mês", meses_disponiveis)

# Filtrar o DataFrame pelo mês selecionado
df_mes = df[df["MES"] == mes_selecionado]

# Agrupando por FILIAL (dados consolidados por mês)
df_agg = df_mes.groupby("FILIAL", as_index=False).agg({
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

# Abas de visualização
tab1, tab2, tab3 = st.tabs(["📈 Comparativos Gerais", "📊 Acumulados & Diários", "📉 Crescimentos"])

with tab1:
    st.subheader("📌 Comparativo de Vendas x Meta x Previsão")
    fig1 = px.bar(
        df_agg,
        x="FILIAL",
        y=["VENDAS_2024", "META_MES", "PREVISAO"],
        barmode="group",
        title=f"Vendas vs Meta vs Previsão – {mes_selecionado}",
        labels={"value": "Valor em R$", "FILIAL": "Filial"},
        color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"]
    )
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Acumulado: Vendas, Meta e 2024")
        fig2 = px.bar(
            df_agg,
            x="FILIAL",
            y=["ACUM_2024", "ACUM_META", "ACUM_VENDAS"],
            barmode="group",
            title="Acumulado Anual por Filial",
            labels={"value": "Valor em R$", "FILIAL": "Filial"},
            color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96"]
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("📆 Vendas do Dia")
        fig3 = px.bar(
            df_agg,
            x="FILIAL",
            y="VENDAS_DO_DIA",
            title="Vendas do Dia por Filial",
            labels={"VENDAS_DO_DIA": "Valor em R$", "FILIAL": "Filial"},
            color="FILIAL",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Crescimento das Vendas em 2025 (%)")
        fig4 = px.bar(
            df_agg,
            x="FILIAL",
            y="CRESC_2025",
            title="Crescimento 2025 vs 2024",
            labels={"CRESC_2025": "Crescimento (%)", "FILIAL": "Filial"},
            color="CRESC_2025",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        st.subheader("🎯 Crescimento da Meta (%)")
        fig5 = px.bar(
            df_agg,
            x="FILIAL",
            y="CRESC_META",
            title="Crescimento da Meta por Filial",
            labels={"CRESC_META": "Crescimento (%)", "FILIAL": "Filial"},
            color="CRESC_META",
            color_continuous_scale="Oranges"
        )
        st.plotly_chart(fig5, use_container_width=True)




# df.rename(columns={"nmFilial": "FILIAL", "vlVenda": "VENDAS_2024"}, inplace=True)