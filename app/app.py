import streamlit as st
import pandas as pd
import glob
import os

import graficas_globales
import graficas_sala

st.set_page_config(page_title="SIGEC", layout="wide")

# 🟢 Si no hay page: que abra Home por defecto
if 'page' not in st.session_state:
    st.session_state.page = 'home'

st.sidebar.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        height: 50px;
        width: 200px;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ Aquí defines la función al inicio
def clasificar_cpu(cpu_full):
    cpu_full = cpu_full.lower()
    if '13th' in cpu_full or '13700' in cpu_full:
        return 'Intel Core i7-13700'
    elif '12th' in cpu_full or '12700' in cpu_full:
        return 'Intel Core i7-12700'
    elif 'i9' in cpu_full and '10900' in cpu_full:
        return 'Intel Core i9-10900X'
    elif 'i5' in cpu_full and '6400' in cpu_full:
        return 'Intel Core i5-6400'
    elif 'ryzen' in cpu_full and '3700' in cpu_full:
        return 'AMD Ryzen 7 3700X'
    else:
        return 'Intel Core i5-6200U'
# 🟢 Sidebar fijo
st.sidebar.title('Menú')
if st.sidebar.button('🏠 Home'):
    st.session_state.page = 'home'

if st.sidebar.button('Individual'):
    st.session_state.page = 'sala'

# ===============================
# HOME (Gráficas Globales)
# ===============================
if st.session_state.page == 'home':
    st.header('📊 Gráficas Globales Interactivas')

    st.plotly_chart(graficas_globales.grafica_temperatura())
    st.plotly_chart(graficas_globales.grafica_relojes())
    st.plotly_chart(graficas_globales.grafica_uso())
    st.plotly_chart(graficas_globales.grafica_boxplot_temp())
    st.plotly_chart(graficas_globales.grafica_dispersion_temp_uso())

# ===============================
# SALA / PC (Análisis Individual)
# ===============================
elif st.session_state.page == 'sala':
    st.header("🔍 Análisis por Computador")

    DATA_DIR = "./data"

    salas = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    sala = st.sidebar.selectbox("Selecciona una Sala", salas)

    sala_path = os.path.join(DATA_DIR, sala)
    archivos = glob.glob(os.path.join(sala_path, "*.csv"))
    archivos_nombres = [os.path.basename(a) for a in archivos]

    archivo = st.sidebar.selectbox("Selecciona un PC", archivos_nombres)

    df = pd.read_csv(os.path.join(sala_path, archivo), encoding="utf-8-sig")

    # === Detectar CPU de la misma forma ===
    cpu_name = 'Desconocido'
    idx_cpu = df.apply(lambda row: row.astype(str).str.contains('CPU').any(), axis=1)
    if idx_cpu.any():
        fila_cpu = df[idx_cpu].iloc[0]
        for celda in fila_cpu:
            if isinstance(celda, str) and 'CPU' in celda:
                cpu_name = celda.strip()
                break
        df = df[~idx_cpu]  # Opcional: borrar fila CPU si quieres

    df['CPU'] = cpu_name
    df['CPU_Short'] = clasificar_cpu(cpu_name)

    # === Procesar ===
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if df['Date'].iloc[0] > df['Date'].iloc[-1]:
            df = df.iloc[::-1].reset_index(drop=True)

    df['Temperaturas núcleo (avg) [°C]'] = pd.to_numeric(df['Temperaturas núcleo (avg) [°C]'], errors='coerce')
    df['Relojes núcleo (avg) [MHz]'] = pd.to_numeric(df['Relojes núcleo (avg) [MHz]'], errors='coerce')
    df['Uso núcleo (avg) [%]'] = pd.to_numeric(df['Uso núcleo (avg) [%]'], errors='coerce')

    df['Tiempo'] = range(1, len(df) + 1)

    fecha_inicio = df['Date'].min().strftime("%Y-%m-%d") if 'Date' in df.columns else 'Sin fecha'

    # === Mostrar Info ===
    st.subheader(f"📄 Información del Computador")
    st.markdown(f"""
    - **Nombre archivo:** `{archivo}`
    - **Procesador:** `{df['CPU_Short'].iloc[0]}`
    - **Fecha de muestra:** `{fecha_inicio}`
    """)

    # === Graficas ===
    st.subheader("🌡️ Temperatura núcleo")
    st.plotly_chart(graficas_sala.grafica_temperatura(df))

    st.subheader("⏲️ Relojes núcleo")
    st.plotly_chart(graficas_sala.grafica_relojes(df))

    st.subheader("💻 Uso núcleo")
    st.plotly_chart(graficas_sala.grafica_uso(df))



