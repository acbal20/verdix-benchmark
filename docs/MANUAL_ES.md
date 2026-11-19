# Manual — VERDIX BENCHMARK

## Qué es
Laboratorio que compara tecnologías ejecutándolas en tu equipo, con números reales:
mediana, media, desviación, p95 y memoria máxima residente. Nada se estima.

## Requisitos
- Python 3 (el venv de VERDIX o stdlib), gcc, node. Ya los tienes: ver `bench.py hardware`.

## Comandos
| Comando | Qué hace |
|---|---|
| `python3 bench.py list` | Lista benchmarks y lenguajes instalados |
| `python3 bench.py hardware` | Detecta CPU/RAM/kernel/gcc/node/commit |
| `python3 bench.py run` | Ejecuta TODA la suite (~40-80 s con CPU libre) |
| `python3 bench.py run sieve --runs 5` | Ejecuta lo que pidas |
| `python3 bench.py report` | Tabla de resultados |
| `python3 bench.py history` | Últimas corridas |
| `python3 -m pytest tests/ -q` | 7 pruebas |

## Cómo interpretar
- La **mediana** manda. La **desviación** te dice si la medición es confiable: si σ > 30 % de la mediana, repites.
- **RSS** = memoria máxima residente del proceso (KB→MB).
- Compara lenguajes SOLO con el mismo benchmark y el mismo input (ver `input_sha256`).
- No compares máquinas distintas en el mismo gráfico sin advertirlo.

## Añadir un benchmark nuevo
1. Implementa el algoritmo en `engine/c/algorithms.c`, `engine/py/algorithms.py`, `engine/js/algorithms.js`.
2. Añade la entrada en `BENCHMARKS` en `bench.py` (archivo/tamaño/repeticiones).
3. Corre: `python3 bench.py run tu_benchmark` y confirma que compila y mide.
4. Añade una prueba en `tests/` si es posible.

## Añadir un lenguaje nuevo (si se instala)
e.g., Rust: implementa `engine/rust/`, añade a `LANGUAGES` y a `bench_command`. No toques nada más: el motor es agnóstico.

## Honestidad
Si un lenguaje no está instalado, NO aparece. Si una corrida falla, se registra el fallo.
Los resultados dependen del hardware: los gráficos siempre muestran CPU/RAM/fecha.
