# Simulador de Políticas de Reemplazo de Caché

## Descripción

Este proyecto implementa un simulador de memoria caché en Python para evaluar y comparar el rendimiento de tres políticas de reemplazo clásicas:

- **LRU (Least Recently Used)** - Elimina el bloque usado menos recientemente
- **FIFO (First In First Out)** - Elimina el bloque más antiguo
- **Random** - Elimina un bloque al azar

El simulador evalúa estas políticas bajo diferentes patrones de acceso a memoria, permitiendo analizar métricas como tasa de aciertos (hit rate), tasa de fallos (miss rate) y número de reemplazos.


## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone https://github.com/Sheilarios/ARQ-CACHE.git
cd proyecto_cache
```
### 2. Intalar dependencias
 pip install -r requirements.txt

 ### Ejecucion
 python main.py
