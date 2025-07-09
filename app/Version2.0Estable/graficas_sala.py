# graficas_sala.py

import plotly.express as px

# ===========================
# 📈 Temperatura: Línea
# ===========================
def grafica_temperatura(df_pc):
    fig = px.line(
        df_pc,
        x='Tiempo',
        y='Temperaturas núcleo (avg) [°C]',
        markers=True,
        title=f'Temperatura vs Tiempo - {df_pc["CPU_Short"].iloc[0]}'
    )
    fig.update_layout(template='plotly_dark')
    return fig

# ===========================
# 📈 Relojes: Línea
# ===========================
def grafica_relojes(df_pc):
    fig = px.line(
        df_pc,
        x='Tiempo',
        y='Relojes núcleo (avg) [MHz]',
        markers=True,
        title=f'Relojes núcleo vs Tiempo - {df_pc["CPU_Short"].iloc[0]}'
    )
    fig.update_layout(template='plotly_dark')
    return fig

# ===========================
# 📈 Uso: Línea
# ===========================
def grafica_uso(df_pc):
    fig = px.line(
        df_pc,
        x='Tiempo',
        y='Uso núcleo (avg) [%]',
        markers=True,
        title=f'Uso núcleo vs Tiempo - {df_pc["CPU_Short"].iloc[0]}'
    )
    fig.update_layout(template='plotly_dark')
    return fig

