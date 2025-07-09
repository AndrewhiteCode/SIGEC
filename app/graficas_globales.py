# graficas_globales.py

import pandas as pd
import plotly.express as px
import glob

# 📂 Ruta base
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # Va a raíz del repo
ruta_base = BASE_DIR / "data"

archivos = glob.glob(ruta_base + '/**/*.csv', recursive=True)

# 🔄 Leer todos los CSVs
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
    dfs.append(df)

df_final = pd.concat(dfs, ignore_index=True)
"""Intel Core i7-13700,CPU , Intel Core i9-10900X,CPU, Intel Core i5-6200U,CPU, AMD Ryzen 7 3700X, Intel Core i7-12700,CPU"""
def clasificar_cpu(cpu_full):
    cpu_full = cpu_full.lower()
    if '13th' in cpu_full or '13700' in cpu_full:
        return 'Intel Core i7-13700'
    elif '12th' in cpu_full or '12700' in cpu_full:
        return 'Intel Core i7-12700'
    elif 'i9' in cpu_full and '10900' in cpu_full:
        return 'Intel Core i9-10900X'
    elif 'i5' in cpu_full and '6400' in cpu_full:
        return 'i5 6'
    elif 'ryzen' in cpu_full and '3700' in cpu_full:
        return 'AMD Ryzen 7 3700X'
    else:
        return 'Intel Core i5-6200U'

df_final['CPU_Short'] = df_final['CPU'].apply(clasificar_cpu)

# ✅ Promedio por CPU_Short y Tiempo
df_grouped = df_final[df_final['Tiempo'] <= 10].groupby(['CPU_Short', 'Tiempo']).agg({
    'Temperaturas núcleo (avg) [°C]': 'mean',
    'Relojes núcleo (avg) [MHz]': 'mean',
    'Uso núcleo (avg) [%]': 'mean'
}).reset_index()

def grafica_temperatura():
    fig = px.line(
        df_grouped,
        x='Tiempo',
        y='Temperaturas núcleo (avg) [°C]',
        color='CPU_Short',
        markers=True,
        title='Temperatura vs Tiempo (Promedio)'
    )
    fig.update_layout(template='plotly_dark')
    return fig

def grafica_relojes():
    fig = px.line(
        df_grouped,
        x='Tiempo',
        y='Relojes núcleo (avg) [MHz]',
        color='CPU_Short',
        markers=True,
        title='Relojes núcleo vs Tiempo (Promedio)'
    )
    fig.update_layout(template='plotly_dark')
    return fig

def grafica_uso():
    fig = px.line(
        df_grouped,
        x='Tiempo',
        y='Uso núcleo (avg) [%]',
        color='CPU_Short',
        markers=True,
        title='Uso núcleo vs Tiempo (Promedio)'
    )
    fig.update_layout(template='plotly_dark')
    return fig

def grafica_boxplot_temp():
    fig = px.box(
        df_final,
        x='CPU_Short',
        y='Temperaturas núcleo (avg) [°C]',
        color='CPU_Short',
        title='Distribución de temperaturas por procesador',
        labels={'CPU_Short': 'Procesador'}
    )
    fig.update_layout(template='plotly_dark')
    return fig

def grafica_dispersion_temp_uso():
    fig = px.scatter(
        df_final,
        x='Temperaturas núcleo (avg) [°C]',
        y='Uso núcleo (avg) [%]',
        color='CPU_Short',
        title='Relación Temperatura vs Uso'
    )
    fig.update_layout(template='plotly_dark')
    return fig

# Y puedes seguir con las otras…
