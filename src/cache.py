"""
Módulo: cache.py
Implementación de memoria caché con políticas de reemplazo:
- LRU (Least Recently Used)
- FIFO (First In First Out)
- Random (Aleatorio)
"""

from collections import OrderedDict, deque
import random


class Cache:
    """
    Simulador de memoria caché con diferentes políticas de reemplazo.
    
    Atributos:
        capacity (int): Número máximo de bloques que puede almacenar la caché
        policy (str): Política de reemplazo ('LRU', 'FIFO', 'Random')
        cache (list): Lista que almacena los bloques actuales en la caché
        hits (int): Contador de aciertos
        misses (int): Contador de fallos
        replacements (int): Contador de reemplazos realizados
        order (OrderedDict): Estructura auxiliar para LRU
        queue (deque): Estructura auxiliar para FIFO
    """
    
    def __init__(self, capacity=4, policy='LRU'):
        """
        Inicializa la memoria caché.
        
        Args:
            capacity (int): Capacidad máxima de la caché en bloques
            policy (str): Política de reemplazo ('LRU', 'FIFO', 'Random')
        """
        self.capacity = capacity
        self.policy = policy
        
        self.cache = []         
        
        self.hits = 0
        self.misses = 0
        self.replacements = 0
        
        self.order = None
        self.queue = None
        
        if policy == 'LRU':
            self.order = OrderedDict()
        elif policy == 'FIFO':
            self.queue = deque()
    
    def access(self, block):
        """
        Procesa un acceso a un bloque de memoria.
        
        Args:
            block (int): Número de bloque al que se accede
            
        Returns:
            str: Resultado del acceso ('HIT', 'MISS', 'MISS (insert)', 'MISS (replace)')
        """
        
        if block in self.cache:
            self.hits += 1
            
            if self.policy == 'LRU':
                self.cache.remove(block)
                self.cache.append(block)
                self.order.move_to_end(block)
            
            elif self.policy == 'FIFO':
                pass
            
            elif self.policy == 'Random':
                pass
            
            return "HIT"
        
        self.misses += 1
        
        if len(self.cache) < self.capacity:
            self.cache.append(block)
            
            if self.policy == 'LRU':
                self.order[block] = True
            
            elif self.policy == 'FIFO':
                self.queue.append(block)
            
            return "MISS (insert)"
        
        self.replacements += 1
        self._replace(block)
        
        return "MISS (replace)"
    
    def _replace(self, new_block):
        """
        Reemplaza un bloque existente según la política.
        
        Args:
            new_block (int): Nuevo bloque a insertar
        """
        
        if self.policy == 'LRU':
            removed = self.cache.pop(0)
            self.cache.append(new_block)
            if removed in self.order:
                del self.order[removed]
            self.order[new_block] = True
        
        elif self.policy == 'FIFO':
            removed = self.cache.pop(0)
            self.cache.append(new_block)
            if self.queue and self.queue[0] == removed:
                self.queue.popleft()
            self.queue.append(new_block)
        
        elif self.policy == 'Random':
            index = random.randint(0, len(self.cache) - 1)
            self.cache[index] = new_block
    
    def get_metrics(self):
        """
        Calcula y retorna las métricas actuales de la simulación.
        
        Returns:
            dict: Diccionario con hits, misses, replacements, hit_rate, miss_rate
        """
        total = self.hits + self.misses
        
        if total > 0:
            hit_rate = (self.hits / total) * 100
            miss_rate = (self.misses / total) * 100
        else:
            hit_rate = 0.0
            miss_rate = 0.0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'replacements': self.replacements,
            'hit_rate': round(hit_rate, 2),
            'miss_rate': round(miss_rate, 2),
            'total_accesses': total
        }
    
    def reset(self):
        """
        Reinicia la caché a su estado inicial.
        Útil para ejecutar múltiples simulaciones sin crear nuevos objetos.
        """
        self.cache = []
        self.hits = 0
        self.misses = 0
        self.replacements = 0
        
        if self.policy == 'LRU':
            self.order = OrderedDict()
        elif self.policy == 'FIFO':
            self.queue = deque()
    
    def get_cache_state(self):
        """
        Retorna el estado actual de la caché.
        
        Returns:
            list: Copia de la lista de bloques en caché
        """
        return self.cache.copy()
    
    def __str__(self):
        """
        Representación en string de la caché.
        """
        return f"Cache(policy={self.policy}, capacity={self.capacity}, state={self.cache})"
    
    def __repr__(self):
        """
        Representación oficial de la caché.
        """
        return f"Cache(capacity={self.capacity}, policy='{self.policy}')"


if __name__ == "__main__":
    
    print("=" * 50)
    print("PRUEBA DE POLÍTICAS DE REEMPLAZO")
    print("=" * 50)
    
    test_sequence = [1, 2, 3, 4, 5, 1, 2, 6, 7, 1]
    
    for policy in ['LRU', 'FIFO', 'Random']:
        print(f"\n--- Política: {policy} ---")
        cache = Cache(capacity=4, policy=policy)
        
        for block in test_sequence:
            result = cache.access(block)
            print(f"Acceso {block}: {result:15} | Caché: {cache.get_cache_state()}")
        
        print(f"\nMétricas finales: {cache.get_metrics()}")