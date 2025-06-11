import streamlit as st
import plotly.express as px
import pandas as pd
import pyodbc

# Conexão com o banco
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
    df = pd.read_sql(query, conn) #aqui é um dataframe em uma variável que ele vai ler qualquer query e conection
    conn.close()
    return df

# Carregando os dados
df = carregar_dados()

st.title("📊 Dashboard de Vendas por Filial")

# Exibir a tabela bruta (só pra teste agora)
st.dataframe(df)

# --- Tratamento de datas e criação de colunas auxiliares ---
df['dtVenda'] = pd.to_datetime(df['dtVenda'])
df['Ano'] = df['dtVenda'].dt.year
df['Mes'] = df['dtVenda'].dt.month
df['Ano-Mes'] = df['dtVenda'].dt.to_period('M').astype(str)

# --- Filtrando apenas dados de 2024 ---
df_2024 = df[df['Ano'] == 2024]

# --- Agrupando por filial e mês para somar as vendas ---
df_grouped = df_2024.groupby(['nmFilial', 'Ano-Mes']).agg({
    'vlVenda': 'sum'
}).reset_index().rename(columns={
    'nmFilial': 'Filial',
    'vlVenda': 'Vendas'
})

# --- Calculando a meta: 5% das vendas por mês ---
df_grouped['Meta'] = df_grouped['Vendas'] * 0.05

# --- Ordenando para facilitar os acumulados ---
df_grouped = df_grouped.sort_values(by=['Filial', 'Ano-Mes'])

# --- Calculando acumulados por filial ---
df_grouped['Acum_Vendas'] = df_grouped.groupby('Filial')['Vendas'].cumsum()
df_grouped['Acum_Meta'] = df_grouped.groupby('Filial')['Meta'].cumsum()

# --- Exibindo o DataFrame tratado ---
st.dataframe(df_grouped)

# Filtro lateral para escolher a filial
filial_selecionada = st.sidebar.selectbox("Selecione a Filial", df_grouped["Filial"].unique())

# Filtrando os dados da filial selecionada
df_filial = df_grouped[df_grouped["Filial"] == filial_selecionada]

# Gráfico de barras: Vendas x Meta por mês
fig = px.bar(
    df_filial,
    x="Ano-Mes",
    y=["Vendas", "Meta"],
    barmode="group",
    title=f"Vendas x Meta - {filial_selecionada}",
    labels={"value": "R$", "Ano-Mes": "Mês", "variable": "Indicador"}
)

st.plotly_chart(fig, use_container_width=True)


