# Cambios clave:
# - En Individual (sala): filtra df_filtrado = df[df['Tiempo'] <= 10]
# - En Comparación: filtra cada df antes de concatenar
# - El resto se mantiene igual

import streamlit as st
import pandas as pd
import glob
import os
import plotly.express as px

import graficas_globales
import graficas_sala

st.set_page_config(page_title="SIGEC", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #4CAF50; font-size: 48px;'>
        🧮 S.I.G.E.C
    </h1>
    <h4 style='text-align: center;'>
        Sistema Interactivo para Graficación Estadística Computacional
    </h4>
""", unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 'home'

st.sidebar.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        height: 50px;
        width: 200px;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

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

st.sidebar.title('Menú')
if st.sidebar.button('🏠 Home', key='home'):
    st.session_state.page = 'home'
if st.sidebar.button('Individual', key='individual'):
    st.session_state.page = 'sala'
if st.sidebar.button('📊 Comparación', key='comparacion'):
    st.session_state.page = 'comparacion'
if st.sidebar.button('📝 Resumen', key='resumen'):
    st.session_state.page = 'resumen'
if st.sidebar.button('ℹ️ Información', key='info'):
    st.session_state.page = 'info'

if st.session_state.page == 'home':
    st.header('📊 Gráficas Globales Interactivas')
    st.markdown("""
    En esta sección puedes ver gráficos generales que muestran cómo se comportan todos los computadores de forma conjunta.
    Estas gráficas permiten observar tendencias de temperatura, velocidad y uso de los procesadores durante las pruebas.
    """)

    st.plotly_chart(graficas_globales.grafica_temperatura())
    st.plotly_chart(graficas_globales.grafica_relojes())
    st.plotly_chart(graficas_globales.grafica_uso())
    st.plotly_chart(graficas_globales.grafica_boxplot_temp())
    st.plotly_chart(graficas_globales.grafica_dispersion_temp_uso())

elif st.session_state.page == 'sala':
    st.header("🔍 Análisis por Computador")
    st.markdown("""
    Aquí puedes elegir un computador específico para ver en detalle cómo ha funcionado.
    Podrás observar sus temperaturas, velocidad del procesador y nivel de uso a lo largo del tiempo.
    """)

    DATA_DIR = "./data"

    salas = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    sala = st.sidebar.selectbox("Selecciona una Sala", salas)

    sala_path = os.path.join(DATA_DIR, sala)
    archivos = glob.glob(os.path.join(sala_path, "*.csv"))
    archivos_nombres = [os.path.basename(a) for a in archivos]

    archivo = st.sidebar.selectbox("Selecciona un PC", archivos_nombres)

    df = pd.read_csv(os.path.join(sala_path, archivo), encoding="utf-8-sig")

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

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if df['Date'].iloc[0] > df['Date'].iloc[-1]:
            df = df.iloc[::-1].reset_index(drop=True)

    df['Temperaturas núcleo (avg) [°C]'] = pd.to_numeric(df['Temperaturas núcleo (avg) [°C]'], errors='coerce')
    df['Relojes núcleo (avg) [MHz]'] = pd.to_numeric(df['Relojes núcleo (avg) [MHz]'], errors='coerce')
    df['Uso núcleo (avg) [%]'] = pd.to_numeric(df['Uso núcleo (avg) [%]'], errors='coerce')

    df['Tiempo'] = df.index * 2

    df_filtrado = df[df['Tiempo'] <= 10]

    fecha_inicio = df['Date'].min().strftime("%Y-%m-%d") if 'Date' in df.columns else 'Sin fecha'

    st.subheader(f"📄 Información del Computador")
    st.markdown(f"""
    - **Nombre archivo:** `{archivo}`
    - **Procesador:** `{df['CPU_Short'].iloc[0]}`
    - **Fecha de muestra:** `{fecha_inicio}`
    """)

    st.subheader("🌡️ Temperatura núcleo")
    st.plotly_chart(graficas_sala.grafica_temperatura(df_filtrado))

    st.subheader("⏲️ Relojes núcleo")
    st.plotly_chart(graficas_sala.grafica_relojes(df_filtrado))

    st.subheader("💻 Uso núcleo")
    st.plotly_chart(graficas_sala.grafica_uso(df_filtrado))

elif st.session_state.page == 'comparacion':
    st.header("🔎 Comparación de Computadores")
    st.markdown("""
    En esta parte puedes seleccionar varios computadores y compararlos en gráficos interactivos.
    Así puedes ver fácilmente las diferencias de temperatura, velocidad y uso entre ellos.
    """)

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

            df['Tiempo'] = range(0, len(df)*2, 2)
            df = df[df['Tiempo'] <= 10]

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

    # ===============================
# RESUMEN GLOBAL
# ===============================
elif st.session_state.page == 'resumen':
    st.header("📑 Resumen General de Computadores")
    st.markdown("""
    Esta sección muestra un resumen de todos los computadores analizados.
    Aquí encontrarás conclusiones automáticas sobre cuál es el mejor, cuál alcanza la mayor temperatura y cuál es más eficiente.
    """)


    DATA_DIR = "./data"
    resumen = []

    salas = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]

    for sala in salas:
        sala_path = os.path.join(DATA_DIR, sala)
        archivos = glob.glob(os.path.join(sala_path, "*.csv"))
        for archivo in archivos:
            df = pd.read_csv(archivo, encoding="utf-8-sig")
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
    st.markdown("""
    En esta parte puedes seleccionar varios computadores y compararlos en gráficos interactivos.
    Así puedes ver fácilmente las diferencias de temperatura, velocidad y uso entre ellos.
    """)


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

            df['Tiempo'] = range(0, len(df)*2, 2)  # si es cada 2 seg

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

# ===============================
# INFORMACIÓN
# ===============================
elif st.session_state.page == 'info':
    st.markdown("""
   
    ### 🎯 **¿Para qué sirve esta aplicación?**

    **S.I.G.E.C** es una herramienta diseñada para **ayudar a analizar y entender el rendimiento de varios computadores** de forma sencilla y visual.  
    Permite ver, comparar y resumir datos reales de funcionamiento de procesadores, como su **temperatura**, **velocidad de reloj** y **uso de recursos**
    durante pruebas de esfuerzo.

    Esta aplicación está pensada para estudiantes, docentes y cualquier persona interesada en conocer cómo se comportan los equipos de nuestra Facultad,
    **sin necesidad de tener conocimientos avanzados en computación**.

    ---

    ### 🗂️ **Funciones principales**

    ✅ **1. Gráficas Globales**  
    Muestra gráficos generales de todos los computadores. Permite observar tendencias generales de temperatura, velocidad y uso de los núcleos.

    ✅ **2. Análisis Individual**  
    Permite seleccionar un computador específico para ver sus datos de forma detallada. Ideal para verificar si algún equipo necesita mantenimiento o revisión.

    ✅ **3. Comparación**  
    Permite elegir varios computadores (mínimo 2, máximo 10) y comparar su rendimiento en gráficos interactivos. 
    Así se puede ver cuál trabaja mejor o cuál podría tener problemas.

    ✅ **4. Resumen**  
    Entrega conclusiones automáticas. Por ejemplo, muestra cuál es el computador con mejor rendimiento, cuál se calienta más y cuál es más eficiente.


    ---

    ### 🔍 **Importancia**

    Con **S.I.G.E.C**, cualquier persona puede tomar **decisiones informadas** sobre el uso y mantenimiento de los computadores,
    ayudando a **optimizar recursos**, **detectar fallas** y **planificar mejoras**.  
    Además, fomenta el uso de la estadística aplicada y la toma de decisiones basada en datos reales, algo fundamental en la ingeniería y la educación moderna.
    
    Este proyecto fue creado especialmente para la asignatura de **Matemática Aplicada II** de la carrera de **Ingeniería en Computación e Informática** del Plan Común de la **Universidad de Magallanes**.
    
    Nuestro objetivo es facilitar el análisis estadístico mediante gráficas interactivas, permitiendo tomar decisiones basadas en datos reales.  
    La muestra de estos datos fue tomada entre el **03 de julio de 2025** y el **04 de julio de 2025**, por lo que en la actualidad los valores pueden variar.
    
    **Objetivo final:**  
    Implementar un método de recolección de datos en tiempo real para disponer de información actualizada a petición del usuario.
    
    
    **Autores:**  
    - **Andrés Felipe Barbosa Conde**  
      Técnico Superior en Análisis de Sistemas Computacionales (2024) — Universidad de Magallanes, Chile.  
      Estudiante regular de Ingeniería en Computación e Informática (2025) — Universidad de Magallanes, Chile.
    
    - **Iván Ignacio Sebastián Gallardo Barría**  
      Estudiante regular de Ingeniería en Computación e Informática (2025) — Universidad de Magallanes, Chile.
    
    **Institución:**  
    Universidad de Magallanes — Facultad de Ingeniería.
    
    **Contacto:**  
    - abarbosa@umagl.cl  
    - ivangall@umag.cl
    
    **Versión:** `2.0`
    """)
