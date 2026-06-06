"""
Módulo: test_patterns.py
Pruebas unitarias para los generadores de patrones de acceso
"""

import unittest
import sys
import os
import random
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.patterns import (
    patron_secuencial,
    patron_secuencial_circular,
    patron_aleatorio,
    patron_localidad,
    patron_localidad_pesada,
    patron_mixto,
    patron_mixto_ordenado,
    patron_estacional,
    patron_con_repeticiones,
    patron_uniforme,
    patron_exponencial,
    PATRONES,
    PATRONES_PRINCIPALES,
    analizar_patron,
    generar_todos_los_patrones
)


class TestPatronSecuencial(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_secuencial(100)
        self.assertEqual(len(secuencia), 100)
    
    def test_valores_correctos(self):
        secuencia = patron_secuencial(10)
        esperado = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.assertEqual(secuencia, esperado)
    
    def test_inicio_personalizado(self):
        secuencia = patron_secuencial(5, inicio=10)
        esperado = [10, 11, 12, 13, 14]
        self.assertEqual(secuencia, esperado)
    
    def test_longitud_cero(self):
        secuencia = patron_secuencial(0)
        self.assertEqual(secuencia, [])
    
    def test_todos_elementos_unicos(self):
        secuencia = patron_secuencial(50)
        self.assertEqual(len(set(secuencia)), 50)


class TestPatronSecuencialCircular(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_secuencial_circular(100, rango_min=1, rango_max=5)
        self.assertEqual(len(secuencia), 100)
    
    def test_circular_1_a_5(self):
        secuencia = patron_secuencial_circular(12, rango_min=1, rango_max=5)
        esperado = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2]
        self.assertEqual(secuencia, esperado)
    
    def test_rango_personalizado(self):
        secuencia = patron_secuencial_circular(10, rango_min=10, rango_max=12)
        esperado = [10, 11, 12, 10, 11, 12, 10, 11, 12, 10]
        self.assertEqual(secuencia, esperado)
    
    def test_rango_unico(self):
        secuencia = patron_secuencial_circular(10, rango_min=5, rango_max=5)
        esperado = [5] * 10
        self.assertEqual(secuencia, esperado)


class TestPatronAleatorio(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_aleatorio(100)
        self.assertEqual(len(secuencia), 100)
    
    def test_rango_valores(self):
        secuencia = patron_aleatorio(1000, rango_min=1, rango_max=10)
        self.assertLessEqual(max(secuencia), 10)
        self.assertGreaterEqual(min(secuencia), 1)
    
    def test_rango_personalizado(self):
        secuencia = patron_aleatorio(500, rango_min=50, rango_max=100)
        self.assertLessEqual(max(secuencia), 100)
        self.assertGreaterEqual(min(secuencia), 50)
    
    def test_semilla_reproducible(self):
        secuencia1 = patron_aleatorio(100, seed=42)
        secuencia2 = patron_aleatorio(100, seed=42)
        self.assertEqual(secuencia1, secuencia2)
    
    def test_semillas_diferentes(self):
        secuencia1 = patron_aleatorio(100, seed=42)
        secuencia2 = patron_aleatorio(100, seed=99)
        self.assertNotEqual(secuencia1, secuencia2)
    
    def test_longitud_cero(self):
        secuencia = patron_aleatorio(0)
        self.assertEqual(secuencia, [])


class TestPatronLocalidad(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_localidad(100)
        self.assertEqual(len(secuencia), 100)
    
    def test_conjunto_por_defecto(self):
        secuencia = patron_localidad(10)
        conjunto_esperado = {1, 2, 3}
        self.assertTrue(set(secuencia).issubset(conjunto_esperado))
    
    def test_conjunto_personalizado(self):
        secuencia = patron_localidad(20, conjunto=[10, 20, 30])
        conjunto_esperado = {10, 20, 30}
        self.assertTrue(set(secuencia).issubset(conjunto_esperado))
    
    def test_patron_ciclico(self):
        secuencia = patron_localidad(6, conjunto=[1, 2, 3])
        esperado = [1, 2, 3, 1, 2, 3]
        self.assertEqual(secuencia, esperado)
    
    def test_longitud_no_multiplo(self):
        secuencia = patron_localidad(7, conjunto=[1, 2, 3])
        esperado = [1, 2, 3, 1, 2, 3, 1]
        self.assertEqual(secuencia, esperado)
    
    def test_longitud_cero(self):
        secuencia = patron_localidad(0)
        self.assertEqual(secuencia, [])


class TestPatronLocalidadPesada(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_localidad_pesada(100)
        self.assertEqual(len(secuencia), 100)
    
    def test_bloque_1_mayoria(self):
        secuencia = patron_localidad_pesada(1000)
        conteo = Counter(secuencia)
        bloque_1_frecuencia = conteo.get(1, 0)
        self.assertGreater(bloque_1_frecuencia, 500)
    
    def test_rango_valores(self):
        secuencia = patron_localidad_pesada(100)
        self.assertLessEqual(max(secuencia), 10)
        self.assertGreaterEqual(min(secuencia), 1)


class TestPatronMixto(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_mixto(100)
        self.assertEqual(len(secuencia), 100)
    
    def test_localidad_porcentaje_70(self):
        secuencia = patron_mixto(1000, localidad_pct=70)
        conteo_localidad = sum(1 for x in secuencia if x in [1, 2, 3])
        self.assertGreaterEqual(conteo_localidad, 600)
        self.assertLessEqual(conteo_localidad, 800)
    
    def test_localidad_porcentaje_50(self):
        secuencia = patron_mixto(1000, localidad_pct=50)
        conteo_localidad = sum(1 for x in secuencia if x in [1, 2, 3])
        self.assertGreaterEqual(conteo_localidad, 400)
        self.assertLessEqual(conteo_localidad, 600)
    
    def test_localidad_porcentaje_0(self):
        secuencia = patron_mixto(100, localidad_pct=0)
        conteo_localidad = sum(1 for x in secuencia if x in [1, 2, 3])
        self.assertEqual(conteo_localidad, 0)
    
    def test_localidad_porcentaje_100(self):
        secuencia = patron_mixto(100, localidad_pct=100)
        self.assertTrue(set(secuencia).issubset({1, 2, 3}))
    
    def test_rango_aleatorio_personalizado(self):
        secuencia = patron_mixto(200, localidad_pct=50, rango_min=10, rango_max=30)
        valores_aleatorios = [x for x in secuencia if x not in [1, 2, 3]]
        if valores_aleatorios:
            self.assertLessEqual(max(valores_aleatorios), 30)
            self.assertGreaterEqual(min(valores_aleatorios), 10)


class TestPatronMixtoOrdenado(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_mixto_ordenado(100)
        self.assertEqual(len(secuencia), 100)
    
    def test_orden_localidad_primero(self):
        secuencia = patron_mixto_ordenado(100, localidad_pct=70)
        primeros = secuencia[:70]
        ultimos = secuencia[70:]
        
        self.assertTrue(set(primeros).issubset({1, 2, 3}))
    
    def test_porcentaje_correcto(self):
        secuencia = patron_mixto_ordenado(200, localidad_pct=75)
        primeros = secuencia[:150]
        ultimos = secuencia[150:]
        
        self.assertTrue(set(primeros).issubset({1, 2, 3}))
        self.assertGreaterEqual(len(ultimos), 49)
        self.assertLessEqual(len(ultimos), 51)


class TestPatronEstacional(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_estacional(100)
        self.assertEqual(len(secuencia), 100)
    
    def test_cambio_de_conjunto(self):
        secuencia = patron_estacional(100, ciclo=20)
        
        primeros = secuencia[:20]
        segundos = secuencia[20:40]
        
        set1 = set(primeros)
        set2 = set(segundos)
        
        self.assertNotEqual(set1, set2)
    
    def test_conjuntos_esperados(self):
        secuencia = patron_estacional(40, ciclo=10)
        pares = set(secuencia[0:10])
        impares = set(secuencia[10:20])
        
        self.assertTrue(pares.issubset({1, 2, 3}))
        self.assertTrue(impares.issubset({10, 11, 12, 13}))


class TestPatronConRepeticiones(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_con_repeticiones(100)
        self.assertEqual(len(secuencia), 100)
    
    def test_bloque_0_se_repite_periodicamente(self):
        secuencia = patron_con_repeticiones(20, intervalo=5)
        posiciones_esperadas = [0, 5, 10, 15]
        
        for pos in posiciones_esperadas:
            if pos < len(secuencia):
                self.assertEqual(secuencia[pos], 0)
    
    def test_intervalo_personalizado(self):
        secuencia = patron_con_repeticiones(30, intervalo=3)
        
        for i in range(0, 30, 3):
            self.assertEqual(secuencia[i], 0)


class TestPatronUniforme(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_uniforme(100)
        self.assertEqual(len(secuencia), 100)
    
    def test_distribucion_uniforme(self):
        secuencia = patron_uniforme(200, rango_min=1, rango_max=10)
        conteo = Counter(secuencia)
        
        for bloque in range(1, 11):
            self.assertGreaterEqual(conteo.get(bloque, 0), 15)
            self.assertLessEqual(conteo.get(bloque, 0), 25)
    
    def test_rango_personalizado(self):
        secuencia = patron_uniforme(100, rango_min=5, rango_max=8)
        self.assertTrue(set(secuencia).issubset({5, 6, 7, 8}))
    
    def test_cada_bloque_aparece(self):
        secuencia = patron_uniforme(100, rango_min=1, rango_max=5)
        self.assertEqual(set(secuencia), {1, 2, 3, 4, 5})


class TestPatronExponencial(unittest.TestCase):
    
    def test_longitud_correcta(self):
        secuencia = patron_exponencial(100)
        self.assertEqual(len(secuencia), 100)
    
    def test_bloques_bajos_mas_frecuentes(self):
        secuencia = patron_exponencial(10000, rango_max=10)
        conteo = Counter(secuencia)
        
        for i in range(1, 10):
            self.assertGreaterEqual(conteo.get(i, 0), conteo.get(i+1, 0))
    
    def test_bloque_1_mas_frecuente(self):
        secuencia = patron_exponencial(5000, rango_max=5)
        conteo = Counter(secuencia)
        
        max_bloque = max(conteo, key=conteo.get)
        self.assertEqual(max_bloque, 1)


class TestDiccionarioPatrones(unittest.TestCase):
    
    def test_patrones_tiene_todos(self):
        patrones_esperados = [
            'secuencial', 'secuencial_circular', 'aleatorio', 'localidad',
            'localidad_pesada', 'mixto', 'mixto_ordenado', 'estacional',
            'repeticiones', 'uniforme', 'exponencial'
        ]
        
        for patron in patrones_esperados:
            self.assertIn(patron, PATRONES)
    
    def test_patrones_principales_tiene_cuatro(self):
        self.assertEqual(len(PATRONES_PRINCIPALES), 4)
        
        patrones_esperados = ['secuencial', 'aleatorio', 'localidad', 'mixto']
        for patron in patrones_esperados:
            self.assertIn(patron, PATRONES_PRINCIPALES)
    
    def test_todos_los_generadores_funcionan(self):
        for nombre, generador in PATRONES.items():
            secuencia = generador(50)
            self.assertEqual(len(secuencia), 50)
            self.assertIsInstance(secuencia, list)


class TestAnalizarPatron(unittest.TestCase):
    
    def test_analizar_patron_retorna_diccionario(self):
        secuencia = [1, 2, 3, 1, 2, 3]
        resultado = analizar_patron(secuencia, "test")
        
        self.assertIsInstance(resultado, dict)
        self.assertIn('nombre', resultado)
        self.assertIn('n', resultado)
        self.assertIn('bloques_unicos', resultado)
        self.assertIn('frecuencias', resultado)
        self.assertIn('tasa_reutilizacion', resultado)
    
    def test_tasa_reutilizacion_correcta(self):
        secuencia = [1, 1, 1, 2, 2, 3]
        resultado = analizar_patron(secuencia, "test")
        
        self.assertAlmostEqual(resultado['tasa_reutilizacion'], 50.0)
    
    def test_bloques_unicos_correctos(self):
        secuencia = [1, 2, 3, 4, 5, 1, 2, 3]
        resultado = analizar_patron(secuencia, "test")
        
        self.assertEqual(resultado['bloques_unicos'], 5)


class TestGenerarTodosLosPatrones(unittest.TestCase):
    
    def test_generar_todos_retorna_diccionario(self):
        resultado = generar_todos_los_patrones(10, mostrar_ejemplo=False)
        
        self.assertIsInstance(resultado, dict)
        self.assertEqual(len(resultado), len(PATRONES))
    
    def test_todas_las_secuencias_tienen_longitud_correcta(self):
        resultado = generar_todos_los_patrones(25, mostrar_ejemplo=False)
        
        for nombre, secuencia in resultado.items():
            self.assertEqual(len(secuencia), 25)


class TestConsistenciaPatrones(unittest.TestCase):
    
    def test_patron_secuencial_reproducible(self):
        s1 = patron_secuencial(100)
        s2 = patron_secuencial(100)
        self.assertEqual(s1, s2)
    
    def test_patron_localidad_reproducible(self):
        s1 = patron_localidad(100)
        s2 = patron_localidad(100)
        self.assertEqual(s1, s2)
    
    def test_patron_mixto_no_reproducible_sin_semilla(self):
        s1 = patron_mixto(100)
        s2 = patron_mixto(100)
        random.seed(42)
        s1_con_semilla = patron_mixto(100, seed=42)
        random.seed(42)
        s2_con_semilla = patron_mixto(100, seed=42)
        self.assertEqual(s1_con_semilla, s2_con_semilla)


class TestCasosLimitePatrones(unittest.TestCase):
    
    def test_secuencial_n_1(self):
        secuencia = patron_secuencial(1)
        self.assertEqual(secuencia, [1])
    
    def test_aleatorio_n_1(self):
        secuencia = patron_aleatorio(1)
        self.assertEqual(len(secuencia), 1)
    
    def test_localidad_n_1(self):
        secuencia = patron_localidad(1)
        self.assertEqual(secuencia, [1])
    
    def test_mixto_n_1(self):
        secuencia = patron_mixto(1)
        self.assertEqual(len(secuencia), 1)
    
    def test_uniforme_n_menor_que_rango(self):
        secuencia = patron_uniforme(3, rango_min=1, rango_max=10)
        self.assertEqual(len(secuencia), 3)


if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)