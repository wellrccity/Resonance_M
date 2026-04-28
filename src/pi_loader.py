# ============================================================
# CARREGAR PI VIA BIBLIOTECA C
# ============================================================
import ctypes
import os
import sys
import time

PI_LIB = None
PI_TOTAL = 0

def carregar_pi_lib():
    global PI_LIB, PI_TOTAL
    
    if sys.platform == 'win32':
        lib_name = 'pi_lib.dll'
    elif sys.platform == 'darwin':
        lib_name = 'pi_lib.dylib'
    else:
        lib_name = 'pi_lib.so'
    
    lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), lib_name)
    
    if not os.path.exists(lib_path):
        print(f"AVISO: {lib_name} nao encontrado")
        print(f"Compilar: gcc -O2 -shared -o {lib_name} pi_lib.c")
        return False
    
    try:
        if sys.platform == 'win32':
            PI_LIB = ctypes.CDLL(lib_path, winmode=0)
        else:
            PI_LIB = ctypes.CDLL(lib_path)
        
        PI_LIB.pi_calcular.argtypes = [ctypes.c_long]
        PI_LIB.pi_calcular.restype = ctypes.c_int
        PI_LIB.pi_digito.argtypes = [ctypes.c_long]
        PI_LIB.pi_digito.restype = ctypes.c_int
        PI_LIB.pi_total.argtypes = []
        PI_LIB.pi_total.restype = ctypes.c_long
        PI_LIB.pi_liberar.argtypes = []
        PI_LIB.pi_liberar.restype = None
        
        n = 10_000  # 10K
        print(f"Calculando {n:,} digitos de pi (C)...")
        t0 = time.time()
        PI_LIB.pi_calcular(n)
        PI_TOTAL = PI_LIB.pi_total()
        primeiros = ''.join(str(PI_LIB.pi_digito(i)) for i in range(50))
        print(f"pi: {primeiros}")
        print(f"ok: 31415926535897932384626433832795028841971693993751")
        print(f"pi: {PI_TOTAL:,} digitos em {time.time()-t0:.1f}s")
        return True
    except Exception as e:
        print(f"ERRO: {e}")
        return False

# fallback: carregar de arquivo
PI_DADOS_ARQUIVO = ""
PI_TAMANHO_ARQUIVO = 0

def carregar_pi_arquivo():
    global PI_DADOS_ARQUIVO, PI_TAMANHO_ARQUIVO
    try:
        with open('pi.txt', 'r') as f:
            raw = f.read().replace('\n','').replace('\r','').replace(' ','').replace('.','')
        if not raw.startswith('3'): raw = '3' + raw
        PI_DADOS_ARQUIVO = raw
        PI_TAMANHO_ARQUIVO = len(raw)
        print(f"pi.txt: {PI_TAMANHO_ARQUIVO:,} digitos")
        return True
    except FileNotFoundError:
        print("pi.txt nao encontrado")
        return False

# tentar carregar pi_lib, senão usa arquivo
USAR_LIB = carregar_pi_lib()
if not USAR_LIB:
    USAR_LIB_ARQUIVO = carregar_pi_arquivo()
    if not USAR_LIB_ARQUIVO:
        print("AVISO: sem fonte de pi! Usando mod 10 como fallback.")

def pi_d(pos):
    """Retorna o dígito de π na posição pos."""
    if USAR_LIB and PI_LIB:
        return PI_LIB.pi_digito(pos % PI_TOTAL if PI_TOTAL > 0 else 0)
    elif PI_TAMANHO_ARQUIVO > 0:
        return int(PI_DADOS_ARQUIVO[pos % PI_TAMANHO_ARQUIVO])
    else:
        return pos % 10