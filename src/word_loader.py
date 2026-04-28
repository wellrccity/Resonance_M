# ============================================================
# CARREGAR PALAVRAS
# ============================================================
import re

def carregar_palavras(caminho):
    palavras = set()
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            for token in re.split(r'\s+', f.read()):
                t = token.strip().lower()
                if t: palavras.add(t)
    except FileNotFoundError: pass
    return palavras

PALAVRAS = carregar_palavras('palavras.txt')
print(f"Palavras: {len(PALAVRAS)}")