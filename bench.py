#!/usr/bin/env python3
"""VERDIX BENCHMARK — orquestador de laboratorio de rendimiento.

Mide, compara y archiva benchmarks reales en este equipo.
Nunca inventa datos: solo mide procesos reales vía /usr/bin/time -v y
time.perf_counter/hrtime. Repetible: entrada seeded (42), mediana de N ejecuciones.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import random
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(ROOT, "results")
DB_PATH = os.path.join(RESULTS, "results.db")
JSON_PATH = os.path.join(RESULTS, "latest.json")
JS_DATA_PATH = os.path.join(ROOT, "web", "results-data.js")
C_BIN = os.path.join(RESULTS, "algorithms_c")
TIME_BIN = "/usr/bin/time"

BENCHMARKS = {
    "quicksort":     {"file": "random.bin", "size": 40000, "runs": 5, "desc": "QuickSort propio sobre 40k enteros"},
    "mergesort":     {"file": "random.bin", "size": 40000, "runs": 5, "desc": "MergeSort propio sobre 40k enteros"},
    "insertionsort": {"file": "random.bin", "size":  2000, "runs": 5, "desc": "Insertion Sort sobre 2k enteros"},
    "bubblesort":    {"file": "random.bin", "size":   800, "runs": 5, "desc": "Bubble Sort sobre 800 enteros"},
    "binary_search": {"file": "sorted.bin", "size": 200000, "runs": 5, "desc": "1.000 búsquedas binarias en array ordenado de 200k"},
    "linear_search": {"file": "sorted.bin", "size": 200000, "runs": 5, "desc": "200 búsquedas lineales (target cerca del final)"},
    "fib_rec":       {"file": None,         "size":    30, "runs": 3, "desc": "Fibonacci(30) recursivo"},
    "fib_iter":      {"file": None,         "size":    90, "runs": 5, "desc": "Fibonacci(90) iterativo"},
    "matrix":        {"file": None,         "size":   100, "runs": 5, "desc": "Multiplicación de matrices 100×100"},
    "sieve":         {"file": None,         "size": 2000000, "runs": 5, "desc": "Criba de Eratóstenes hasta 2.000.000"},
}
LANGUAGES = {
    "c":      {"version_cmd": ["gcc", "-dumpversion"], "label": "C (gcc -O2)"},
    "python": {"version_cmd": [sys.executable, "--version"], "label": "Python (stdlib pura)"},
    "javascript": {"version_cmd": ["node", "--version"], "label": "JavaScript (Node)"},
}


def ensure_inputs():
    os.makedirs(RESULTS, exist_ok=True)
    rnd = random.Random(42)
    data = [rnd.randint(-2_000_000_000, 2_000_000_000) for _ in range(200000)]
    with open(os.path.join(RESULTS, "random.bin"), "wb") as f:
        import struct
        f.write(struct.pack(f"<{len(data)}i", *data))
    sdata = sorted(data)
    with open(os.path.join(RESULTS, "sorted.bin"), "wb") as f:
        import struct
        f.write(struct.pack(f"<{len(sdata)}i", *sdata))


def input_path(spec_file):
    if spec_file == "random.bin":
        path = os.path.join(RESULTS, "random.bin")
        # los sorts usan solo los primeros 40000 / 2000 / 800 elementos
        return path
    if spec_file == "sorted.bin":
        return os.path.join(RESULTS, "sorted.bin")
    return None


def truncated_input(spec_file, size):
    src = input_path(spec_file)
    if src is None:
        return None
    dst = os.path.join(RESULTS, f"_sorted_{size}.bin" if spec_file == "sorted.bin" else f"_rand_{size}.bin")
    if not os.path.exists(dst):
        with open(src, "rb") as f:
            data = f.read()
        n_total = len(data) // 4
        n = min(n_total, size)
        with open(dst, "wb") as f:
            f.write(data[: n * 4])
    return dst


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def compile_c():
    src = os.path.join(ROOT, "engine", "c", "algorithms.c")
    if not os.path.exists(src):
        raise RuntimeError("falta engine/c/algorithms.c")
    subprocess.run(["gcc", "-O2", "-o", C_BIN, src], check=True)


def run_subprocess(cmd):
    """Ejecuta cmd bajo /usr/bin/time -v → (elapsed_ms, max_rss_kb, internal_ms, raw)."""
    full = [TIME_BIN, "-v"] + cmd
    t0 = time.perf_counter()
    proc = subprocess.run(full, capture_output=True, text=True, timeout=300)
    t1 = time.perf_counter()
    internal_ms = None
    m = re.search(r"internal_ms=([0-9.]+)", proc.stdout)
    if m:
        internal_ms = float(m.group(1))
    rss_kb = None
    for line in proc.stderr.splitlines():
        if "Maximum resident set size" in line:
            rss_kb = int(re.search(r"(\d+)", line).group(1))
            break
    elapsed_ms = (t1 - t0) * 1000
    return elapsed_ms, rss_kb, internal_ms, proc.returncode


def stats(values):
    xs = sorted(values)
    n = len(xs)
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / (n - 1) if n > 1 else 0.0
    stdev = math.sqrt(var)
    def pct(p):
        k = (n - 1) * p
        f = math.floor(k); c = math.ceil(k)
        if f == c: return xs[int(k)]
        return xs[f] + (xs[c] - xs[f]) * (k - f)
    return {"n": n, "mean": round(mean, 3), "median": round(pct(0.5), 3), "stdev": round(stdev, 3),
            "min": round(xs[0], 3), "max": round(xs[-1], 3), "p95": round(pct(0.95), 3)}


def bench_command(lang, name, input_file):
    py = sys.executable
    if lang == "c":
        return [C_BIN, name] + ([input_file] if input_file else [])
    if lang == "python":
        return [py, os.path.join(ROOT, "engine", "py", "algorithms.py"), name] + ([input_file] if input_file else [])
    if lang == "javascript":
        return ["node", os.path.join(ROOT, "engine", "js", "algorithms.js"), name] + ([input_file] if input_file else [])
    raise ValueError(lang)


def run_benchmark(name, runs=None, langs=("c", "python", "javascript")):
    spec = BENCHMARKS[name]
    ensure_inputs()
    if "c" in langs:
        compile_c()
    input_file = None
    if spec["file"]:
        input_file = truncated_input(spec["file"], spec["size"])
    in_sha = sha256_of(input_file) if input_file else None
    runs = runs or spec["runs"]
    out = []
    for lang in langs:
        samples, rss_all, ok = [], [], 0
        for _ in range(runs):
            elapsed, rss_kb, internal_ms, rc = run_subprocess(bench_command(lang, name, input_file))
            val = internal_ms if internal_ms is not None else elapsed
            if rc == 0:
                ok += 1
                samples.append(val)
                if rss_kb:
                    rss_all.append(rss_kb)
            else:
                print(f"  ⚠️  {lang}/{name} fallo (rc={rc})", file=sys.stderr)
        if samples:
            st = stats(samples)
            st.update({"benchmark": name, "language": lang, "runs_ok": ok, "runs": runs,
                       "input_sha256": in_sha,
                       "peak_rss_kb": round(sum(rss_all) / len(rss_all)) if rss_all else None})
            out.append(st)
        else:
            out.append({"benchmark": name, "language": lang, "error": "todas las ejecuciones fallaron"})
    return out


def db():
    os.makedirs(RESULTS, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS runs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT DEFAULT CURRENT_TIMESTAMP,
        hostname TEXT, kernel TEXT, cpu_model TEXT, cores INTEGER, ram_mb INTEGER,
        python TEXT, gcc TEXT, node TEXT, git_commit TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER REFERENCES runs(id),
        benchmark TEXT, language TEXT, runs_ok INTEGER, runs INTEGER,
        mean_ms REAL, median_ms REAL, stdev_ms REAL, min_ms REAL, max_ms REAL, p95_ms REAL,
        peak_rss_kb INTEGER, input_sha256 TEXT, description TEXT)""")
    return conn


def hw_info():
    cpu_model = "desconocido"
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    cpu_model = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    ram_mb = 0
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    ram_mb = int(line.split()[1]) // 1024
                    break
    except OSError:
        pass
    commit = None
    try:
        commit = subprocess.check_output(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                                         text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        pass
    return {"hostname": platform.node(), "kernel": platform.release(), "cpu_model": cpu_model,
            "cores": os.cpu_count() or 0, "ram_mb": ram_mb,
            "python": platform.python_version(),
            "gcc": subprocess.run(["gcc", "-dumpversion"], capture_output=True, text=True).stdout.strip(),
            "node": subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip(),
            "git_commit": commit}


def cmd_list(_):
    print("BENCHMARKS disponibles:")
    for name, spec in BENCHMARKS.items():
        print(f"  {name:15} {spec['desc']}")
    print("\nLenguajes: C (gcc -O2), Python (stdlib), JavaScript (Node). Rust/Go no instalados — se omiten honesto.")


def cmd_hardware(_):
    print(json.dumps(hw_info(), ensure_ascii=False, indent=2))


def cmd_run(args):
    names = args.benchmarks or list(BENCHMARKS)
    unknown = [n for n in names if n not in BENCHMARKS]
    if unknown:
        print("Benchmarks desconocidos:", ", ".join(unknown), file=sys.stderr)
        sys.exit(2)
    hw = hw_info()
    print(f"=== VERDIX BENCHMARK — {hw['cpu_model']} · {hw['cores']} núcleos · {hw['ram_mb']} MB RAM ===")
    conn = db()
    cur = conn.execute("INSERT INTO runs(hostname,kernel,cpu_model,cores,ram_mb,python,gcc,node,git_commit) VALUES (?,?,?,?,?,?,?,?,?)",
                       (hw["hostname"], hw["kernel"], hw["cpu_model"], hw["cores"], hw["ram_mb"],
                        hw["python"], hw["gcc"], hw["node"], hw["git_commit"]))
    run_id = cur.lastrowid
    summary = {"run_id": run_id, "when": datetime.now(timezone.utc).isoformat(), "hardware": hw, "results": []}
    for name in names:
        print(f"\n— {name}: {BENCHMARKS[name]['desc']}")
        rows = run_benchmark(name, runs=args.runs)
        for st in rows:
            if "error" in st:
                print(f"   {st['language']:11} ERROR: {st['error']}")
                continue
            print(f"   {st['language']:11} mediana={st['median']:9.1f} ms  media={st['mean']:9.1f} ms  "
                  f"σ={st['stdev']:7.1f}  p95={st['p95']:9.1f}  RSS={st['peak_rss_kb']} KB")
            conn.execute("INSERT INTO results(run_id,benchmark,language,runs_ok,runs,mean_ms,median_ms,stdev_ms,min_ms,max_ms,p95_ms,peak_rss_kb,input_sha256,description) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (run_id, name, st["language"], st["runs_ok"], st["runs"], st["mean"], st["median"],
                          st["stdev"], st["min"], st["max"], st["p95"], st["peak_rss_kb"],
                          st["input_sha256"], BENCHMARKS[name]["desc"]))
            summary["results"].append({**st, "description": BENCHMARKS[name]["desc"]})
    conn.commit()
    conn.close()
    with open(JSON_PATH, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(JS_DATA_PATH, "w") as f:
        f.write("window.BENCH_RESULTS = " + json.dumps(summary, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"\n✅ Resultados guardados en {DB_PATH} y exportados a latest.json + web/results-data.js")


def cmd_report(_):
    conn = db()
    rows = conn.execute("""SELECT benchmark, language, ROUND(median_ms,1), ROUND(mean_ms,1), ROUND(stdev_ms,1), peak_rss_kb
                           FROM results ORDER BY run_id DESC, benchmark, language""").fetchall()
    conn.close()
    if not rows:
        print("Sin resultados todavía. Ejecuta: python3 bench.py run")
        return
    current = None
    for bench, lang, med, mean, sd, rss in rows:
        if bench != current:
            print(f"\n{bench}")
            current = bench
        print(f"   {lang:11} mediana={med:9.1f} ms  media={mean:9.1f} ms  σ={sd:7.1f}  RSS={rss} KB")


def cmd_history(_):
    conn = db()
    runs = conn.execute("SELECT id, ts, cpu_model, cores FROM runs ORDER BY id DESC LIMIT 10").fetchall()
    for rid, ts, cpu, cores in runs:
        n = conn.execute("SELECT COUNT(*) FROM results WHERE run_id=?", (rid,)).fetchone()[0]
        print(f"run #{rid}  {ts}  {cpu}  ({cores} cores)  — {n} resultados")
    conn.close()


def main():
    ap = argparse.ArgumentParser(description="VERDIX BENCHMARK — laboratorio universal de rendimiento")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="listar benchmarks")
    sub.add_parser("hardware", help="detectar hardware")
    p = sub.add_parser("run", help="ejecutar benchmarks")
    p.add_argument("benchmarks", nargs="*", help="nombres (vacío = todos)")
    p.add_argument("--runs", type=int, default=None)
    sub.add_parser("report", help="tabla de resultados")
    sub.add_parser("history", help="últimas ejecuciones")
    args = ap.parse_args()
    {"list": cmd_list, "hardware": cmd_hardware, "run": cmd_run,
     "report": cmd_report, "history": cmd_history}[args.cmd](args)


if __name__ == "__main__":
    main()
