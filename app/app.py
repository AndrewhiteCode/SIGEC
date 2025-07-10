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

# ✅ Clasificador de CPU
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

# 🟢 Sidebar fijo con KEYS ÚNICOS
st.sidebar.title('Menú')
if st.sidebar.button('🏠 Home', key="home_btn"):
    st.session_state.page = 'home'
if st.sidebar.button('Individual', key="individual_btn"):
    st.session_state.page = 'sala'
if st.sidebar.button('📊 Comparación', key="comparacion_btn"):
    st.session_state.page = 'comparacion'
if st.sidebar.button('📝 Resumen', key="resumen_btn"):
    st.session_state.page = 'resumen'

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

    # === Detectar CPU ===
    cpu_name = 'Desconocido'
    idx_cpu = df.apply(lambda row: row.astype(str).str.contains('CPU').any(), axis=1)
    if idx_cpu.any():
        fila_cpu = df[idx_cpu].iloc[0]
        for celda in fila_cpu:
            if isinstance(celda, str) and 'CPU' in celda:
                cpu_name = celda.strip()
                break
        df = df[~idx_cpu]

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

# ===============================
# RESUMEN GLOBAL
# ===============================
elif st.session_state.page == 'resumen':
    st.header("📑 Resumen General de Computadores")

    DATA_DIR = "./data"
    resumen = []

    salas = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]

    for sala in salas:
        sala_path = os.path.join(DATA_DIR, sala)
        archivos = glob.glob(os.path.join(sala_path, "*.csv"))
        for archivo in archivos:
            df = pd.read_csv(archivo, encoding="utf-8-sig")
            # Detectar CPU
            cpu_name = 'Desconocido'
            idx_cpu = df.apply(lambda row: row.astype(str).str.contains('CPU').any(), axis=1)
            if idx_cpu.any():
                fila_cpu = df[idx_cpu].iloc[0]
                for celda in fila_cpu:
                    if isinstance(celda, str) and 'CPU' in celda:
                        cpu_name = celda.strip()
                        break
                df = df[~idx_cpu]

            df['Temperaturas núcleo (avg) [°C]'] = pd.to_numeric(df['Temperaturas núcleo (avg) [°C]'], errors='coerce')
            df['Relojes núcleo (avg) [MHz]'] = pd.to_numeric(df['Relojes núcleo (avg) [MHz]'], errors='coerce')

            temp_prom = df['Temperaturas núcleo (avg) [°C]'].mean()
            temp_max = df['Temperaturas núcleo (avg) [°C]'].max()
            reloj_prom = df['Relojes núcleo (avg) [MHz]'].mean()

            resumen.append({
                'Sala': sala,
                'Archivo': os.path.basename(archivo),
                'CPU': clasificar_cpu(cpu_name),
                'Temp_Promedio': temp_prom,
                'Temp_Max': temp_max,
                'Reloj_Promedio': reloj_prom
            })

    resumen_df = pd.DataFrame(resumen)

    st.subheader("📊 Tabla Resumen")
    st.dataframe(resumen_df)

    mejor_pc = resumen_df.loc[resumen_df['Temp_Promedio'].idxmin()]
    peor_temp_pc = resumen_df.loc[resumen_df['Temp_Max'].idxmax()]
    mejor_reloj_pc = resumen_df.loc[resumen_df['Reloj_Promedio'].idxmax()]

    st.subheader("📌 Conclusiones")
    st.markdown(f"""
    - ✅ **Mejor computador (menor temperatura promedio)**: `{mejor_pc['CPU']}` en sala `{mejor_pc['Sala']}` (`{mejor_pc['Archivo']}`) con `{mejor_pc['Temp_Promedio']:.2f} °C` promedio.
    - 🔥 **Mayor temperatura máxima alcanzada**: `{peor_temp_pc['CPU']}` en sala `{peor_temp_pc['Sala']}` (`{peor_temp_pc['Archivo']}`) con `{peor_temp_pc['Temp_Max']:.2f} °C`.
    - ⚡ **Procesador más eficiente (mayor reloj promedio)**: `{mejor_reloj_pc['CPU']}` en sala `{mejor_reloj_pc['Sala']}` (`{mejor_reloj_pc['Archivo']}`) con `{mejor_reloj_pc['Reloj_Promedio']:.2f} MHz`.
    """)

# ===============================
# COMPARACION MULTIPLE
# ===============================
elif st.session_state.page == 'comparacion':
    st.header("🔎 Comparación de Computadores")

    import plotly.express as px

    DATA_DIR = "./data"

    pcs = []
    salas = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    for sala in salas:
        sala_path = os.path.join(DATA_DIR, sala)
        archivos = glob.glob(os.path.join(sala_path, "*.csv"))
        for archivo in archivos:
            pcs.append(f"{sala}/{os.path.basename(archivo)}")

    seleccionados = st.multiselect(
        "Selecciona entre 2 y 10 computadores para comparar:",
        pcs
    )

    if len(seleccionados) < 2:
        st.info("Selecciona al menos 2 computadores para comparar.")
    elif len(seleccionados) > 10:
        st.warning("Selecciona máximo 10 computadores.")
    else:
        dfs = []
        for pc in seleccionados:
            sala, archivo = pc.split("/")
            archivo_path = os.path.join(DATA_DIR, sala, archivo)
            df = pd.read_csv(archivo_path, encoding="utf-8-sig")

            cpu_name = 'Desconocido'
            idx_cpu = df.apply(lambda row: row.astype(str).str.contains('CPU').any(), axis=1)
            if idx_cpu.any():
                fila_cpu = df[idx_cpu].iloc[0]
                for celda in fila_cpu:
                    if isinstance(celda, str) and 'CPU' in celda:
                        cpu_name = celda.strip()
                        break
                df = df[~idx_cpu]

            df['CPU'] = clasificar_cpu(cpu_name)
            df['Sala'] = sala
            df['Archivo'] = archivo

            df['Temperaturas núcleo (avg) [°C]'] = pd.to_numeric(df['Temperaturas núcleo (avg) [°C]'], errors='coerce')
            df['Relojes núcleo (avg) [MHz]'] = pd.to_numeric(df['Relojes núcleo (avg) [MHz]'], errors='coerce')
            df['Uso núcleo (avg) [%]'] = pd.to_numeric(df['Uso núcleo (avg) [%]'], errors='coerce')

            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                if df['Date'].iloc[0] > df['Date'].iloc[-1]:
                    df = df.iloc[::-1].reset_index(drop=True)

            df['Tiempo'] = range(1, len(df) + 1)
            df['PC'] = f"{sala}/{archivo}"

            dfs.append(df)

        df_comparacion = pd.concat(dfs, ignore_index=True)

        st.subheader("🌡️ Comparación Temperatura vs Tiempo")
        fig_temp = px.line(
            df_comparacion,
            x="Tiempo",
            y="Temperaturas núcleo (avg) [°C]",
            color="PC",
            labels={"Temperaturas núcleo (avg) [°C]": "Temperatura [°C]"}
        )
        st.plotly_chart(fig_temp, use_container_width=True)

        st.subheader("⏲️ Comparación Reloj vs Tiempo")
        fig_reloj = px.line(
            df_comparacion,
            x="Tiempo",
            y="Relojes núcleo (avg) [MHz]",
            color="PC",
            labels={"Relojes núcleo (avg) [MHz]": "Reloj [MHz]"}
        )
        st.plotly_chart(fig_reloj, use_container_width=True)

        st.subheader("💻 Comparación Uso vs Tiempo")
        fig_uso = px.line(
            df_comparacion,
            x="Tiempo",
            y="Uso núcleo (avg) [%]",
            color="PC",
            labels={"Uso núcleo (avg) [%]": "Uso [%]"}
        )
        st.plotly_chart(fig_uso, use_container_width=True)

        resumen = []
        for df in dfs:
            temp_prom = df['Temperaturas núcleo (avg) [°C]'].mean()
            temp_max = df['Temperaturas núcleo (avg) [°C]'].max()
            reloj_prom = df['Relojes núcleo (avg) [MHz]'].mean()

            resumen.append({
                'PC': df['PC'].iloc[0],
                'Sala': df['Sala'].iloc[0],
                'CPU': df['CPU'].iloc[0],
                'Temp_Promedio': temp_prom,
                'Temp_Max': temp_max,
                'Reloj_Promedio': reloj_prom
            })

        resumen_df = pd.DataFrame(resumen)
        st.subheader("📊 Tabla Resumen de Comparación")
        st.dataframe(resumen_df)

        mejor_pc = resumen_df.loc[resumen_df['Temp_Promedio'].idxmin()]
        peor_temp_pc = resumen_df.loc[resumen_df['Temp_Max'].idxmax()]
        mejor_reloj_pc = resumen_df.loc[resumen_df['Reloj_Promedio'].idxmax()]

        st.subheader("📌 Conclusiones de la Comparación")
        st.markdown(f"""
        - ✅ **Mejor computador (menor temperatura promedio)**: `{mejor_pc['CPU']}` en sala `{mejor_pc['Sala']}` (`{mejor_pc['PC']}`) con `{mejor_pc['Temp_Promedio']:.2f} °C` promedio.
        - 🔥 **Mayor temperatura máxima alcanzada**: `{peor_temp_pc['CPU']}` en sala `{peor_temp_pc['Sala']}` (`{peor_temp_pc['PC']}`) con `{peor_temp_pc['Temp_Max']:.2f} °C`.
        - ⚡ **Procesador más eficiente (mayor reloj promedio)**: `{mejor_reloj_pc['CPU']}` en sala `{mejor_reloj_pc['Sala']}` (`{mejor_reloj_pc['PC']}`) con `{mejor_reloj_pc['Reloj_Promedio']:.2f} MHz`.
        """)

