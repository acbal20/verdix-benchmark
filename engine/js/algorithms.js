// VERDIX BENCHMARK — implementaciones JS (node)
'use strict';
const fs = require('fs');

function quicksort(arr) {
  if (arr.length <= 1) return arr;
  const pivot = arr[arr.length >> 1];
  const left = [], mid = [], right = [];
  for (const x of arr) {
    if (x < pivot) left.push(x); else if (x > pivot) right.push(x); else mid.push(x);
  }
  return quicksort(left).concat(mid, quicksort(right));
}
function mergesort(arr) {
  if (arr.length <= 1) return arr;
  const mid = arr.length >> 1;
  return merge(mergesort(arr.slice(0, mid)), mergesort(arr.slice(mid)));
}
function merge(a, b) {
  const out = []; let i = 0, j = 0;
  while (i < a.length && j < b.length) out.push(a[i] <= b[j] ? a[i++] : b[j++]);
  while (i < a.length) out.push(a[i++]);
  while (j < b.length) out.push(b[j++]);
  return out;
}
function insertionsort(arr) {
  for (let i = 1; i < arr.length; i++) {
    const key = arr[i]; let j = i - 1;
    while (j >= 0 && arr[j] > key) { arr[j + 1] = arr[j]; j--; }
    arr[j + 1] = key;
  }
  return arr;
}
function bubblesort(arr) {
  for (let i = 0; i < arr.length - 1; i++) {
    let swapped = false;
    for (let j = 0; j < arr.length - 1 - i; j++) {
      if (arr[j] > arr[j + 1]) { const t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t; swapped = true; }
    }
    if (!swapped) break;
  }
  return arr;
}
function binarySearch(arr, target) {
  let lo = 0, hi = arr.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid] === target) return mid;
    if (arr[mid] < target) lo = mid + 1; else hi = mid - 1;
  }
  return -1;
}
function linearSearch(arr, target) {
  for (let i = 0; i < arr.length; i++) if (arr[i] === target) return i;
  return -1;
}
function fibRec(n) { return n < 2 ? n : fibRec(n - 1) + fibRec(n - 2); }
function fibIter(n) { let a = 0, b = 1; for (let i = 0; i < n; i++) { const t = a + b; a = b; b = t; } return a; }
function matrixMul(n) {
  const a = [], b = [], c = [];
  for (let i = 0; i < n; i++) { a.push([]); b.push([]); c.push(new Array(n).fill(0));
    for (let j = 0; j < n; j++) { a[i][j] = (i + j) % 7 - 3; b[i][j] = (i * j) % 5 - 2; } }
  for (let i = 0; i < n; i++) for (let k = 0; k < n; k++) {
    const aik = a[i][k]; if (aik === 0) continue;
    for (let j = 0; j < n; j++) c[i][j] += aik * b[k][j];
  }
  return c.flat().reduce((s, x) => s + x, 0);
}

function sieve(n) {
  const notP = new Uint8Array(n + 1);
  let count = 0;
  for (let p = 2; p <= n; p++) {
    if (!notP[p]) {
      count++;
      for (let m = p * p; m <= n; m += p) notP[m] = 1;
    }
  }
  return count;
}

const bench = process.argv[2];
const t0 = process.hrtime.bigint();
if (bench === 'fib_rec') fibRec(30);
else if (bench === 'fib_iter') fibIter(90);
else if (bench === 'matrix') matrixMul(100);
else if (bench === 'sieve') sieve(2000000);
else {
  const buf = fs.readFileSync(process.argv[3]);
  const n = buf.length / 4;
  const arr = new Int32Array(n);
  for (let i = 0; i < n; i++) arr[i] = buf.readInt32LE(i * 4);
  if (bench === 'quicksort') quicksort(Array.from(arr));
  else if (bench === 'mergesort') mergesort(Array.from(arr));
  else if (bench === 'insertionsort') insertionsort(arr);
  else if (bench === 'bubblesort') bubblesort(arr);
  else if (bench === 'binary_search') { for (let q = 0; q < 1000; q++) binarySearch(arr, arr[(q * 7919) % n]); }
  else if (bench === 'linear_search') { const t = arr[(n * 37) / 41 | 0]; for (let q = 0; q < 200; q++) linearSearch(arr, t); }
}
const t1 = process.hrtime.bigint();
console.log('internal_ms=' + (Number(t1 - t0) / 1e6).toFixed(3));
