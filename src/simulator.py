from src.cache import Cache

def ejecutar_simulacion(policy, access_sequence, capacity=4):
    cache = Cache(capacity, policy)
    
    for block in access_sequence:
        cache.access(block)
    
    return cache.get_metrics()


def ejecutar_simulacion_con_seguimiento(policy, access_sequence, capacity=4):
    cache = Cache(capacity, policy)
    seguimiento = []
    
    for i, block in enumerate(access_sequence):
        resultado = cache.access(block)
        seguimiento.append({
            'acceso': i + 1,
            'bloque': block,
            'resultado': resultado,
            'estado_cache': cache.get_cache_state(),
            'hits': cache.hits,
            'misses': cache.misses,
            'replacements': cache.replacements
        })
    
    metrics = cache.get_metrics()
    
    return metrics, seguimiento


def comparar_politicas(access_sequence, politicas=None, capacity=4):
    if politicas is None:
        politicas = ['LRU', 'FIFO', 'Random']
    
    resultados = {}
    
    for policy in politicas:
        resultados[policy] = ejecutar_simulacion(policy, access_sequence, capacity)
    
    return resultados


def ejecutar_multiples_secuencias(policy, secuencias, capacity=4):
    resultados = []
    
    for i, sequence in enumerate(secuencias):
        metrics = ejecutar_simulacion(policy, sequence, capacity)
        metrics['secuencia_id'] = i + 1
        resultados.append(metrics)
    
    return resultados