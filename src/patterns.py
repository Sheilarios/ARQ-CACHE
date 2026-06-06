"""
Módulo: patterns.py
Generadores de patrones de acceso a memoria para evaluar políticas de caché.

Patrones disponibles:
1. Secuencial: Acceso lineal sin reutilización (1,2,3,4,5,...)
2. Aleatorio: Accesos completamente aleatorios
3. Localidad temporal: Reutilización de un conjunto pequeño de datos (1,2,3,1,2,3,...)
4. Mixto: Combinación de localidad temporal y accesos aleatorios
5. Localidad con salto: Reutilización con cierta distancia entre accesos
6. Peak: Accesos concentrados en un subconjunto muy pequeño
7. Uniforme: Distribución uniforme en todo el rango
"""

import random
import numpy as np


def patron_secuencial(n=1000, inicio=1):
    """
    Patrón secuencial: accede a bloques en orden creciente.
    Representa aplicaciones que recorren datos linealmente (ej: procesamiento de arrays).
    
    Args:
        n (int): Número total de accesos
        inicio (int): Primer bloque a acceder
    
    Returns:
        list: Secuencia de accesos
    """
    return [inicio + i for i in range(n)]


def patron_secuencial_circular(n=1000, rango_min=1, rango_max=20):
    """
    Patrón secuencial circular: cuando llega al final, vuelve al inicio.
    Representa recorridos cíclicos.
    
    Args:
        n (int): Número total de accesos
        rango_min (int): Valor mínimo del bloque
        rango_max (int): Valor máximo del bloque
    
    Returns:
        list: Secuencia de accesos
    """
    rango = rango_max - rango_min + 1
    return [rango_min + (i % rango) for i in range(n)]


def patron_aleatorio(n=1000, rango_min=1, rango_max=20, seed=None):
    """
    Patrón aleatorio: accesos generados aleatoriamente.
    Representa aplicaciones con patrones impredecibles.
    
    Args:
        n (int): Número total de accesos
        rango_min (int): Valor mínimo del bloque
        rango_max (int): Valor máximo del bloque
        seed (int): Semilla para reproducibilidad (opcional)
    
    Returns:
        list: Secuencia de accesos aleatorios
    """
    if seed is not None:
        random.seed(seed)
    
    return [random.randint(rango_min, rango_max) for _ in range(n)]


def patron_localidad(n=1000, conjunto=None):
    """
    Patrón con localidad temporal: reutiliza frecuentemente un conjunto pequeño.
    Representa aplicaciones que trabajan con un working set reducido.
    
    Args:
        n (int): Número total de accesos
        conjunto (list): Conjunto de bloques a reutilizar (por defecto [1,2,3])
    
    Returns:
        list: Secuencia con alta localidad temporal
    """
    if conjunto is None:
        conjunto = [1, 2, 3]
    
    repeticiones = n // len(conjunto) + 1
    return (conjunto * repeticiones)[:n]


def patron_localidad_pesada(n=1000):
    """
    Patrón con localidad temporal muy fuerte.
    Un bloque se accede mucho más frecuentemente que otros.
    Representa aplicaciones con un bloque "caliente".
    
    Args:
        n (int): Número total de accesos
    
    Returns:
        list: Secuencia con localidad extrema
    """
    secuencia = []
    for i in range(n):
        if random.random() < 0.7:
            secuencia.append(1)
        else:
            secuencia.append(random.randint(2, 10))
    return secuencia


def patron_mixto(n=1000, localidad_pct=70, rango_min=1, rango_max=20):
    """
    Patrón mixto: combina localidad temporal con accesos aleatorios.
    Representa aplicaciones reales que tienen zonas calientes y exploración.
    
    Args:
        n (int): Número total de accesos
        localidad_pct (int): Porcentaje de accesos con localidad temporal (0-100)
        rango_min (int): Valor mínimo del bloque
        rango_max (int): Valor máximo del bloque
    
    Returns:
        list: Secuencia mixta
    """
    n_localidad = int(n * localidad_pct / 100)
    n_aleatorio = n - n_localidad
    
    conjunto_local = [1, 2, 3]
    repeticiones = n_localidad // len(conjunto_local) + 1
    localidad = (conjunto_local * repeticiones)[:n_localidad]
    
    aleatorio = [random.randint(rango_min, rango_max) for _ in range(n_aleatorio)]
    
    mixto = localidad + aleatorio
    random.shuffle(mixto)
    
    return mixto


def patron_mixto_ordenado(n=1000, localidad_pct=70):
    """
    Patrón mixto sin mezclar: primero localidad, luego aleatorio.
    Útil para análisis separados.
    
    Args:
        n (int): Número total de accesos
        localidad_pct (int): Porcentaje de accesos con localidad temporal
    
    Returns:
        list: Secuencia con localidad primero, luego aleatorio
    """
    n_localidad = int(n * localidad_pct / 100)
    n_aleatorio = n - n_localidad
    
    localidad = patron_localidad(n_localidad)
    aleatorio = patron_aleatorio(n_aleatorio)
    
    return localidad + aleatorio


def patron_estacional(n=1000, ciclo=50):
    """
    Patrón estacional: fases con alta localidad alternadas con fases exploratorias.
    Representa aplicaciones con cambios de fase.
    
    Args:
        n (int): Número total de accesos
        ciclo (int): Duración de cada fase en accesos
    
    Returns:
        list: Secuencia con cambios de fase
    """
    secuencia = []
    fases = n // ciclo
    
    for fase in range(fases):
        if fase % 2 == 0:
            conjunto = [1, 2, 3]
            secuencia.extend((conjunto * (ciclo // len(conjunto) + 1))[:ciclo])
        else:
            conjunto = [10, 11, 12, 13]
            secuencia.extend((conjunto * (ciclo // len(conjunto) + 1))[:ciclo])
    
    return secuencia[:n]


def patron_con_repeticiones(n=1000, intervalo=10):
    """
    Patrón con repeticiones periódicas.
    Cada cierto número de accesos, se repite un bloque específico.
    
    Args:
        n (int): Número total de accesos
        intervalo (int): Cada cuántos accesos se repite el bloque especial
    
    Returns:
        list: Secuencia con repeticiones periódicas
    """
    secuencia = []
    for i in range(n):
        if i % intervalo == 0:
            secuencia.append(0)  
        else:
            secuencia.append(random.randint(1, 20))
    return secuencia


def patron_uniforme(n=1000, rango_min=1, rango_max=20):
    """
    Patrón con distribución uniforme (cada bloque aparece aproximadamente igual).
    Representa acceso equitativo a todos los bloques.
    
    Args:
        n (int): Número total de accesos
        rango_min (int): Valor mínimo del bloque
        rango_max (int): Valor máximo del bloque
    
    Returns:
        list: Secuencia con distribución uniforme
    """
    num_bloques = rango_max - rango_min + 1
    repeticiones_por_bloque = n // num_bloques
    resto = n % num_bloques
    
    secuencia = []
    for bloque in range(rango_min, rango_max + 1):
        secuencia.extend([bloque] * repeticiones_por_bloque)
    
    for i in range(resto):
        secuencia.append(rango_min + i)
    
    random.shuffle(secuencia)
    return secuencia


def patron_exponencial(n=1000, rango_max=20):
    """
    Patrón con distribución exponencial (bloques bajos más frecuentes).
    Representa aplicaciones donde ciertos bloques son mucho más populares.
    
    Args:
        n (int): Número total de accesos
        rango_max (int): Valor máximo del bloque
    
    Returns:
        list: Secuencia con distribución exponencial
    """
    pesos = [2 ** (-i) for i in range(rango_max)]
    pesos = [p / sum(pesos) for p in pesos]
    
    bloques = list(range(1, rango_max + 1))
    return random.choices(bloques, weights=pesos, k=n)


PATRONES = {
    'secuencial': patron_secuencial,
    'secuencial_circular': patron_secuencial_circular,
    'aleatorio': patron_aleatorio,
    'localidad': patron_localidad,
    'localidad_pesada': patron_localidad_pesada,
    'mixto': patron_mixto,
    'mixto_ordenado': patron_mixto_ordenado,
    'estacional': patron_estacional,
    'repeticiones': patron_con_repeticiones,
    'uniforme': patron_uniforme,
    'exponencial': patron_exponencial
}


PATRONES_PRINCIPALES = {
    'secuencial': patron_secuencial,
    'aleatorio': patron_aleatorio,
    'localidad': patron_localidad,
    'mixto': patron_mixto
}


def generar_todos_los_patrones(n=1000, mostrar_ejemplo=True):
    """
    Genera y muestra ejemplos de todos los patrones disponibles.
    Útil para verificar el comportamiento de cada patrón.
    
    Args:
        n (int): Número de accesos a generar por patrón
        mostrar_ejemplo (bool): Si es True, muestra los primeros accesos
    
    Returns:
        dict: Diccionario con nombre -> secuencia
    """
    resultados = {}
    
    print("=" * 60)
    print("GENERACIÓN DE PATRONES DE ACCESO")
    print("=" * 60)
    
    for nombre, generador in PATRONES.items():
        secuencia = generador(n)
        resultados[nombre] = secuencia
        
        print(f"\n{nombre}:")
        print(f"  Longitud: {len(secuencia)} accesos")
        
        if mostrar_ejemplo:
            ejemplo = secuencia[:20]
            print(f"  Ejemplo: {ejemplo}")
        
        bloques_unicos = len(set(secuencia))
        print(f"  Bloques únicos: {bloques_unicos}")
    
    return resultados


def analizar_patron(secuencia, nombre="Patrón"):
    """
    Analiza las propiedades de un patrón de acceso.
    
    Args:
        secuencia (list): Secuencia de accesos
        nombre (str): Nombre del patrón para mostrar
    
    Returns:
        dict: Estadísticas del patrón
    """
    from collections import Counter
    
    n = len(secuencia)
    bloques_unicos = len(set(secuencia))
    frecuencias = Counter(secuencia)
    
    total_accesos = n
    total_accesos_repetidos = sum(f-1 for f in frecuencias.values() if f > 1)
    tasa_reutilizacion = (total_accesos_repetidos / total_accesos) * 100 if total_accesos > 0 else 0
    
    repeticiones = sum(1 for i in range(1, n) if secuencia[i] == secuencia[i-1])
    prob_repeticion_consecutiva = (repeticiones / (n-1)) * 100 if n > 1 else 0
    
    print(f"\n=== Análisis de patrón: {nombre} ===")
    print(f"  Total accesos: {n}")
    print(f"  Bloques únicos: {bloques_unicos}")
    print(f"  Bloque más frecuente: {frecuencias.most_common(1)[0]}")
    print(f"  Tasa de reutilización: {tasa_reutilizacion:.2f}%")
    print(f"  Repeticiones consecutivas: {prob_repeticion_consecutiva:.2f}%")
    
    return {
        'nombre': nombre,
        'n': n,
        'bloques_unicos': bloques_unicos,
        'frecuencias': frecuencias,
        'tasa_reutilizacion': tasa_reutilizacion,
        'prob_repeticion_consecutiva': prob_repeticion_consecutiva
    }

if __name__ == "__main__":
    
    print("=== EJEMPLOS DE PATRONES DE ACCESO ===\n")
    
    print("1. Patrón secuencial:")
    sec = patron_secuencial(20)
    print(f"   {sec}")
    
    print("\n2. Patrón aleatorio:")
    rand = patron_aleatorio(20, seed=42)
    print(f"   {rand}")
    
    print("\n3. Patrón con localidad temporal:")
    loc = patron_localidad(20)
    print(f"   {loc}")
    
    print("\n4. Patrón mixto (70% localidad + 30% aleatorio):")
    mix = patron_mixto(20, localidad_pct=70)
    print(f"   {mix}")
    
    print("\n" + "=" * 50)
    print("PATRONES PRINCIPALES PARA EXPERIMENTOS")
    print("=" * 50)
    
    for nombre, generador in PATRONES_PRINCIPALES.items():
        secuencia = generador(20)
        print(f"\n{nombre}:")
        print(f"  {secuencia}")
    
    print("\n" + "=" * 50)
    print("ANÁLISIS DETALLADO DE PATRONES")
    print("=" * 50)
    
    for nombre, generador in PATRONES_PRINCIPALES.items():
        secuencia = generador(100)
        analizar_patron(secuencia, nombre)
    
    print("\n" + "=" * 50)
    print("TODOS LOS PATRONES DISPONIBLES")
    print("=" * 50)
    
    todos = generar_todos_los_patrones(20, mostrar_ejemplo=True)
    
    print("\n\nPatrones disponibles:")
    for nombre in PATRONES.keys():
        print(f"  - {nombre}")