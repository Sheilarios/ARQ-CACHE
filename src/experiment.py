"""
Módulo: experiment.py
Ejecuta experimentos completos con múltiples iteraciones para evaluar
las políticas de reemplazo bajo diferentes patrones de acceso.
"""

import numpy as np
import pandas as pd
from src.simulator import ejecutar_simulacion
from src.patterns import PATRONES


def ejecutar_experimento(policy, pattern_name, iteraciones=10, capacity=4, verbose=False):
    """
    Ejecuta un experimento completo para una política y patrón específicos.
    
    Args:
        policy (str): Política de reemplazo ('LRU', 'FIFO', 'Random')
        pattern_name (str): Nombre del patrón ('secuencial', 'aleatorio', 'localidad', 'mixto')
        iteraciones (int): Número de veces que se repite el experimento
        capacity (int): Tamaño de la caché en bloques
        verbose (bool): Si es True, muestra progreso en consola
    
    Returns:
        tuple: (promedio, detalles)
            - promedio (dict): Métricas promedio de todas las iteraciones
            - detalles (list): Lista con los resultados de cada iteración
    """
    
    resultados = []
    
    for i in range(iteraciones):
        if verbose:
            print(f"  Iteración {i+1}/{iteraciones}")
        
        generador = PATRONES.get(pattern_name)
        
        if generador is None:
            raise ValueError(f"Patrón '{pattern_name}' no reconocido. "
                           f"Opciones: {list(PATRONES.keys())}")
        
        sequence = generador()
        
        metrics = ejecutar_simulacion(policy, sequence, capacity)
        
        metrics['iteracion'] = i + 1
        metrics['politica'] = policy
        metrics['patron'] = pattern_name
        
        resultados.append(metrics)
    
    promedio = {
        'politica': policy,
        'patron': pattern_name,
        'capacidad': capacity,
        'iteraciones': iteraciones,
        'hits': np.mean([r['hits'] for r in resultados]),
        'misses': np.mean([r['misses'] for r in resultados]),
        'replacements': np.mean([r['replacements'] for r in resultados]),
        'hit_rate': np.mean([r['hit_rate'] for r in resultados]),
        'miss_rate': np.mean([r['miss_rate'] for r in resultados]),
        'std_hit_rate': np.std([r['hit_rate'] for r in resultados])  # Desviación estándar
    }
    
    return promedio, resultados


def ejecutar_experimento_con_semillas(policy, pattern_name, iteraciones=10, capacity=4):
    """
    Ejecuta un experimento con semillas fijas para Random.
    Útil para tener resultados reproducibles.
    
    Args:
        policy (str): Política de reemplazo
        pattern_name (str): Nombre del patrón
        iteraciones (int): Número de iteraciones
        capacity (int): Tamaño de la caché
    
    Returns:
        tuple: (promedio, detalles)
    """
    
    resultados = []
    
    for i in range(iteraciones):
        # Fijar semilla para que cada iteración sea reproducible
        random_seed = i * 100
        np.random.seed(random_seed)
        import random
        random.seed(random_seed)
        
        generador = PATRONES.get(pattern_name)
        sequence = generador()
        
        metrics = ejecutar_simulacion(policy, sequence, capacity)
        metrics['iteracion'] = i + 1
        metrics['semilla'] = random_seed
        metrics['politica'] = policy
        metrics['patron'] = pattern_name
        
        resultados.append(metrics)
    
    promedio = {
        'politica': policy,
        'patron': pattern_name,
        'capacidad': capacity,
        'iteraciones': iteraciones,
        'hits': np.mean([r['hits'] for r in resultados]),
        'misses': np.mean([r['misses'] for r in resultados]),
        'replacements': np.mean([r['replacements'] for r in resultados]),
        'hit_rate': np.mean([r['hit_rate'] for r in resultados]),
        'miss_rate': np.mean([r['miss_rate'] for r in resultados]),
        'std_hit_rate': np.std([r['hit_rate'] for r in resultados])
    }
    
    return promedio, resultados


def ejecutar_todos_los_experimentos(politicas=None, patrones=None, iteraciones=10, 
                                     capacity=4, verbose=True, reproducible=False):
    """
    Ejecuta todas las combinaciones de políticas y patrones.
    
    Args:
        politicas (list): Lista de políticas a evaluar (por defecto: ['LRU', 'FIFO', 'Random'])
        patrones (list): Lista de patrones a evaluar (por defecto: todos)
        iteraciones (int): Número de iteraciones por experimento
        capacity (int): Tamaño de la caché
        verbose (bool): Si es True, muestra progreso en consola
        reproducible (bool): Si es True, usa semillas fijas para Random
    
    Returns:
        tuple: (resultados_promedio, resultados_detallados)
            - resultados_promedio (list): Lista de diccionarios con promedios
            - resultados_detallados (list): Lista de diccionarios con todas las iteraciones
    """
    
    if politicas is None:
        politicas = ['LRU', 'FIFO', 'Random']
    
    if patrones is None:
        patrones = list(PATRONES.keys())
    
    resultados_promedio = []
    resultados_detallados = []
    
    total_experimentos = len(politicas) * len(patrones)
    contador = 0
    
    print("=" * 60)
    print("INICIANDO EXPERIMENTOS COMPLETOS")
    print("=" * 60)
    print(f"Políticas: {politicas}")
    print(f"Patrones: {patrones}")
    print(f"Iteraciones por experimento: {iteraciones}")
    print(f"Capacidad de caché: {capacity} bloques")
    print(f"Modo reproducible: {reproducible}")
    print("=" * 60)
    
    for policy in politicas:
        for pattern in patrones:
            contador += 1
            print(f"\n[{contador}/{total_experimentos}] Ejecutando: {policy} - {pattern}")
            
            if reproducible:
                promedio, detalles = ejecutar_experimento_con_semillas(
                    policy, pattern, iteraciones, capacity
                )
            else:
                promedio, detalles = ejecutar_experimento(
                    policy, pattern, iteraciones, capacity, verbose=False
                )
            
            resultados_promedio.append(promedio)
            resultados_detallados.extend(detalles)
    
    print("\n" + "=" * 60)
    print("EXPERIMENTOS COMPLETADOS")
    print("=" * 60)
    
    return resultados_promedio, resultados_detallados


def exportar_resultados(resultados_promedio, resultados_detallados, output_dir='results'):
    """
    Exporta los resultados a archivos CSV.
    
    Args:
        resultados_promedio (list): Lista de promedios
        resultados_detallados (list): Lista de resultados detallados
        output_dir (str): Directorio donde guardar los archivos
    
    Returns:
        tuple: (df_promedio, df_detalle) DataFrames de pandas
    """
    
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    df_promedio = pd.DataFrame(resultados_promedio)
    df_detalle = pd.DataFrame(resultados_detallados)
    
    df_promedio.to_csv(f'{output_dir}/resultados_promedio.csv', index=False)
    df_detalle.to_csv(f'{output_dir}/resultados_detallados.csv', index=False)
    
    print(f"\n Resultados exportados a '{output_dir}/'")
    print(f"   - {output_dir}/resultados_promedio.csv")
    print(f"   - {output_dir}/resultados_detallados.csv")
    
    return df_promedio, df_detalle


def mostrar_resumen(df_promedio):
    """
    Muestra un resumen formateado de los resultados.
    
    Args:
        df_promedio (DataFrame): DataFrame con los resultados promedio
    """
    
    print("\n" + "=" * 80)
    print("RESUMEN DE RESULTADOS")
    print("=" * 80)
    
    display_df = df_promedio[['politica', 'patron', 'hit_rate', 'miss_rate', 'replacements']].copy()
    display_df = display_df.round({'hit_rate': 2, 'miss_rate': 2, 'replacements': 2})
    display_df.columns = ['Política', 'Patrón', 'Hit Rate (%)', 'Miss Rate (%)', 'Reemplazos']
    
    print(display_df.to_string(index=False))
    
    print("\n" + "=" * 80)
    
    print("\nMEJOR POLÍTICA POR PATRÓN (mayor hit rate):")
    for patron in df_promedio['patron'].unique():
        df_patron = df_promedio[df_promedio['patron'] == patron]
        mejor = df_patron.loc[df_patron['hit_rate'].idxmax()]
        print(f"  {patron}: {mejor['politica']} ({mejor['hit_rate']:.2f}%)")
    
    print("\nPEOR POLÍTICA POR PATRÓN (menor hit rate):")
    for patron in df_promedio['patron'].unique():
        df_patron = df_promedio[df_promedio['patron'] == patron]
        peor = df_patron.loc[df_patron['hit_rate'].idxmin()]
        print(f"  {patron}: {peor['politica']} ({peor['hit_rate']:.2f}%)")
    
    print("\nMEJOR POLÍTICA EN PROMEDIO (todos los patrones):")
    promedio_por_politica = df_promedio.groupby('politica')['hit_rate'].mean()
    for policy, hr in promedio_por_politica.sort_values(ascending=False).items():
        print(f"  {policy}: {hr:.2f}% promedio")


def comparar_con_teoria(df_promedio):
    """
    Compara los resultados obtenidos con lo esperado teóricamente.
    
    Args:
        df_promedio (DataFrame): DataFrame con los resultados promedio
    """
    
    print("\n" + "=" * 80)
    print("COMPARACIÓN CON EXPECTATIVAS TEÓRICAS")
    print("=" * 80)
    
    for _, row in df_promedio.iterrows():
        policy = row['politica']
        patron = row['patron']
        hit_rate = row['hit_rate']
        
        if patron == 'secuencial':
            esperado = 0.4  
            explicacion = "Solo acierta en los primeros 4 accesos"
        
        elif patron == 'localidad':
            if policy == 'LRU':
                esperado = 66.7  
                explicacion = "LRU aprovecha la reutilización de 1,2,3"
            else:
                esperado = 33.3
                explicacion = "FIFO/Random pueden perder la localidad"
        
        elif patron == 'aleatorio':
            esperado = (4 / 20) * 100  # 20% aproximadamente
            explicacion = "Expectativa teórica: capacidad/rango = 4/20 = 20%"
        
        elif patron == 'mixto':
            if policy == 'LRU':
                esperado = 45.0
                explicacion = "LRU beneficio parcial de localidad"
            else:
                esperado = 35.0
                explicacion = "FIFO/Random menor aprovechamiento"
        
        else:
            continue
        
        print(f"\n{policy} - {patron}:")
        print(f"  Obtenido: {hit_rate:.2f}%")
        print(f"  Esperado: {esperado:.2f}%")
        print(f"  Diferencia: {hit_rate - esperado:+.2f}%")
        print(f"  Explicación: {explicacion}")


if __name__ == "__main__":
    
    print("=== EJEMPLO DE USO DE experiment.py ===\n")
    
    print("1. Ejecutando experimento simple...")
    promedio, detalles = ejecutar_experimento(
        policy='LRU', 
        pattern_name='localidad', 
        iteraciones=5,
        verbose=True
    )
    print(f"Resultado promedio: Hit Rate = {promedio['hit_rate']:.2f}%")
    
    print("\n2. Ejecutando todos los experimentos...")
    resultados_prom, resultados_det = ejecutar_todos_los_experimentos(
        iteraciones=5,
        verbose=True,
        reproducible=True
    )
    
    df_prom, df_det = exportar_resultados(resultados_prom, resultados_det)
    
    mostrar_resumen(df_prom)
    
    comparar_con_teoria(df_prom)