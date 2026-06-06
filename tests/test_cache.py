"""
Módulo: test_cache.py
Pruebas unitarias para el simulador de caché
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cache import Cache
from src.simulator import ejecutar_simulacion, comparar_politicas
from src.patterns import patron_secuencial, patron_aleatorio, patron_localidad, patron_mixto


class TestCacheInicializacion(unittest.TestCase):
    
    def test_inicializacion_lru(self):
        cache = Cache(capacity=4, policy='LRU')
        self.assertEqual(cache.capacity, 4)
        self.assertEqual(cache.policy, 'LRU')
        self.assertEqual(cache.cache, [])
        self.assertEqual(cache.hits, 0)
        self.assertEqual(cache.misses, 0)
        self.assertEqual(cache.replacements, 0)
    
    def test_inicializacion_fifo(self):
        cache = Cache(capacity=8, policy='FIFO')
        self.assertEqual(cache.capacity, 8)
        self.assertEqual(cache.policy, 'FIFO')
        self.assertEqual(cache.cache, [])
    
    def test_inicializacion_random(self):
        cache = Cache(capacity=4, policy='Random')
        self.assertEqual(cache.capacity, 4)
        self.assertEqual(cache.policy, 'Random')
    
    def test_valores_por_defecto(self):
        cache = Cache()
        self.assertEqual(cache.capacity, 4)
        self.assertEqual(cache.policy, 'LRU')


class TestCacheAccesos(unittest.TestCase):
    
    def test_hit_detectado_correctamente(self):
        cache = Cache(capacity=4, policy='LRU')
        cache.access(1)
        cache.access(2)
        cache.access(3)
        cache.access(1)
        
        self.assertEqual(cache.hits, 1)
        self.assertEqual(cache.misses, 3)
    
    def test_miss_detectado_correctamente(self):
        cache = Cache(capacity=4, policy='LRU')
        cache.access(1)
        cache.access(2)
        cache.access(3)
        cache.access(4)
        cache.access(5)
        
        self.assertEqual(cache.hits, 0)
        self.assertEqual(cache.misses, 5)
    
    def test_insert_hasta_llenar(self):
        cache = Cache(capacity=3, policy='LRU')
        cache.access(1)
        cache.access(2)
        cache.access(3)
        
        self.assertEqual(cache.cache, [1, 2, 3])
        self.assertEqual(cache.replacements, 0)
    
    def test_reemplazo_cuando_lleno(self):
        cache = Cache(capacity=3, policy='LRU')
        cache.access(1)
        cache.access(2)
        cache.access(3)
        cache.access(4)
        
        self.assertEqual(len(cache.cache), 3)
        self.assertEqual(cache.replacements, 1)


class TestPoliticaLRU(unittest.TestCase):
    
    def test_lru_reemplaza_menos_reciente(self):
        cache = Cache(capacity=3, policy='LRU')
        cache.access(1)
        cache.access(2)
        cache.access(3)
        cache.access(4)
        
        self.assertNotIn(1, cache.cache)
        self.assertIn(2, cache.cache)
        self.assertIn(3, cache.cache)
        self.assertIn(4, cache.cache)
    
    def test_lru_actualiza_orden_con_hit(self):
        cache = Cache(capacity=3, policy='LRU')
        cache.access(1)
        cache.access(2)
        cache.access(3)
        cache.access(2)
        cache.access(4)
        
        self.assertIn(2, cache.cache)
        self.assertEqual(cache.cache[-1], 4)
    
    def test_lru_secuencia_completa(self):
        cache = Cache(capacity=4, policy='LRU')
        secuencia = [1, 2, 3, 4, 5, 1, 2, 6, 7, 1]
        
        for block in secuencia:
            cache.access(block)
        
        self.assertEqual(cache.hits, 3)
        self.assertEqual(cache.replacements, 5)
    
    def test_lru_con_localidad(self):
        cache = Cache(capacity=4, policy='LRU')
        secuencia = [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
        
        for block in secuencia:
            cache.access(block)
        
        self.assertGreater(cache.hits, cache.misses / 2)


class TestPoliticaFIFO(unittest.TestCase):
    
    def test_fifo_reemplaza_primero(self):
        cache = Cache(capacity=3, policy='FIFO')
        cache.access(1)
        cache.access(2)
        cache.access(3)
        cache.access(4)
        
        self.assertNotIn(1, cache.cache)
        self.assertIn(2, cache.cache)
        self.assertIn(3, cache.cache)
        self.assertIn(4, cache.cache)
    
    def test_fifo_no_actualiza_orden_con_hit(self):
        cache = Cache(capacity=3, policy='FIFO')
        cache.access(1)
        cache.access(2)
        cache.access(3)
        cache.access(2)
        cache.access(4)
        
        self.assertNotIn(1, cache.cache)
        self.assertIn(2, cache.cache)
    
    def test_fifo_orden_estricto(self):
        cache = Cache(capacity=4, policy='FIFO')
        
        for i in range(1, 9):
            cache.access(i)
        
        self.assertEqual(cache.cache, [5, 6, 7, 8])


class TestPoliticaRandom(unittest.TestCase):
    
    def test_random_mantiene_tamano(self):
        cache = Cache(capacity=4, policy='Random')
        
        for i in range(1, 101):
            cache.access(i)
        
        self.assertEqual(len(cache.cache), 4)
    
    def test_random_no_levanta_error(self):
        cache = Cache(capacity=4, policy='Random')
        
        for i in range(1, 101):
            try:
                cache.access(i)
            except Exception as e:
                self.fail(f"Random policy lanzó excepción: {e}")
    
    def test_random_contadores_funcionan(self):
        cache = Cache(capacity=4, policy='Random')
        secuencia = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        for block in secuencia:
            cache.access(block)
        
        total = cache.hits + cache.misses
        self.assertEqual(total, len(secuencia))
        self.assertEqual(cache.replacements, len(secuencia) - 4)


class TestMetricas(unittest.TestCase):
    
    def test_get_metrics_retorna_todos_los_campos(self):
        cache = Cache(capacity=4, policy='LRU')
        cache.access(1)
        cache.access(2)
        
        metrics = cache.get_metrics()
        
        campos_esperados = ['hits', 'misses', 'replacements', 'hit_rate', 'miss_rate', 'total_accesses']
        for campo in campos_esperados:
            self.assertIn(campo, metrics)
    
    def test_hit_rate_correcto(self):
        cache = Cache(capacity=4, policy='LRU')
        cache.access(1)
        cache.access(1)
        cache.access(2)
        cache.access(2)
        cache.access(3)
        
        metrics = cache.get_metrics()
        self.assertEqual(metrics['hit_rate'], 40.0)
    
    def test_miss_rate_correcto(self):
        cache = Cache(capacity=4, policy='LRU')
        cache.access(1)
        cache.access(2)
        cache.access(3)
        cache.access(4)
        cache.access(5)
        
        metrics = cache.get_metrics()
        self.assertEqual(metrics['miss_rate'], 100.0)
    
    def test_hit_rate_cero_sin_accesos(self):
        cache = Cache(capacity=4, policy='LRU')
        metrics = cache.get_metrics()
        self.assertEqual(metrics['hit_rate'], 0.0)
        self.assertEqual(metrics['total_accesses'], 0)


class TestReset(unittest.TestCase):
    
    def test_reset_limpia_contadores(self):
        cache = Cache(capacity=4, policy='LRU')
        
        for i in range(1, 11):
            cache.access(i)
        
        cache.reset()
        
        self.assertEqual(cache.hits, 0)
        self.assertEqual(cache.misses, 0)
        self.assertEqual(cache.replacements, 0)
        self.assertEqual(cache.cache, [])
    
    def test_reset_funciona_despues_de_uso(self):
        cache = Cache(capacity=4, policy='FIFO')
        
        cache.access(1)
        cache.access(2)
        cache.reset()
        cache.access(3)
        
        self.assertEqual(cache.cache, [3])
        self.assertEqual(cache.hits, 0)
        self.assertEqual(cache.misses, 1)


class TestGetCacheState(unittest.TestCase):
    
    def test_get_cache_state_retorna_copia(self):
        cache = Cache(capacity=4, policy='LRU')
        cache.access(1)
        cache.access(2)
        
        estado = cache.get_cache_state()
        self.assertEqual(estado, [1, 2])
        
        estado.append(99)
        self.assertNotEqual(cache.cache, estado)


class TestSimulador(unittest.TestCase):
    
    def test_ejecutar_simulacion_retorna_metricas(self):
        secuencia = [1, 2, 3, 4, 5]
        metrics = ejecutar_simulacion('LRU', secuencia, capacity=4)
        
        self.assertIn('hits', metrics)
        self.assertIn('misses', metrics)
        self.assertIn('hit_rate', metrics)
    
    def test_ejecutar_simulacion_con_cache_llena(self):
        secuencia = list(range(1, 101))
        metrics = ejecutar_simulacion('LRU', secuencia, capacity=4)
        
        self.assertEqual(metrics['hits'], 4)
        self.assertEqual(metrics['replacements'], 96)
    
    def test_comparar_politicas_retorna_tres(self):
        secuencia = [1, 2, 3, 4, 5]
        resultados = comparar_politicas(secuencia, capacity=4)
        
        self.assertEqual(len(resultados), 3)
        self.assertIn('LRU', resultados)
        self.assertIn('FIFO', resultados)
        self.assertIn('Random', resultados)
    
    def test_comparar_politicas_con_politicas_personalizadas(self):
        secuencia = [1, 2, 3]
        resultados = comparar_politicas(secuencia, politicas=['LRU', 'FIFO'], capacity=4)
        
        self.assertEqual(len(resultados), 2)


class TestPatronesConCache(unittest.TestCase):
    
    def test_patron_secuencial_todas_iguales(self):
        secuencia = patron_secuencial(100)
        
        resultado_lru = ejecutar_simulacion('LRU', secuencia, capacity=4)
        resultado_fifo = ejecutar_simulacion('FIFO', secuencia, capacity=4)
        
        self.assertEqual(resultado_lru['hits'], resultado_fifo['hits'])
    
    def test_patron_localidad_lru_superior(self):
        secuencia = patron_localidad(200)
        
        resultado_lru = ejecutar_simulacion('LRU', secuencia, capacity=4)
        resultado_fifo = ejecutar_simulacion('FIFO', secuencia, capacity=4)
        
        self.assertGreaterEqual(resultado_lru['hit_rate'], resultado_fifo['hit_rate'])
    
    def test_patron_aleatorio_similares(self):
        secuencia = patron_aleatorio(500, seed=42)
        
        resultado_lru = ejecutar_simulacion('LRU', secuencia, capacity=4)
        resultado_random = ejecutar_simulacion('Random', secuencia, capacity=4)
        
        diferencia = abs(resultado_lru['hit_rate'] - resultado_random['hit_rate'])
        self.assertLess(diferencia, 15)


class TestCasosLimite(unittest.TestCase):
    
    def test_cache_capacidad_1(self):
        cache = Cache(capacity=1, policy='LRU')
        
        for i in range(1, 11):
            cache.access(i)
        
        self.assertEqual(len(cache.cache), 1)
        self.assertEqual(cache.hits, 0)
        self.assertEqual(cache.replacements, 9)
    
    def test_cache_capacidad_grande(self):
        cache = Cache(capacity=100, policy='LRU')
        
        for i in range(1, 51):
            cache.access(i)
        
        self.assertEqual(len(cache.cache), 50)
        self.assertEqual(cache.replacements, 0)
    
    def test_secuencia_vacia(self):
        cache = Cache(capacity=4, policy='LRU')
        
        metrics = cache.get_metrics()
        
        self.assertEqual(metrics['total_accesses'], 0)
        self.assertEqual(metrics['hit_rate'], 0.0)
    
    def test_mismos_bloques_repetidos(self):
        cache = Cache(capacity=4, policy='LRU')
        
        for _ in range(100):
            cache.access(1)
        
        self.assertEqual(cache.hits, 99)
        self.assertEqual(cache.replacements, 0)
    
    def test_bloques_fuera_de_rango(self):
        cache = Cache(capacity=4, policy='LRU')
        
        cache.access(999)
        cache.access(1000)
        cache.access(1001)
        
        self.assertEqual(cache.cache, [999, 1000, 1001])


class TestStringsYRepresentacion(unittest.TestCase):
    
    def test_str_method(self):
        cache = Cache(capacity=4, policy='LRU')
        cache.access(1)
        cache.access(2)
        
        cadena = str(cache)
        self.assertIn('LRU', cadena)
        self.assertIn('4', cadena)
    
    def test_repr_method(self):
        cache = Cache(capacity=4, policy='LRU')
        representacion = repr(cache)
        
        self.assertIn('capacity=4', representacion)
        self.assertIn('LRU', representacion)


if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)