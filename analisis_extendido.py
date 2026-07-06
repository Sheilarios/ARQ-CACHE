"""
Módulo: analisis_extendido.py
Extiende el simulador con dos análisis solicitados por el docente:

1. AMAT (Average Memory Access Time / Tiempo Medio de Acceso a la Memoria)
   calculado a partir de las tasas de fallo obtenidas por el simulador.

2. Escalabilidad: repite los experimentos principales (secuencial, aleatorio,
   localidad, mixto) variando la capacidad de la caché (4, 8 y 16 bloques)
   para observar cómo cambia el Hit Rate de cada política.

No modifica src/cache.py, src/simulator.py ni src/patterns.py: reutiliza
ejecutar_todos_los_experimentos() tal como está definida en src/experiment.py.

Uso:
    python analisis_extendido.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

from src.experiment import ejecutar_todos_los_experimentos, exportar_resultados

PATRONES_ARTICULO = ['secuencial', 'aleatorio', 'localidad', 'mixto']

def calcular_amat(df_promedio, t_hit_ns=1.0, penalizacion_fallo_ns=20.0):
    """
    Calcula el AMAT para cada fila de resultados promedio.

    AMAT = T_hit + (Miss_rate/100) * Penalizacion_por_fallo

    Args:
        df_promedio (DataFrame): salida de exportar_resultados() con columna 'miss_rate'
        t_hit_ns (float): tiempo de acceso a la caché en caso de acierto (ns)
        penalizacion_fallo_ns (float): tiempo adicional por fallo, p. ej. acceso
            a memoria principal (ns)

    Returns:
        DataFrame: copia de df_promedio con la columna 'amat_ns' añadida
    """
    df = df_promedio.copy()
    df['amat_ns'] = t_hit_ns + (df['miss_rate'] / 100.0) * penalizacion_fallo_ns
    df['t_hit_ns'] = t_hit_ns
    df['penalizacion_fallo_ns'] = penalizacion_fallo_ns
    return df


def generar_tabla_amat(df_amat, patrones=PATRONES_ARTICULO, output_dir='results/tablas'):
    """
    Genera la tabla de AMAT (política x patrón) lista para el artículo,
    en CSV y en formato LaTeX.
    """
    os.makedirs(output_dir, exist_ok=True)

    tabla = df_amat[df_amat['patron'].isin(patrones)][
        ['politica', 'patron', 'hit_rate', 'miss_rate', 'amat_ns']
    ].copy()
    tabla = tabla.round({'hit_rate': 2, 'miss_rate': 2, 'amat_ns': 3})
    tabla = tabla.sort_values(['patron', 'politica'])

    tabla.to_csv(f'{output_dir}/tabla_amat.csv', index=False)

    tabla_pivot = tabla.pivot(index='politica', columns='patron', values='amat_ns')
    tabla_pivot = tabla_pivot[patrones]  # mismo orden que el artículo
    tabla_pivot.to_csv(f'{output_dir}/tabla_amat_pivot.csv')

    latex = tabla_pivot.round(2).to_latex(
        caption='AMAT estimado por política y escenario (ns)',
        label='tab:amat'
    )
    with open(f'{output_dir}/tabla_amat.tex', 'w', encoding='utf-8') as f:
        f.write(latex)

    print(f"Tabla AMAT guardada en {output_dir}/tabla_amat.csv y tabla_amat.tex")
    print("\nAMAT (ns) por política y patrón:")
    print(tabla_pivot.round(3).to_string())

    return tabla_pivot


def graficar_amat(tabla_pivot, output_dir='results/graficos'):
    """Gráfico de barras comparando AMAT por política y escenario."""
    os.makedirs(output_dir, exist_ok=True)

    colores = {'LRU': '#2E86AB', 'FIFO': '#A23B72', 'Random': '#F18F01'}
    ax = tabla_pivot.T.plot(kind='bar', figsize=(10, 6),
                             color=[colores.get(c, '#888888') for c in tabla_pivot.index])
    ax.set_xlabel('Patrón de acceso', fontsize=12, fontweight='bold')
    ax.set_ylabel('AMAT (ns)', fontsize=12, fontweight='bold')
    ax.set_title('Tiempo Medio de Acceso a la Memoria (AMAT) por política y patrón',
                 fontsize=13, fontweight='bold')
    ax.legend(title='Política')
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/comparacion_amat.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Gráfico guardado: {output_dir}/comparacion_amat.png")


def ejecutar_analisis_escalabilidad(capacidades=(4, 8, 16), iteraciones=10,
                                     patrones=PATRONES_ARTICULO,
                                     output_dir='results'):
    """
    Ejecuta el conjunto de experimentos del artículo para varias capacidades
    de caché y devuelve un único DataFrame combinado.

    Args:
        capacidades (iterable): tamaños de caché a evaluar, en bloques
        iteraciones (int): número de corridas por combinación política/patrón
        patrones (list): patrones a evaluar (por defecto, los 4 del artículo)
        output_dir (str): carpeta donde guardar resultados

    Returns:
        DataFrame: resultados promedio para todas las capacidades, con
        columna 'capacidad'
    """
    os.makedirs(output_dir, exist_ok=True)
    frames = []

    for cap in capacidades:
        print(f"\n{'='*60}\nEjecutando experimentos con capacidad = {cap} bloques\n{'='*60}")
        resultados_promedio, resultados_detallados = ejecutar_todos_los_experimentos(
            patrones=patrones,
            iteraciones=iteraciones,
            capacity=cap,
            verbose=False,
            reproducible=True
        )
        df_promedio, _ = exportar_resultados(
            resultados_promedio, resultados_detallados,
            output_dir=f'{output_dir}/cap_{cap}'
        )
        df_promedio['capacidad'] = cap
        frames.append(df_promedio)

    df_todas = pd.concat(frames, ignore_index=True)
    df_todas.to_csv(f'{output_dir}/resultados_escalabilidad.csv', index=False)
    print(f"\nResultados combinados guardados en {output_dir}/resultados_escalabilidad.csv")
    return df_todas


def generar_tabla_escalabilidad(df_todas, patrones=PATRONES_ARTICULO,
                                 output_dir='results/tablas'):
    """
    Genera tablas comparativas de Hit Rate, Miss Rate y Reemplazos
    según la capacidad de la caché.
    """
    os.makedirs(output_dir, exist_ok=True)

    metricas = {
        'hit_rate': 'Hit Rate (%)',
        'miss_rate': 'Miss Rate (%)',
        'replacements': 'Reemplazos'
    }

    for metrica, nombre in metricas.items():

        tabla = df_todas[df_todas['patron'].isin(patrones)][
            ['patron', 'politica', 'capacidad', metrica]
        ].copy()

        tabla = tabla.round(2)

        tabla_pivot = tabla.pivot_table(
            index=['patron', 'politica'],
            columns='capacidad',
            values=metrica
        )

        archivo = metrica.lower().replace(" ", "_")

        tabla_pivot.to_csv(f'{output_dir}/tabla_{archivo}_escalabilidad.csv')

        print(f"\n{'='*70}")
        print(nombre)
        print(tabla_pivot.to_string())

    return


def graficar_escalabilidad(df_todas, patrones=PATRONES_ARTICULO,
                            output_dir='results/graficos'):
    """Gráfico de líneas: Hit Rate vs. capacidad de caché, un subplot por patrón."""
    os.makedirs(output_dir, exist_ok=True)

    colores = {'LRU': '#2E86AB', 'FIFO': '#A23B72', 'Random': '#F18F01'}
    fig, axes = plt.subplots(1, len(patrones), figsize=(5 * len(patrones), 5), sharey=True)

    for ax, patron in zip(axes, patrones):
        sub = df_todas[df_todas['patron'] == patron]
        for politica in ['LRU', 'FIFO', 'Random']:
            datos = sub[sub['politica'] == politica].sort_values('capacidad')
            ax.plot(datos['capacidad'], datos['hit_rate'], marker='o',
                    label=politica, color=colores.get(politica))
        ax.set_title(patron.capitalize())
        ax.set_xlabel('Capacidad (bloques)')
        ax.set_xticks(list(df_todas['capacidad'].unique()))
        ax.grid(True, alpha=0.3)

    axes[0].set_ylabel('Hit Rate (%)')
    axes[0].legend()
    plt.suptitle('Hit Rate según capacidad de caché, por patrón y política', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/escalabilidad_hit_rate.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Gráfico guardado: {output_dir}/escalabilidad_hit_rate.png")


def main():
    print("=" * 70)
    print("ANÁLISIS EXTENDIDO: AMAT Y ESCALABILIDAD DE CAPACIDAD DE CACHÉ")
    print("=" * 70)

    # --- 1. AMAT, usando la capacidad principal del artículo (4 bloques) ---
    print("\n[1/2] Calculando AMAT con capacidad = 4 bloques (configuración base)...")
    resultados_promedio, resultados_detallados = ejecutar_todos_los_experimentos(
        patrones=PATRONES_ARTICULO,
        iteraciones=10,
        capacity=4,
        verbose=False,
        reproducible=True
    )
    df_promedio, _ = exportar_resultados(resultados_promedio, resultados_detallados)

    df_amat = calcular_amat(df_promedio, t_hit_ns=1.0, penalizacion_fallo_ns=20.0)
    tabla_amat = generar_tabla_amat(df_amat)
    graficar_amat(tabla_amat)

    print("\n[2/2] Ejecutando análisis de escalabilidad (4, 8 y 16 bloques)...")
    df_escalabilidad = ejecutar_analisis_escalabilidad(capacidades=(4, 8, 16), iteraciones=10)
    generar_tabla_escalabilidad(df_escalabilidad)
    graficar_escalabilidad(df_escalabilidad)

    print("\n" + "=" * 70)
    print("ANÁLISIS EXTENDIDO COMPLETADO")
    print("=" * 70)
    print("Archivos generados en results/:")
    print("  - tablas/tabla_amat.csv, tabla_amat.tex")
    print("  - tablas/tabla_escalabilidad.csv")
    print("  - graficos/comparacion_amat.png")
    print("  - graficos/escalabilidad_hit_rate.png")
    print("  - resultados_escalabilidad.csv")


if __name__ == "__main__":
    main()
