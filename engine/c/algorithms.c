#define _POSIX_C_SOURCE 199309L
/* VERDIX BENCHMARK — implementaciones C (gcc -O2) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

static int cmp_int(const void *a, const void *b) {
    int32_t x = *(const int32_t*)a, y = *(const int32_t*)b;
    return (x > y) - (x < y);
}
static void swap(int32_t *a, int32_t *b) { int32_t t = *a; *a = *b; *b = t; }

/* ---- QuickSort (implementación propia, recursiva) ---- */
static void quicksort(int32_t *arr, long lo, long hi) {
    if (lo >= hi) return;
    int32_t pivot = arr[(lo + hi) / 2];
    long i = lo, j = hi;
    while (i <= j) {
        while (arr[i] < pivot) i++;
        while (arr[j] > pivot) j--;
        if (i <= j) { swap(&arr[i], &arr[j]); i++; j--; }
    }
    if (lo < j) quicksort(arr, lo, j);
    if (i < hi) quicksort(arr, i, hi);
}

/* ---- MergeSort ---- */
static void merge(int32_t *arr, long lo, long mid, long hi, int32_t *tmp) {
    long i = lo, j = mid + 1, k = lo;
    while (i <= mid && j <= hi) tmp[k++] = (arr[i] <= arr[j]) ? arr[i++] : arr[j++];
    while (i <= mid) tmp[k++] = arr[i++];
    while (j <= hi) tmp[k++] = arr[j++];
    for (long x = lo; x <= hi; x++) arr[x] = tmp[x];
}
static void mergesort_rec(int32_t *arr, long lo, long hi, int32_t *tmp) {
    if (lo >= hi) return;
    long mid = (lo + hi) / 2;
    mergesort_rec(arr, lo, mid, tmp);
    mergesort_rec(arr, mid + 1, hi, tmp);
    merge(arr, lo, mid, hi, tmp);
}

/* ---- Insertion Sort ---- */
static void insertionsort(int32_t *arr, long n) {
    for (long i = 1; i < n; i++) {
        int32_t key = arr[i];
        long j = i - 1;
        while (j >= 0 && arr[j] > key) { arr[j + 1] = arr[j]; j--; }
        arr[j + 1] = key;
    }
}

/* ---- Bubble Sort (solo tamaños pequeños) ---- */
static void bubblesort(int32_t *arr, long n) {
    for (long i = 0; i < n - 1; i++) {
        int swapped = 0;
        for (long j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) { swap(&arr[j], &arr[j + 1]); swapped = 1; }
        }
        if (!swapped) break;
    }
}

/* ---- Búsqueda binaria (iterativa) ---- */
static long binary_search(const int32_t *arr, long n, int32_t target) {
    long lo = 0, hi = n - 1;
    while (lo <= hi) {
        long mid = (lo + hi) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}
static long linear_search(const int32_t *arr, long n, int32_t target) {
    for (long i = 0; i < n; i++) if (arr[i] == target) return i;
    return -1;
}

/* ---- Fibonacci ---- */
static long fib_rec(int n) { return n < 2 ? n : fib_rec(n - 1) + fib_rec(n - 2); }
static long fib_iter(int n) {
    long a = 0, b = 1;
    for (int i = 0; i < n; i++) { long t = a + b; a = b; b = t; }
    return a;
}

/* ---- Matriz 100x100 ---- */
static double matrix_mul(int n) {
    static double a[128][128], b[128][128], c[128][128];
    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) { a[i][j] = (i + j) % 7 - 3; b[i][j] = (i * j) % 5 - 2; }
    for (int i = 0; i < n; i++) for (int k = 0; k < n; k++) {
        double aik = a[i][k];
        for (int j = 0; j < n; j++) c[i][j] += aik * b[k][j];
    }
    double s = 0;
    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) s += c[i][j];
    return s;
}

static int32_t *read_input(const char *path, long *n) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long bytes = ftell(f);
    rewind(f);
    *n = bytes / sizeof(int32_t);
    int32_t *arr = malloc(bytes);
    if (fread(arr, 1, bytes, f) != (size_t)bytes) { free(arr); fclose(f); return NULL; }
    fclose(f);
    return arr;
}

static double now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1e6;
}

/* ---- Criba de Eratóstenes (n fijo) ---- */
static long sieve(int n) {
    unsigned char *notp = calloc(n + 1, 1);
    long count = 0;
    for (int p = 2; p <= n; p++) {
        if (!notp[p]) {
            count++;
            for (long m = (long)p * p; m <= n; m += p) notp[m] = 1;
        }
    }
    free(notp);
    return count;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "uso: algorithms_c <bench> [array.bin]\n"); return 1; }
    const char *bench = argv[1];
    long n = 0;
    int32_t *arr = NULL;
    int needs_input = strcmp(bench, "matrix") != 0 && strcmp(bench, "fib_rec") != 0 &&
                      strcmp(bench, "fib_iter") != 0 && strcmp(bench, "sieve") != 0;

    if (needs_input) {
        if (argc < 3) { fprintf(stderr, "%s requiere array.bin\n", bench); return 1; }
        arr = read_input(argv[2], &n);
        if (!arr) { fprintf(stderr, "no se pudo leer input\n"); return 1; }
    }

    double t0 = now_ms();

    if (strcmp(bench, "quicksort") == 0) quicksort(arr, 0, n - 1);
    else if (strcmp(bench, "mergesort") == 0) { int32_t *tmp = malloc(n * sizeof(int32_t)); mergesort_rec(arr, 0, n - 1, tmp); free(tmp); }
    else if (strcmp(bench, "insertionsort") == 0) insertionsort(arr, n);
    else if (strcmp(bench, "bubblesort") == 0) bubblesort(arr, n);
    else if (strcmp(bench, "binary_search") == 0) {
        /* arr[] ya llega ordenado desde el orquestador (input: sorted.bin) */
        long hits = 0;
        for (long q = 0; q < 1000; q++) hits += binary_search(arr, n, arr[(q * 7919) % n]);
        if (hits < -1000) printf("imposible\n");
    } else if (strcmp(bench, "linear_search") == 0) {
        long hits = 0;
        int32_t target = arr[(n * 37) / 41]; /* target cerca del final: peor caso típico */
        for (long q = 0; q < 200; q++) hits += linear_search(arr, n, target);
        if (hits < 0) printf("imposible\n");
    } else if (strcmp(bench, "fib_rec") == 0) { volatile long r = fib_rec(30); (void)r; }
    else if (strcmp(bench, "fib_iter") == 0) { volatile long r = fib_iter(90); (void)r; }
    else if (strcmp(bench, "matrix") == 0) { volatile double r = matrix_mul(100); (void)r; }
    else if (strcmp(bench, "sieve") == 0) { volatile long r = sieve(2000000); (void)r; }
    else { fprintf(stderr, "bench desconocido: %s\n", bench); free(arr); return 1; }

    double t1 = now_ms();
    printf("internal_ms=%.3f\n", t1 - t0);
    free(arr);
    return 0;
}
