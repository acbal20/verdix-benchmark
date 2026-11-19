# Seguridad — VERDIX BENCHMARK

## Qué toca y qué no
- Toca: compila y ejecuta SOLO el C/Python/JS incluido en `engine/` (propio, auditado; sin código de terceros).
- Toca el filesystem SOLO en: `results/` (SQLite, .bin generados, latest.json) y `web/` (results-data.js).
- NO almacena ni transmite claves/credenciales/datos personales en ninguna parte.
- NO hace llamadas de red durante la ejecución de benchmarks (el dashboard es estático).
- NO edita archivos fuera de su carpeta.

## Qué NO hace (y nunca debe hacer)
- No ejecuta código descargado de internet.
- No ejecuta binarios sin firma propia sin confirmación del operador.
- No lanza procesos como root ni con sudo.
- No agota recursos: timeout 300 s por ejecución; un benchmark a la vez; N repeticiones configurable.
- No mide nada "por aproximación": si una medición falla, se registra el fallo.

## Datos personales
- Ninguno. El `input_sha256` es de enteros aleatorios (semilla 42), no datos reales.
- El hardware reportado (CPU/RAM/kernel) NO identifica personas.

## Reporte de problemas
Abre un issue en el repositorio VERDIX (el mantenedor es NOX) con pasos para reproducir.
