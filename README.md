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

## Resultados medidos (19-nov-2026, Celeron 4205U · 2 núcleos · 3.7 GB)

| Benchmark | C | JS (Node) | Python |
|---|---|---|---|
| quicksort 40k | 13.9 ms | 190.0 ms | 398.1 ms |
| mergesort 40k | 17.6 ms | 146.6 ms | 401.1 ms |
| insertionsort 2k | 1.0 ms | 15.4 ms | 390.8 ms |
| bubblesort 800 | 5.2 ms | 17.7 ms | 106.4 ms |
| binary_search (×1000) | 0.3 ms | 48.8 ms | 39.7 ms |
| linear_search (×200) | 60.3 ms | 313.9 ms | 6141.4 ms |
| fib_rec(30) | 9.4 ms | 39.6 ms | 599.3 ms |
| matrix 100×100 | 2.4 ms | 58.9 ms | 298.7 ms |
| sieve(2.000.000) | 54.8 ms | 100.0 ms | 437.5 ms |

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
