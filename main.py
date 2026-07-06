import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from src.experiment import ejecutar_todos_los_experimentos, exportar_resultados, mostrar_resumen
from src.patterns import PATRONES_PRINCIPALES


def crear_directorios():

    directorios = ['results', 'results/graficos', 'results/tablas']
    for d in directorios:
        os.makedirs(d, exist_ok=True)
    print("Directorios creados: results, results/graficos, results/tablas")


def generar_grafico_barras(df_promedio, output_dir='results/graficos'): 

    politicas = df_promedio['politica'].unique()
    patrones = df_promedio['patron'].unique()
    
    x = np.arange(len(patrones))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    colores = {'LRU': '#2E86AB', 'FIFO': '#A23B72', 'Random': '#F18F01'}
    
    for i, policy in enumerate(politicas):
        datos = df_promedio[df_promedio['politica'] == policy]
        hit_rates = []
        for patron in patrones:
            hr = datos[datos['patron'] == patron]['hit_rate'].values
            hit_rates.append(hr[0] if len(hr) > 0 else 0)
        
        bars = ax.bar(x + i*width, hit_rates, width, label=policy, color=colores.get(policy, '#888888'))
        
        for bar, hr in zip(bars, hit_rates):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{hr:.1f}%', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('Patrón de acceso', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tasa de aciertos (%)', fontsize=12, fontweight='bold')
    ax.set_title('Comparación de políticas de reemplazo de caché\nCapacidad: 4 bloques, 1000 accesos',
                fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(patrones, fontsize=11)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/comparacion_hit_rate.png', dpi=150, bbox_inches='tight')
    plt.savefig(f'{output_dir}/comparacion_hit_rate.pdf', bbox_inches='tight')
    print(f" Gráfico guardado: {output_dir}/comparacion_hit_rate.png")
    plt.close()


def generar_grafico_reemplazos(df_promedio, output_dir='results/graficos'):

    politicas = df_promedio['politica'].unique()
    patrones = df_promedio['patron'].unique()
    
    x = np.arange(len(patrones))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    colores = {'LRU': '#2E86AB', 'FIFO': '#A23B72', 'Random': '#F18F01'}
    
    for i, policy in enumerate(politicas):
        datos = df_promedio[df_promedio['politica'] == policy]
        reemplazos = []
        for patron in patrones:
            r = datos[datos['patron'] == patron]['replacements'].values
            reemplazos.append(r[0] if len(r) > 0 else 0)
        
        ax.bar(x + i*width, reemplazos, width, label=policy, color=colores.get(policy, '#888888'))
    
    ax.set_xlabel('Patrón de acceso', fontsize=12, fontweight='bold')
    ax.set_ylabel('Número de reemplazos', fontsize=12, fontweight='bold')
    ax.set_title('Reemplazos realizados por política y patrón', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(patrones, fontsize=11)
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/comparacion_reemplazos.png', dpi=150, bbox_inches='tight')
    plt.savefig(f'{output_dir}/comparacion_reemplazos.pdf', bbox_inches='tight')
    print(f"Gráfico guardado: {output_dir}/comparacion_reemplazos.png")
    plt.close()


def generar_grafico_lineas(df_promedio, output_dir='results/graficos'):   

    politicas = df_promedio['politica'].unique()
    patrones = df_promedio['patron'].unique()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colores = {'LRU': '#2E86AB', 'FIFO': '#A23B72', 'Random': '#F18F01'}
    marcadores = {'LRU': 'o', 'FIFO': 's', 'Random': '^'}
    
    for policy in politicas:
        datos = df_promedio[df_promedio['politica'] == policy]
        hit_rates = []
        for patron in patrones:
            hr = datos[datos['patron'] == patron]['hit_rate'].values
            hit_rates.append(hr[0] if len(hr) > 0 else 0)
        
        ax.plot(patrones, hit_rates, marker=marcadores.get(policy, 'o'), 
               linewidth=2, markersize=8, label=policy, color=colores.get(policy))
        
        for i, hr in enumerate(hit_rates):
            ax.annotate(f'{hr:.1f}%', (patrones[i], hr), 
                       textcoords="offset points", xytext=(0, 10), ha='center', fontsize=9)
    
    ax.set_xlabel('Patrón de acceso', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tasa de aciertos (%)', fontsize=12, fontweight='bold')
    ax.set_title('Rendimiento de políticas por tipo de patrón', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/tendencias_hit_rate.png', dpi=150, bbox_inches='tight')
    print(f"Gráfico guardado: {output_dir}/tendencias_hit_rate.png")
    plt.close()


def generar_tabla_resumen_latex(df_promedio, output_dir='results/tablas'):

    tabla = df_promedio[['politica', 'patron', 'hit_rate', 'miss_rate', 'replacements']].copy()
    tabla.columns = ['Política', 'Patrón', 'Hit Rate (\\%)', 'Miss Rate (\\%)', 'Reemplazos']
    tabla = tabla.round({'Hit Rate (\\%)': 2, 'Miss Rate (\\%)': 2, 'Reemplazos': 2})
    
    tabla = tabla.sort_values(['Política', 'Patrón'])
    
    latex_content = tabla.to_latex(index=False, escape=False)
    
    with open(f'{output_dir}/tabla_resultados.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"Tabla LaTeX guardada: {output_dir}/tabla_resultados.tex")
    
    tabla.to_csv(f'{output_dir}/tabla_resultados.csv', index=False)
    print(f"Tabla CSV guardada: {output_dir}/tabla_resultados.csv")


def generar_archivo_para_articulo(df_promedio, output_dir='results'):

    with open(f'{output_dir}/resultados_para_articulo.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RESULTADOS PARA EL ARTÍCULO\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("3.1 Configuración experimental\n")
        f.write("-" * 40 + "\n")
        f.write("Parámetros de simulación:\n")
        f.write("- Tamaño de caché: 4 bloques\n")
        f.write("- Total de accesos: 1000\n")
        f.write("- Iteraciones: 10\n")
        f.write("- Rango de direcciones: 1 - 20\n")
        f.write("- Políticas evaluadas: LRU, FIFO, Random\n\n")
        
        f.write("3.2 Resultados para patrón secuencial\n")
        f.write("-" * 40 + "\n")
        secuencial = df_promedio[df_promedio['patron'] == 'secuencial']
        for _, row in secuencial.iterrows():
            f.write(f"  {row['politica']}: Hit Rate = {row['hit_rate']:.2f}%, "
                   f"Reemplazos = {row['replacements']:.0f}\n")
        f.write("\n")
        
        f.write("3.3 Resultados para patrón aleatorio\n")
        f.write("-" * 40 + "\n")
        aleatorio = df_promedio[df_promedio['patron'] == 'aleatorio']
        for _, row in aleatorio.iterrows():
            f.write(f"  {row['politica']}: Hit Rate = {row['hit_rate']:.2f}%, "
                   f"Reemplazos = {row['replacements']:.0f}\n")
        f.write("\n")
        
        f.write("3.4 Resultados para patrón con localidad temporal\n")
        f.write("-" * 40 + "\n")
        localidad = df_promedio[df_promedio['patron'] == 'localidad']
        for _, row in localidad.iterrows():
            f.write(f"  {row['politica']}: Hit Rate = {row['hit_rate']:.2f}%, "
                   f"Reemplazos = {row['replacements']:.0f}\n")
        f.write("\n")
        
        f.write("3.5 Resultados agregados y comparativos\n")
        f.write("-" * 40 + "\n")
        
        for patron in df_promedio['patron'].unique():
            f.write(f"\n{patron.upper()}:\n")
            df_patron = df_promedio[df_promedio['patron'] == patron]
            mejor = df_patron.loc[df_patron['hit_rate'].idxmax()]
            peor = df_patron.loc[df_patron['hit_rate'].idxmin()]
            f.write(f"  Mejor política: {mejor['politica']} ({mejor['hit_rate']:.2f}%)\n")
            f.write(f"  Peor política: {peor['politica']} ({peor['hit_rate']:.2f}%)\n")
        
        f.write("\n" + "=" * 80 + "\n")
    
    print(f" Archivo para artículo guardado: {output_dir}/resultados_para_articulo.txt")


def generar_grafico_comparativo_politicas(df_promedio, output_dir='results/graficos'):

    patrones = df_promedio['patron'].unique()
    politicas = df_promedio['politica'].unique()
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    
    angulos = np.linspace(0, 2 * np.pi, len(patrones), endpoint=False).tolist()
    angulos += angulos[:1]
    
    colores = {'LRU': '#2E86AB', 'FIFO': '#A23B72', 'Random': '#F18F01'}
    
    for policy in politicas:
        datos = df_promedio[df_promedio['politica'] == policy]
        valores = []
        for patron in patrones:
            hr = datos[datos['patron'] == patron]['hit_rate'].values
            valores.append(hr[0] if len(hr) > 0 else 0)
        valores += valores[:1]
        
        ax.plot(angulos, valores, 'o-', linewidth=2, label=policy, color=colores.get(policy))
        ax.fill(angulos, valores, alpha=0.1, color=colores.get(policy))
    
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(patrones, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=8)
    ax.set_title('Comparación de políticas (gráfico radial)', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/radar_comparacion.png', dpi=150, bbox_inches='tight')
    print(f"Gráfico radar guardado: {output_dir}/radar_comparacion.png")
    plt.close()


def main():
    
    print("=" * 70)
    print("SIMULADOR DE POLÍTICAS DE REEMPLAZO DE CACHÉ")
    print("LRU - FIFO - RANDOM")
    print("=" * 70)
    print()
    
    crear_directorios()
    print()
    
    ITERACIONES = 10
    CAPACIDAD = 4
    
    print(f"Configuración:")
    print(f"   - Capacidad de caché: {CAPACIDAD} bloques")
    print(f"   - Accesos por simulación: 1000")
    print(f"   - Iteraciones por experimento: {ITERACIONES}")
    print(f"   - Políticas: LRU, FIFO, Random")
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
    print("Generando gráficos...")
    generar_grafico_barras(df_promedio)
    generar_grafico_reemplazos(df_promedio)
    generar_grafico_lineas(df_promedio)
    generar_grafico_comparativo_politicas(df_promedio)
    
    generar_tabla_resumen_latex(df_promedio)
    
    generar_archivo_para_articulo(df_promedio)
    
    print("\n" + "=" * 70)
    print("SIMULACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\nResultados guardados en la carpeta 'results/'")
    print("   - CSV: resultados_promedio.csv, resultados_detallados.csv")
    print("   - Gráficos: results/graficos/")
    print("   - Tablas: results/tablas/")
    print("   - Texto para artículo: results/resultados_para_articulo.txt")
    print()


if __name__ == "__main__":
    main()