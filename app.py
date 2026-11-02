import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Interactivo de Ventas y Rentabilidad", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel('SalidaVentas.xlsx')

df = load_data()

# --- PANEL DE CONTROL Y FILTROS ---
st.sidebar.title("📌 Panel de Control y Filtros")

region_sel = st.sidebar.multiselect("Región:", df['Region'].unique(), df['Region'].unique())
estado_sel = st.sidebar.multiselect("Estado:", df['State'].unique(), df['State'].unique())
categoria_sel = st.sidebar.multiselect("Categoría de Producto:", df['Category'].unique(), df['Category'].unique())

df_filt = df[
    (df['Region'].isin(region_sel)) &
    (df['State'].isin(estado_sel)) &
    (df['Category'].isin(categoria_sel))
]

# --- TÍTULO Y MÉTRICAS ---
st.title("📊 Dashboard Interactivo de Ventas y Rentabilidad")
st.markdown("Explora el rendimiento comercial, márgenes y áreas de oportunidad en tiempo real.")

col1, col2, col3, col4 = st.columns(4)

total_sales = df_filt['Sales'].sum()
total_profit = df_filt['Profit'].sum()
margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
total_tx = len(df_filt)

col1.metric("🛒 Ventas Totales", f"${total_sales:,.2f}")
col2.metric("💵 Ganancia/Pérdida Neta", f"${total_profit:,.2f}")
col3.metric("📈 % Margen General Promedio", f"{margin:.2f}%")
col4.metric("📦 Transacciones", f"{total_tx:,}")

st.markdown("---")

# --- GRÁFICAS ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📌 Ventas y Ganancias por Subcategoría")
    subcat_df = df_filt.groupby('Sub-Category')[['Sales', 'Profit']].sum().reset_index().sort_values(by='Sales', ascending=False)
    fig_bar = px.bar(
        subcat_df, 
        x='Sub-Category', 
        y='Sales', 
        color='Profit', 
        color_continuous_scale='RdYlGn',
        labels={'Sales': 'Ventas Totales'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_graf2:
    st.subheader("📉 Curva de Impacto del Descuento en Rentabilidad")
    fig_scatter = px.scatter(
        df_filt, 
        x='Discount', 
        y='Profit', 
        color='Category',
        labels={'Discount': 'Relación entre Descuento (%)', 'Profit': 'Ganancia ($)'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
