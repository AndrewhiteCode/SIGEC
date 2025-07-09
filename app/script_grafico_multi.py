import pandas as pd
import glob
import plotly.express as px

# 🎯 Clasificación CPU
def clasificar_cpu(cpu_full):
    cpu_full = cpu_full.lower()
    if '13th' in cpu_full or '13700' in cpu_full:
        return 'i7 13'
    elif '12th' in cpu_full or '12700' in cpu_full:
        return 'i7 12'
    elif 'i9' in cpu_full and '10900' in cpu_full:
        return 'i9 10'
    elif 'i5' in cpu_full and '6400' in cpu_full:
        return 'i5 6'
    elif 'ryzen' in cpu_full and '3700' in cpu_full:
        return 'Ryzen 7 3700'
    else:
        return 'Otro'

# ✅ Cargar datos
def cargar_datos():
    ruta_base = r'C:\Users\Andres\Desktop\MAT2\data'
    archivos = glob.glob(ruta_base + '/**/*.csv', recursive=True)

    dfs = []
    for archivo in archivos:
        df = pd.read_csv(archivo, encoding='utf-8-sig')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        cpu_name = 'Desconocido'
        idx_cpu = df.apply(lambda row: row.astype(str).str.contains('CPU').any(), axis=1)
        if idx_cpu.any():
            fila_cpu = df[idx_cpu].iloc[0]
            for celda in fila_cpu:
                if isinstance(celda, str) and 'CPU' in celda:
                    cpu_name = celda.strip()
                    break
            df = df[~idx_cpu]

        df = df[df['Date'].notna()]
        df['Tiempo'] = range(1, len(df) + 1)

        df['Temperaturas núcleo (avg) [°C]'] = pd.to_numeric(df['Temperaturas núcleo (avg) [°C]'], errors='coerce')
        df['Relojes núcleo (avg) [MHz]'] = pd.to_numeric(df['Relojes núcleo (avg) [MHz]'], errors='coerce')
        df['Uso núcleo (avg) [%]'] = pd.to_numeric(df['Uso núcleo (avg) [%]'], errors='coerce')

        df['CPU'] = cpu_name
        df['Equipo'] = archivo

        dfs.append(df)

    df_final = pd.concat(dfs, ignore_index=True)
    df_final['CPU_Short'] = df_final['CPU'].apply(clasificar_cpu)
    return df_final

# ✅ Generar gráficas Plotly 1:1 con tu script original
def generar_graficas_plotly():
    df_plot = cargar_datos()
    figs = []

    # 1) Temperatura vs Tiempo
    fig1 = px.line(
        df_plot[df_plot['Tiempo'] <= 10],
        x='Tiempo',
        y='Temperaturas núcleo (avg) [°C]',
        color='CPU_Short',
        title='Temperatura vs Tiempo',
        markers=True
    )
    figs.append(fig1)

    # 2) Relojes núcleo vs Tiempo
    fig2 = px.line(
        df_plot[df_plot['Tiempo'] <= 10],
        x='Tiempo',
        y='Relojes núcleo (avg) [MHz]',
        color='CPU_Short',
        title='Relojes núcleo (MHz) vs Tiempo',
        markers=True
    )
    figs.append(fig2)

    # 3) Uso núcleo vs Tiempo
    fig3 = px.line(
        df_plot[df_plot['Tiempo'] <= 10],
        x='Tiempo',
        y='Uso núcleo (avg) [%]',
        color='CPU_Short',
        title='Uso núcleo (%) vs Tiempo',
        markers=True
    )
    figs.append(fig3)

    # 4) Cantidad de procesadores por modelo (ÚNICOS)
    equipos_unicos = df_plot[['Equipo', 'CPU_Short']].drop_duplicates()
    modelos = equipos_unicos['CPU_Short'].value_counts().reset_index()
    modelos.columns = ['CPU', 'Cantidad']

    fig4 = px.bar(
        modelos,
        x='CPU',
        y='Cantidad',
        title='Cantidad de procesadores por modelo (equipos únicos)',
        text_auto=True
    )
    figs.append(fig4)

    # 5) Núcleos Físicos y Lógicos
    info_nucleos = {
        'i7 13': {'Fisicos': 16, 'Logicos': 24},
        'i7 12': {'Fisicos': 12, 'Logicos': 20},
        'i9 10': {'Fisicos': 10, 'Logicos': 20},
        'i5 6': {'Fisicos': 2,  'Logicos': 4},
        'Ryzen 7 3700': {'Fisicos': 8, 'Logicos': 16}
    }

    df_nucleos = pd.DataFrame(info_nucleos).T.reset_index()
    df_nucleos.columns = ['CPU_Short', 'Fisicos', 'Logicos']

    df_nucleos_plot = equipos_unicos.merge(df_nucleos, on='CPU_Short', how='left').drop_duplicates('CPU_Short')

    df_nucleos_melt = df_nucleos_plot.melt(
        id_vars='CPU_Short',
        value_vars=['Fisicos', 'Logicos'],
        var_name='Tipo',
        value_name='Cantidad'
    )

    fig5 = px.bar(
        df_nucleos_melt,
        x='CPU_Short',
        y='Cantidad',
        color='Tipo',
        barmode='group',
        title='Núcleos Físicos y Lógicos por procesador'
    )
    figs.append(fig5)

    # 6) Dispersión Temperatura vs Uso
    fig6 = px.scatter(
        df_plot,
        x='Temperaturas núcleo (avg) [°C]',
        y='Uso núcleo (avg) [%]',
        color='CPU_Short',
        opacity=0.6,
        title='Relación entre Temperatura y Uso del núcleo'
    )
    figs.append(fig6)

    # 7) Boxplot Temperatura por CPU
    fig7 = px.box(
        df_plot,
        x='CPU_Short',
        y='Temperaturas núcleo (avg) [°C]',
        title='Distribución de temperaturas por procesador'
    )
    figs.append(fig7)

    return figs
