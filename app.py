import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Dashboard Interactivo de Ventas y Rentabilidad", layout="wide")


@st.cache_data
def load_data():
    excel_path = Path(__file__).resolve().parent / "SalidaVentas.xlsx"
    if not excel_path.exists():
        st.error(f"No se encontró el archivo: {excel_path.name}")
        return pd.DataFrame()

    df = pd.read_excel(excel_path)
    return df


df = load_data()

if df.empty:
    st.warning("No hay datos para mostrar. Verifica que el archivo 'SalidaVentas.xlsx' exista en la misma carpeta que app.py.")
    st.stop()

required_columns = {"Region", "State", "Category", "Sub-Category", "Sales", "Profit", "Discount"}
missing_columns = sorted(required_columns - set(df.columns))
if missing_columns:
    st.error(f"Faltan columnas requeridas en el archivo: {', '.join(missing_columns)}")
    st.stop()

# --- PANEL DE CONTROL Y FILTROS ---
st.sidebar.title("📌 Panel de Control y Filtros")
region_sel = st.sidebar.multiselect("Región:", options=df["Region"].dropna().unique(), default=df["Region"].dropna().unique())
state_sel = st.sidebar.multiselect("Estado:", options=df["State"].dropna().unique(), default=df["State"].dropna().unique())
categoria_sel = st.sidebar.multiselect("Categoría de Producto:", options=df["Category"].dropna().unique(), default=df["Category"].dropna().unique())

df_filt = df[
    (df["Region"].isin(region_sel)) &
    (df["State"].isin(state_sel)) &
    (df["Category"].isin(categoria_sel))
].copy()

# --- TÍTULO Y MÉTRICAS ---
st.title("📊 Dashboard Interactivo de Ventas y Rentabilidad")
st.markdown("Explora el rendimiento comercial, márgenes y áreas de oportunidad en tiempo real.")

col1, col2, col3, col4 = st.columns(4)

total_sales = float(df_filt["Sales"].sum())
total_profit = float(df_filt["Profit"].sum())
margin = (total_profit / total_sales * 100) if total_sales else 0.0
total_tx = int(len(df_filt))

col1.metric("🛒 Ventas Totales", f"${total_sales:,.2f}")
col2.metric("💵 Ganancia Neta", f"${total_profit:,.2f}")
col3.metric("📈 % de Margen", f"{margin:.2f}%")
col4.metric("📦 Total de Transacciones", f"{total_tx:,}")

st.markdown("---")

# --- GRÁFICAS ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📌 Ventas por Subcategoría")
    subcat_df = (
        df_filt.groupby("Sub-Category", as_index=False)
        .agg(Ventas=("Sales", "sum"), Ganancia=("Profit", "sum"))
        .sort_values("Ventas", ascending=False)
    )

    fig_bar = px.bar(
        subcat_df,
        x="Sub-Category",
        y="Ventas",
        color="Ganancia",
        color_continuous_scale="RdYlGn",
        labels={"Sub-Category": "Subcategoría", "Ventas": "Ventas Totales", "Ganancia": "Ganancia"},
        title="Ventas por Subcategoría"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_graf2:
    st.subheader("📉 Descuento vs. Ganancia")
    fig_scatter = px.scatter(
        df_filt,
        x="Discount",
        y="Profit",
        color="Category",
        labels={"Discount": "Descuento (%)", "Profit": "Ganancia ($)", "Category": "Categoría"},
        title="Relación entre Descuento y Ganancia"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
