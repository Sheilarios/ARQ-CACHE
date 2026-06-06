"""
Paquete de simulación de políticas de reemplazo de caché
"""

from src.cache import Cache
from src.patterns import (
    patron_secuencial,
    patron_aleatorio,
    patron_localidad,
    patron_mixto,
    PATRONES
)
from src.simulator import ejecutar_simulacion
from src.experiment import (
    ejecutar_experimento,
    ejecutar_todos_los_experimentos
)

__all__ = [
    'Cache',
    'patron_secuencial',
    'patron_aleatorio',
    'patron_localidad',
    'patron_mixto',
    'PATRONES',
    'ejecutar_simulacion',
    'ejecutar_experimento',
    'ejecutar_todos_los_experimentos'
]