import sys
import struct
import os

def read_pgm_p5(path):
    with open(path, "rb") as f:
        magic = f.readline().strip()
        if magic != b'P5':
            raise ValueError("Somente PGM P5 (binário) suportado")
        def read_non_comment():
            line = f.readline()
            while line.startswith(b'#'):
                line = f.readline()
            return line
        dims = b""
        while True:
            line = read_non_comment()
            dims += line
            if len(dims.split()) >= 2:
                break
        parts = dims.split()
        w = int(parts[0]); h = int(parts[1])
        maxv_line = read_non_comment()
        maxv = int(maxv_line.split()[0])
        pixels = f.read(w*h)
        if len(pixels) != w*h:
            raise ValueError("Arquivo PGM truncado")
        return w, h, maxv, pixels

def main():
    if len(sys.argv) != 4:
        print("Uso: python sender_fifo.py <fifo_path> <entrada.pgm> <verbose(0|1)>")
        print("Ex: python sender_fifo.py /tmp/imgpipe input.pgm 1")
        sys.exit(1)

    fifo = sys.argv[1]
    inpath = sys.argv[2]
    verbose = bool(int(sys.argv[3]))

    # cria FIFO se não existir
    try:
        if not os.path.exists(fifo):
            os.mkfifo(fifo)
            if verbose: print(f"[sender] FIFO criado em {fifo}")
    except FileExistsError:
        pass

    w,h,maxv,pixels = read_pgm_p5(inpath)
    header = struct.pack('<iii', w, h, maxv)

    if verbose:
        print(f"[sender] Abrindo FIFO {fifo} para escrita (vai bloquear até worker abrir leitura)...")
    # abre FIFO em modo binário (bloqueia até reader abrir)
    with open(fifo, "wb") as f:
        # envia header + pixels
        f.write(header)
        f.flush()
        f.write(pixels)
        f.flush()
    if verbose:
        print(f"[sender] Enviado {w}x{h} pixels via FIFO {fifo}")

if __name__ == "__main__":
    main()
