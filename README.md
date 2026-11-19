# VERDIX BENCHMARK

Laboratorio universal de rendimiento del ecosistema VERDIX. **Mide y compara; nunca inventa datos.**

## Qué hace hoy (núcleo real, ejecutable)

- Benchmarks **reales** en este equipo: QuickSort, MergeSort, Insertion Sort, Bubble Sort, búsqueda binaria, búsqueda lineal, Fibonacci recursivo/iterativo, multiplicación de matrices 100×100 y Criba de Eratóstenes (2.000.000).
- Lenguajes que **están instalados**: C (gcc -O2), Python 3 (stdlib pura, sin `list.sort()`), JavaScript (Node).
  - Rust y Go: no instalados → no aparecen. Nada se simula.
- Estadísticas honestas por medición: mediana, media, σ, p95, mín, máx, memoria máxima residente (vía `/usr/bin/time -v`), N ejecuciones (por defecto 5, 3 para fib_rec).
- Entrada reproducible: arrays `random.bin` / `sorted.bin` generados con **semilla 42**; mismo SHA-256 para los tres lenguajes.
- Historial en **SQLite** (`results/results.db`) con metadatos del hardware en cada corrida.
- Dashboard estático sin red (`web/index.html`, Chart.js local): gráficos, tabla, **veredicto calculado** a partir de las medianas medidas (no hay opiniones hardcodeadas).

## Uso

```bash
python3 bench.py list        # benchmarks disponibles y lenguajes instalados
python3 bench.py hardware    # CPU/RAM/kernel/commit de git
python3 bench.py run         # toda la suite (~80 s en Celeron 4205U)
python3 bench.py run quicksort sieve --runs 5
python3 bench.py report      # tabla de resultados
python3 bench.py history     # últimas corridas
python3 -m pytest tests/ -q  # 7 pruebas
```

## Resultados medidos (19-nov-2026, CPU ociosa tras pausar NOX-1, Celeron 4205U · 2 núcleos · 3.7 GB)


## Nuevas categorías (medidas en CPU ociosa, 19-nov-2026)
| Categoría | JS (Node) | Python | Qué mide |
|---|---|---|---|
| SHA-256 32 MB | 249.0 ms | 428.2 ms | hash de datos deterministas |
| gzip 8 MB (nivel 6) | 83.6 ms | 90.6 ms | compresión real |
| Parseo 20k JSON | 37.8 ms | 67.5 ms | `JSON.parse` / `json.loads` |
| Regex ~2 MB | 7.6 ms | 74.0 ms | conteo de coincidencias |
| Memoria 64 MB | 42.8 ms | 47.7 ms | asignación + escritura dispersa |
| Monte Carlo 500k | (ver dashboard) | 321.9 ms | π con semilla 42 |

C no implementa estas seis: **se omiten, nunca se simula un resultado**.

| Benchmark | C | JS (Node) | Python |
|---|---|---|---|
| quicksort 40k | 6.3 ms | 55.6 ms | 199.9 ms |
| mergesort 40k | 6.3 ms | 55.6 ms | 199.9 ms |
| insertionsort 2k | 0.7 ms | 9.6 ms | 178.3 ms |
| bubblesort 800 | 2.1 ms | 8.3 ms | 56.8 ms |
| binary_search (×1000) | 0.4 ms | 18.4 ms | 18.9 ms |
| linear_search (×200) | 21.7 ms | 119.4 ms | 3368.2 ms |
| fib_rec(30) | 3.9 ms | 25.1 ms | 264.7 ms |
| matrix 100×100 | 0.9 ms | 27.2 ms | 125.1 ms |
| sieve(2.000.000) | 15.0 ms | 36.5 ms | 210.6 ms |

Metodología completa y notas de honestidad en `web/index.html` (sección Metodología).

## Integración VERDIX

- Dashboard desplegado junto a la web VERDIX en `/benchmark/` (Vercel).
- MAHORAGA podrá consultar `results/latest.json` para detectar regresiones.
- Conexión con VERDIX DEV LAB: el recomendador prioriza herramientas **medidas** aquí (sección "medido en este equipo") cuando existan datos.

## Límites conocidos (honestos)

1. Un solo equipo de medición: no comparar entre máquinas sin avisar.
2. fib_iter(90) es demasiado trivial para sacar conclusión útil (se publica igual).
3. No hay benchmarks de red/OS/bases de datos/IA en esta fase: requieren servicios o instalaciones extra — se añaden con autorización explícita, sin tocar lo existente.
4. El veredicto del dashboard se calcula de las medianas; si σ es alto, fíjate en la desviación y repite.

## Licencia

Parte del ecosistema VERDIX (código abierto, $0 presupuesto, créditos: NOX / VERDIX).
