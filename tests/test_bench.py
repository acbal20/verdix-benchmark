"""Pruebas de VERDIX BENCHMARK (sin red, sin instalar nada)."""
import json
import os
import sqlite3
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bench  # noqa: E402


def test_benchmarks_config_valido():
    for name, spec in bench.BENCHMARKS.items():
        assert "desc" in spec and isinstance(spec["desc"], str) and spec["desc"]
        assert "runs" in spec and spec["runs"] >= 1
        assert "size" in spec and spec["size"] >= 1
        assert spec["file"] in (None, "random.bin", "sorted.bin")


def test_stats_basico():
    st = bench.stats([10.0, 20.0, 30.0, 40.0, 50.0])
    assert st["n"] == 5
    assert st["median"] == 30.0
    assert st["mean"] == 30.0
    assert st["min"] == 10.0
    assert st["max"] == 50.0
    assert st["stdev"] > 0
    assert st["p95"] >= 40.0


def test_stats_un_elemento():
    st = bench.stats([42.0])
    assert st["n"] == 1
    assert st["stdev"] == 0.0


def test_hardware_detecta_cpu():
    hw = bench.hw_info()
    assert hw["cores"] >= 1
    assert hw["ram_mb"] > 0
    assert "Intel" in hw["cpu_model"] or hw["cpu_model"] == "desconocido"


def test_sqlite_esquema():
    conn = bench.db()
    cols = [r[1] for r in conn.execute("PRAGMA table_info(results)").fetchall()]
    for expected in ("benchmark", "language", "median_ms", "peak_rss_kb", "input_sha256"):
        assert expected in cols
    conn.close()


def test_cli_list_exit_cero():
    rc = subprocess.run([sys.executable, os.path.join(ROOT, "bench.py"), "list"],
                        capture_output=True, text=True)
    assert rc.returncode == 0
    assert "quicksort" in rc.stdout


def test_lenguajes_soportados():
    for lang in ("c", "python", "javascript"):
        cmd = bench.bench_command(lang, "fib_iter", None)
        assert isinstance(cmd, list) and len(cmd) >= 2
