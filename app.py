import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Control de Gastos y Ahorro", page_icon="💰", layout="wide")

st.title("📊 Panel de Control Financiero y Ahorro")
st.markdown("Gestiona tus finanzas personales conectadas con tu Google Sheet y tu Atajo de iPhone.")

# Reemplaza esto con el ID real de tu Google Sheet (lo encuentras en la URL de tu hoja)
# Ejemplo de URL: https://docs.google.com/spreadsheets/d/AQUI_ESTA_EL_ID/edit
SHEET_ID = st.secrets.get("SHEET_ID", "TU_SHEET_ID_AQUÍ")
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Transacciones"

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(url)
        # Limpiar espacios en los nombres de las columnas por si acaso
        df.columns = df.columns.str.strip()
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"No se pudieron cargar los datos. Asegúrate de que la hoja sea pública para lectura ('Cualquier persona con el enlace'). Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Filtros de mes/año
    df['Mes'] = df['Fecha'].dt.to_period('M').astype(str)
    meses_disponibles = sorted(df['Mes'].unique(), reverse=True)
    
    mes_seleccionado = st.sidebar.selectbox("Selecciona el Mes", meses_disponibles)
    df_filtrado = df[df['Mes'] == mes_seleccionado]
    
    # Métricas principales
    ingresos_totales = df_filtrado[df_filtrado['Tipo'].str.lower() == 'ingreso']['Monto'].sum()
    gastos_totales = df_filtrado[df_filtrado['Tipo'].str.lower() == 'gasto']['Monto'].sum()
    ahorro_actual = ingresos_totales - gastos_totales
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos Totales", f"${ingresos_totales:,.2f}")
    col2.metric("Gastos Totales", f"${gastos_totales:,.2f}", delta=f"-${gastos_totales:,.2f}", delta_color="inverse")
    col3.metric("Ahorro Neto del Mes", f"${ahorro_actual:,.2f}")
    
    st.divider()
    
    # Gráficos
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Gastos por Categoría")
        df_gastos = df_filtrado[df_filtrado['Tipo'].str.lower() == 'gasto']
        if not df_gastos.empty:
            fig_cat = px.pie(df_gastos, names='Categoria', values='Monto', hole=0.4, title="Distribución de Egresos")
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No hay gastos registrados en este mes.")
            
    with col_g2:
        st.subheader("Evolución Diaria de Gastos")
        if not df_gastos.empty:
            df_diario = df_gastos.groupby(df_gastos['Fecha'].dt.date)['Monto'].sum().reset_index()
            fig_line = px.line(df_diario, x='Fecha', y='Monto', markers=True, title="Gastos por Día")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No hay datos suficientes para mostrar la evolución.")
            
    st.subheader("Historial de Transacciones del Mes")
    st.dataframe(df_filtrado[['Fecha', 'Tipo', 'Categoria', 'Monto', 'Descripcion']], use_container_width=True)
else:
    st.warning("Aún no hay transacciones registradas o la hoja está vacía.")