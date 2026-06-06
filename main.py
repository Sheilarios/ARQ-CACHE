"""
Modulo: main.py
Script principal para ejecutar la simulacion de politicas de reemplazo de cache
"""

import os
import sys
import subprocess
import pandas as pd
import numpy as np

# ============================================================
# VERIFICAR E INSTALAR MATPLOTLIB SI ES NECESARIO
# ============================================================
try:
    import matplotlib.pyplot as plt
    import matplotlib
except ImportError:
    print("Matplotlib no esta instalado. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt
    import matplotlib

from src.experiment import ejecutar_todos_los_experimentos, exportar_resultados, mostrar_resumen
from src.patterns import PATRONES_PRINCIPALES

# ============================================================
# CONFIGURACION DE FUENTES PARA EVITAR PROBLEMAS DE CODIFICACION
# ============================================================
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def crear_directorios():
    """Crea los directorios necesarios para guardar resultados"""
    directorios = ['results', 'results/graficos', 'results/tablas']
    for d in directorios:
        os.makedirs(d, exist_ok=True)
    print("Directorios creados: results, results/graficos, results/tablas")


def generar_grafico_barras(df_promedio, output_dir='results/graficos'):
    """Genera grafico de barras comparativo de hit rates - INCLUYE LRU, FIFO, RANDOM"""
    
    # FORZAR las 3 politicas explicitamente
    politicas = ['LRU', 'FIFO', 'Random']
    patrones_principales = ['secuencial', 'aleatorio', 'localidad', 'mixto']
    
    # Verificar que los datos existan
    df_filtrado = df_promedio[df_promedio['patron'].isin(patrones_principales)]
    
    # Verificar que todas las politicas estan en los datos
    politicas_existentes = df_filtrado['politica'].unique()
    for p in politicas:
        if p not in politicas_existentes:
            print(f"ADVERTENCIA: La politica {p} no existe en los datos")
    
    # Mapeo de nombres a ingles
    nombres_ingles = {
        'secuencial': 'Sequential',
        'aleatorio': 'Random',
        'localidad': 'Locality',
        'mixto': 'Mixed'
    }
    
    x = np.arange(len(patrones_principales))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    colores = {'LRU': '#2E86AB', 'FIFO': '#A23B72', 'Random': '#F18F01'}
    
    for i, policy in enumerate(politicas):
        # Obtener datos para esta politica
        datos = df_filtrado[df_filtrado['politica'] == policy]
        hit_rates = []
        for patron in patrones_principales:
            hr = datos[datos['patron'] == patron]['hit_rate'].values
            if len(hr) > 0:
                hit_rates.append(hr[0])
            else:
                hit_rates.append(0)
                print(f"ADVERTENCIA: No hay datos para {policy} - {patron}")
        
        bars = ax.bar(x + i*width, hit_rates, width, label=policy, color=colores.get(policy, '#888888'))
        
        for bar, hr in zip(bars, hit_rates):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{hr:.1f}%', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('Access Pattern', fontsize=12, fontweight='bold')
    ax.set_ylabel('Hit Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Cache Replacement Policies Comparison (LRU, FIFO, Random)\nCache Size: 4 blocks, 1000 accesses',
                fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels([nombres_ingles[p] for p in patrones_principales], fontsize=11)
    ax.legend(loc='upper left', fontsize=11)
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/comparacion_hit_rate.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Grafico guardado: {output_dir}/comparacion_hit_rate.png (INCLUYE LRU, FIFO, RANDOM)")


def generar_grafico_reemplazos(df_promedio, output_dir='results/graficos'):
    """Genera grafico de barras comparativo de reemplazos - INCLUYE LRU, FIFO, RANDOM"""
    
    # FORZAR las 3 politicas explicitamente
    politicas = ['LRU', 'FIFO', 'Random']
    patrones_principales = ['secuencial', 'aleatorio', 'localidad', 'mixto']
    
    df_filtrado = df_promedio[df_promedio['patron'].isin(patrones_principales)]
    
    nombres_ingles = {
        'secuencial': 'Sequential',
        'aleatorio': 'Random',
        'localidad': 'Locality',
        'mixto': 'Mixed'
    }
    
    x = np.arange(len(patrones_principales))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    colores = {'LRU': '#2E86AB', 'FIFO': '#A23B72', 'Random': '#F18F01'}
    
    for i, policy in enumerate(politicas):
        datos = df_filtrado[df_filtrado['politica'] == policy]
        reemplazos = []
        for patron in patrones_principales:
            r = datos[datos['patron'] == patron]['replacements'].values
            if len(r) > 0:
                reemplazos.append(r[0])
            else:
                reemplazos.append(0)
        
        ax.bar(x + i*width, reemplazos, width, label=policy, color=colores.get(policy, '#888888'))
    
    ax.set_xlabel('Access Pattern', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Replacements', fontsize=12, fontweight='bold')
    ax.set_title('Replacements by Policy and Access Pattern (LRU, FIFO, Random)', 
                fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels([nombres_ingles[p] for p in patrones_principales], fontsize=11)
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/comparacion_reemplazos.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Grafico guardado: {output_dir}/comparacion_reemplazos.png (INCLUYE LRU, FIFO, RANDOM)")


def generar_grafico_lineas(df_promedio, output_dir='results/graficos'):
    """Genera grafico de lineas - INCLUYE LRU, FIFO, RANDOM"""
    
    politicas = ['LRU', 'FIFO', 'Random']
    patrones_principales = ['secuencial', 'aleatorio', 'localidad', 'mixto']
    df_filtrado = df_promedio[df_promedio['patron'].isin(patrones_principales)]
    
    nombres_ingles = {
        'secuencial': 'Sequential',
        'aleatorio': 'Random',
        'localidad': 'Locality',
        'mixto': 'Mixed'
    }
    patrones_ingles = [nombres_ingles[p] for p in patrones_principales]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colores = {'LRU': '#2E86AB', 'FIFO': '#A23B72', 'Random': '#F18F01'}
    marcadores = {'LRU': 'o', 'FIFO': 's', 'Random': '^'}
    
    for policy in politicas:
        datos = df_filtrado[df_filtrado['politica'] == policy]
        hit_rates = []
        for patron in patrones_principales:
            hr = datos[datos['patron'] == patron]['hit_rate'].values
            hit_rates.append(hr[0] if len(hr) > 0 else 0)
        
        ax.plot(patrones_ingles, hit_rates, marker=marcadores.get(policy, 'o'), 
               linewidth=2, markersize=8, label=policy, color=colores.get(policy))
        
        for i, hr in enumerate(hit_rates):
            ax.annotate(f'{hr:.1f}%', (patrones_ingles[i], hr), 
                       textcoords="offset points", xytext=(0, 10), ha='center', fontsize=9)
    
    ax.set_xlabel('Access Pattern', fontsize=12, fontweight='bold')
    ax.set_ylabel('Hit Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Policy Performance by Access Pattern (LRU, FIFO, Random)', 
                fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/tendencias_hit_rate.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Grafico guardado: {output_dir}/tendencias_hit_rate.png")


def generar_tabla_resumen_latex(df_promedio, output_dir='results/tablas'):
    """Genera tabla de resultados en formato LaTeX (opcional)"""
    
    patrones_principales = ['secuencial', 'aleatorio', 'localidad', 'mixto']
    df_filtrado = df_promedio[df_promedio['patron'].isin(patrones_principales)]
    
    # Ordenar por politica (LRU, FIFO, Random)
    orden_politicas = ['LRU', 'FIFO', 'Random']
    df_filtrado['politica'] = pd.Categorical(df_filtrado['politica'], categories=orden_politicas, ordered=True)
    df_filtrado = df_filtrado.sort_values(['politica', 'patron'])
    
    tabla = df_filtrado[['politica', 'patron', 'hit_rate', 'miss_rate', 'replacements']].copy()
    tabla.columns = ['Politica', 'Patron', 'Hit Rate (%)', 'Miss Rate (%)', 'Reemplazos']
    tabla = tabla.round({'Hit Rate (%)': 2, 'Miss Rate (%)': 2, 'Reemplazos': 2})
    
    # Guardar CSV (siempre funciona)
    tabla.to_csv(f'{output_dir}/tabla_resultados.csv', index=False)
    print(f"Tabla CSV guardada: {output_dir}/tabla_resultados.csv")
    
    # Intentar generar LaTeX (opcional)
    try:
        latex_content = tabla.to_latex(index=False, escape=False)
        with open(f'{output_dir}/tabla_resultados.tex', 'w', encoding='utf-8') as f:
            f.write(latex_content)
        print(f"Tabla LaTeX guardada: {output_dir}/tabla_resultados.tex")
    except Exception as e:
        print(f"Nota: LaTeX no generado (opcional). Error: {e}")


def generar_archivo_para_articulo(df_promedio, output_dir='results'):
    """Genera un archivo con los resultados listos para copiar al articulo"""
    
    patrones_principales = ['secuencial', 'aleatorio', 'localidad', 'mixto']
    df_filtrado = df_promedio[df_promedio['patron'].isin(patrones_principales)]
    
    with open(f'{output_dir}/resultados_para_articulo.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RESULTADOS PARA EL ARTICULO\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("3.1 Configuracion experimental\n")
        f.write("-" * 40 + "\n")
        f.write("Parametros de simulacion:\n")
        f.write("- Tamanio de cache: 4 bloques\n")
        f.write("- Total de accesos: 1000\n")
        f.write("- Iteraciones: 10\n")
        f.write("- Rango de direcciones: 1 - 20\n")
        f.write("- Politicas evaluadas: LRU, FIFO, Random\n\n")
        
        for patron in patrones_principales:
            f.write(f"Resultados para patron {patron}\n")
            f.write("-" * 40 + "\n")
            df_patron = df_filtrado[df_filtrado['patron'] == patron]
            for _, row in df_patron.iterrows():
                f.write(f"  {row['politica']}: Hit Rate = {row['hit_rate']:.2f}%, "
                       f"Reemplazos = {row['replacements']:.0f}\n")
            f.write("\n")
        
        f.write("MEJOR POLITICA POR PATRON\n")
        f.write("-" * 40 + "\n")
        for patron in patrones_principales:
            df_patron = df_filtrado[df_filtrado['patron'] == patron]
            mejor = df_patron.loc[df_patron['hit_rate'].idxmax()]
            f.write(f"  {patron}: {mejor['politica']} ({mejor['hit_rate']:.2f}%)\n")
        
        f.write("\n" + "=" * 80 + "\n")
    
    print(f"Archivo para articulo guardado: {output_dir}/resultados_para_articulo.txt")


def generar_grafico_comparativo_politicas(df_promedio, output_dir='results/graficos'):
    """Genera grafico tipo radar - INCLUYE LRU, FIFO, RANDOM"""
    
    politicas = ['LRU', 'FIFO', 'Random']
    patrones_principales = ['secuencial', 'aleatorio', 'localidad', 'mixto']
    df_filtrado = df_promedio[df_promedio['patron'].isin(patrones_principales)]
    
    nombres_ingles = {
        'secuencial': 'Sequential',
        'aleatorio': 'Random',
        'localidad': 'Locality',
        'mixto': 'Mixed'
    }
    patrones_ingles = [nombres_ingles[p] for p in patrones_principales]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    
    angulos = np.linspace(0, 2 * np.pi, len(patrones_principales), endpoint=False).tolist()
    angulos += angulos[:1]
    
    colores = {'LRU': '#2E86AB', 'FIFO': '#A23B72', 'Random': '#F18F01'}
    
    for policy in politicas:
        datos = df_filtrado[df_filtrado['politica'] == policy]
        valores = []
        for patron in patrones_principales:
            hr = datos[datos['patron'] == patron]['hit_rate'].values
            valores.append(hr[0] if len(hr) > 0 else 0)
        valores += valores[:1]
        
        ax.plot(angulos, valores, 'o-', linewidth=2, label=policy, color=colores.get(policy))
        ax.fill(angulos, valores, alpha=0.1, color=colores.get(policy))
    
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(patrones_ingles, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=8)
    ax.set_title('Policy Comparison (Radar Chart) - LRU, FIFO, Random', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/radar_comparacion.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Grafico radar guardado: {output_dir}/radar_comparacion.png")


def main():
    """Funcion principal que ejecuta toda la simulacion"""
    
    print("=" * 70)
    print("SIMULADOR DE POLITICAS DE REEMPLAZO DE CACHE")
    print("LRU - FIFO - RANDOM")
    print("=" * 70)
    print()
    
    crear_directorios()
    print()
    
    ITERACIONES = 10
    CAPACIDAD = 4
    
    print(f"Configuracion:")
    print(f"   - Capacidad de cache: {CAPACIDAD} bloques")
    print(f"   - Accesos por simulacion: 1000")
    print(f"   - Iteraciones por experimento: {ITERACIONES}")
    print(f"   - Politicas: LRU, FIFO, Random")
    print(f"   - Patrones: {list(PATRONES_PRINCIPALES.keys())}")
    print()
    
    print("Iniciando experimentos...")
    print("-" * 50)
    
    resultados_promedio, resultados_detallados = ejecutar_todos_los_experimentos(
        iteraciones=ITERACIONES,
        capacity=CAPACIDAD,
        verbose=True,
        reproducible=True
    )
    
    print()
    print("-" * 50)
    
    df_promedio, df_detalle = exportar_resultados(resultados_promedio, resultados_detallados)
    
    mostrar_resumen(df_promedio)
    
    print("\n" + "-" * 50)
    print("Generando graficos...")
    generar_grafico_barras(df_promedio)
    generar_grafico_reemplazos(df_promedio)
    generar_grafico_lineas(df_promedio)
    generar_grafico_comparativo_politicas(df_promedio)
    
    generar_tabla_resumen_latex(df_promedio)
    
    generar_archivo_para_articulo(df_promedio)
    
    print("\n" + "=" * 70)
    print("SIMULACION COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\nResultados guardados en la carpeta 'results/'")
    print("   - CSV: resultados_promedio.csv, resultados_detallados.csv")
    print("   - Graficos: results/graficos/")
    print("   - Tablas: results/tablas/")
    print("   - Texto para articulo: results/resultados_para_articulo.txt")
    print()


if __name__ == "__main__":
    main()