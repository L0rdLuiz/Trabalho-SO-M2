#!/usr/bin/env python3
# worker_fifo.py
import sys, struct, os, threading, time
from threading import Semaphore, Lock, Thread

QMAX = 128

class CircularQueue:
    def __init__(self, capacity=QMAX):
        self.buf = [None]*capacity
        self.cap = capacity
        self.head = 0
        self.tail = 0
        self.count = 0
        self.lock = Lock()
        self.sem_items = Semaphore(0)
        self.sem_space = Semaphore(capacity)
    def put(self, item):
        self.sem_space.acquire()
        with self.lock:
            self.buf[self.tail] = item
            self.tail = (self.tail+1) % self.cap
            self.count += 1
        self.sem_items.release()
    def get(self):
        self.sem_items.acquire()
        with self.lock:
            item = self.buf[self.head]
            self.head = (self.head+1) % self.cap
            self.count -= 1
        self.sem_space.release()
        return item

def write_pgm_p5(path, w, h, maxv, pixels_bytes):
    with open(path, "wb") as f:
        f.write(b"P5\n")
        f.write(f"{w} {h}\n".encode())
        f.write(f"{maxv}\n".encode())
        f.write(pixels_bytes)

def apply_negative_block(in_bytes, out_array, w, rs, re):
    for r in range(rs, re):
        off = r*w
        for c in range(w):
            out_array[off+c] = 255 - in_bytes[off+c]

def apply_slice_block(in_bytes, out_array, w, rs, re, t1, t2):
    for r in range(rs, re):
        off = r*w
        for c in range(w):
            val = in_bytes[off+c]
            if val <= t1 or val >= t2:
                out_array[off+c] = 255
            else:
                out_array[off+c] = val

def worker_thread_fn(tid, queue, in_bytes, out_array, w, mode, t1, t2, counter, counter_lock, per_thread_counts, verbose):
    processed = 0
    while True:
        task = queue.get()
        if task is None:
            if verbose:
                print(f"[thread-{tid}] Recebeu sentinel, saindo. Processou {processed} linhas.")
            break
        rs,re = task
        if mode=="neg":
            apply_negative_block(in_bytes,out_array,w,rs,re)
        else:
            apply_slice_block(in_bytes,out_array,w,rs,re,t1,t2)
        processed += (re - rs)
        with counter_lock:
            counter[0] -= 1
            if counter[0] == 0:
                # último sinaliza via condição externa (cond.notify_all() handled in main)
                pass
    per_thread_counts[tid] = processed

def main():
    start = time.perf_counter()
    if len(sys.argv)<5:
        print("Uso: python worker_fifo.py <fifo_path> <saida.pgm> <neg|slice> [t1 t2] [nthreads] [verbose(0|1)]")
        print("Ex: python worker_fifo.py /tmp/imgpipe out.pgm neg 4 1")
        sys.exit(1)
    fifo = sys.argv[1]
    outpath = sys.argv[2]
    mode = sys.argv[3]
    idx = 4
    if mode=="slice":
        t1=int(sys.argv[4]); t2=int(sys.argv[5]); idx=6
    else:
        t1=t2=0
    nthreads = int(sys.argv[idx]) if len(sys.argv)>idx else 4
    verbose = bool(int(sys.argv[idx+1])) if len(sys.argv) > idx+1 else True

    # garante FIFO existente (se não existir, bloqueia até sender criar)
    if verbose:
        print(f"[worker] Abrindo FIFO {fifo} para leitura (bloqueia até sender abrir escrita)...")
    # abre FIFO para leitura binária
    with open(fifo, "rb") as f:
        # ler header (12 bytes)
        hdr = f.read(12)
        if len(hdr) != 12:
            print("[worker] Erro: header incompleto recebido")
            return
        w,h,maxv = struct.unpack('<iii', hdr)
        if verbose:
            print(f"[worker] Recebido header: {w}x{h}, maxv={maxv}")
        # ler pixels
        expected = w*h
        pixels = bytearray()
        while len(pixels) < expected:
            chunk = f.read(expected - len(pixels))
            if not chunk:
                break
            pixels.extend(chunk)
    if len(pixels) != w*h:
        print(f"[worker] Aviso: pixels recebidos ({len(pixels)}) != esperado ({w*h})")
    in_bytes = bytes(pixels)
    out_array = bytearray(w*h)

    q = CircularQueue(QMAX)
    total_tasks = h  # uma tarefa por linha (pode agrupar linhas se quiser)
    counter=[total_tasks]
    counter_lock = Lock()
    cond = threading.Condition(counter_lock)

    # criamos threads
    threads=[]
    per_thread_counts = [0]*nthreads
    for i in range(nthreads):
        t=Thread(target=worker_thread_fn, args=(i,q,in_bytes,out_array,w,mode,t1,t2,counter,counter_lock,per_thread_counts,verbose))
        t.start(); threads.append(t)

    # enfileira tasks (uma linha por tarefa) — se preferir reduzir overhead, agrupe linhas por bloco.
    for r in range(h):
        q.put((r,r+1))

    # espera terminar: checamos o counter protegido por condição
    with cond:
        while counter[0] > 0:
            cond.wait(timeout=0.1)
            # a condição é notificada internamente quando chega a zero (ou timeout),
            # aqui usamos timeout para também permitir prints periódicos.
    # sinaliza fim aos threads
    for _ in range(nthreads): q.put(None)
    for t in threads: t.join()

    write_pgm_p5(outpath,w,h,maxv,bytes(out_array))
    end = time.perf_counter()

    print(f"[worker] Imagem salva em {outpath}")
    print(f"[worker] Tempo total: {end-start:.3f} s")
    # estatísticas por thread (demonstração clara de trabalho paralelo)
    for i,cnt in enumerate(per_thread_counts):
        print(f"[worker] thread-{i} processou {cnt} linhas")
    print(f"[worker] total linhas processadas: {sum(per_thread_counts)} (esperado {h})")

if __name__ == "__main__":
    main()
