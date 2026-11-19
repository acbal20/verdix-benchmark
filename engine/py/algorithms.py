"""VERDIX BENCHMARK — implementaciones Python puras (sin sort()/built-ins pesados)."""
import sys, time, re, random

def quicksort(arr):
    if len(arr) <= 1: return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    mid  = [x for x in arr if x == pivot]
    right= [x for x in arr if x > pivot]
    return quicksort(left) + mid + quicksort(right)

def mergesort(arr):
    if len(arr) <= 1: return arr
    mid = len(arr)//2
    return merge(mergesort(arr[:mid]), mergesort(arr[mid:]))

def merge(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]: out.append(a[i]); i += 1
        else:            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return out

def insertionsort(arr):
    for i in range(1, len(arr)):
        key, j = arr[i], i - 1
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]; j -= 1
        arr[j+1] = key
    return arr

def bubblesort(arr):
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j+1]: arr[j], arr[j+1] = arr[j+1], arr[j]; swapped = True
        if not swapped: break
    return arr

def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target: return mid
        if arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

def linear_search(arr, target):
    for i, x in enumerate(arr):
        if x == target: return i
    return -1

def fib_rec(n):
    return n if n < 2 else fib_rec(n-1) + fib_rec(n-2)

def fib_iter(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a

def matrix_mul(n):
    a = [[(i + j) % 7 - 3 for j in range(n)] for i in range(n)]
    b = [[(i * j) % 5 - 2 for j in range(n)] for i in range(n)]
    c = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            aik = a[i][k]
            if aik == 0: continue
            row_c, row_b = c[i], b[k]
            for j in range(n): row_c[j] += aik * row_b[j]
    return sum(sum(r) for r in c)

def sieve(n):
    not_p = bytearray(n + 1)
    count = 0
    for p in range(2, n + 1):
        if not not_p[p]:
            count += 1
            start = p * p
            if start <= n:
                not_p[start::p] = b"\x01" * (((n - start) // p) + 1)
    return count

def main():
    bench = sys.argv[1]
    t0 = time.perf_counter()
    if bench == "sha256_32mb":
        import hashlib
        data = bytes(((i * 31 + 7) % 256) for i in range(1 << 20)) * 32
        hashlib.sha256(data).digest()
    elif bench == "gzip_8mb":
        import zlib
        zlib.compress(bytes(range(256)) * 32768, 6)
    elif bench == "json_parse":
        import json
        doc = json.dumps([{"id": i, "name": "verdix" + str(i), "ok": i % 2 == 0} for i in range(20000)])
        json.loads(doc)
    elif bench == "regex_count":
        texto = "NEON Verdix 1234 xyz\n" * 100000
        re.findall(r"[A-Z]{3,}\s\d+", texto)
    elif bench == "mem_alloc":
        buf = bytearray(64 << 20)
        for i in range(0, len(buf), 4096): buf[i] = 1
    elif bench == "pi_monte_carlo":
        r = random.Random(42)
        dentro = sum(1 for _ in range(500000) if r.random()**2 + r.random()**2 <= 1)
    elif bench in ("fib_rec", "fib_iter", "matrix", "sieve"):
        if bench == "fib_rec": fib_rec(30)
        elif bench == "fib_iter": fib_iter(90)
        elif bench == "sieve": sieve(2000000)
        else: matrix_mul(100)
    else:
        import struct
        path = sys.argv[2]
        with open(path, "rb") as f:
            data = f.read()
        n = len(data) // 4
        arr = list(struct.unpack(f"<{n}i", data))
        if bench == "quicksort": quicksort(arr)
        elif bench == "mergesort": mergesort(arr)
        elif bench == "insertionsort": insertionsort(arr)
        elif bench == "bubblesort": bubblesort(arr)
        elif bench == "binary_search":
            for q in range(1000): binary_search(arr, arr[(q * 7919) % n])
        elif bench == "linear_search":
            target = arr[(n * 37) // 41]
            for _ in range(200): linear_search(arr, target)
    t1 = time.perf_counter()
    print(f"internal_ms={(t1-t0)*1000:.3f}")

if __name__ == "__main__":
    main()
