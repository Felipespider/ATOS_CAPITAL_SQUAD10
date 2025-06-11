import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Exemplo de dados
df = pd.DataFrame({
    'mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'vendas_2024': [100, 120, 130, 110, 150, 170],
    'vendas_2025': [110, 125, 140, 130, 160, 180],
})

# Cria o gráfico
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['mês'], y=df['vendas_2024'], mode='lines+markers', name='Vendas 2024')) # Adiciona linha para vendas 2024
fig.add_trace(go.Scatter(x=df['mês'], y=df['vendas_2025'], mode='lines+markers', name='Vendas 2025')) # Adiciona linha para vendas 2025
fig.add_trace(go.Bar(x=df['mês'], y=df['vendas_2024'], name='Vendas 2024', opacity=0.5)) # Adiciona barra para vendas 2024

fig.update_layout(title='Comparativo de Vendas', xaxis_title='Mês', yaxis_title='Vendas')

# Exibe no Streamlit
st.plotly_chart(fig)
