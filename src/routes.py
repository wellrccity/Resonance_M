# ============================================================
# ROTAS
# ============================================================
from flask import Flask, render_template, request, jsonify
from src.generators import gerar_texto
from src.order import aplicar_ordem
from src.analyzers import analisar_palavras, calcular_score
from src.pi_loader import USAR_LIB, PI_TOTAL, PI_TAMANHO_ARQUIVO
from src.engines import motor_seed, motor_freq, motor_hib, motor_chars, motor_filtro
from src.workers import w_seed, w_freq, w_hib, w_chars, w_filtro
import threading
import os

# Pega o caminho absoluto da pasta Resonance_M (um nível acima de src)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)


@app.route('/')
def index(): return render_template('index.html')

@app.route('/update',methods=['POST'])
def update():
    d=request.json; seed=d.get('seed',''); comp=int(d.get('comprimento',1000))
    mult=int(d.get('multiplicador',0)); freq=int(d.get('frequencia',0)); ordem=d.get('ordem','0')
    raw=gerar_texto(seed,comp,mult,freq)
    exib=aplicar_ordem(raw,ordem) if ordem and ordem!='0' else raw
    pi_info=analisar_palavras(exib); sc=calcular_score(pi_info,comp,max(1,len(seed)))
    return jsonify({"resultado":exib,"resultado_raw":raw,"palavras_info":pi_info,
                    "total_palavras":len(pi_info),"score":sc,
                    "pos_primeira":pi_info[0]['posicao'] if pi_info else -1})

@app.route('/pi_info',methods=['GET'])
def pi_info():
    """Informações sobre π carregado."""
    return jsonify({
        "usando_lib": USAR_LIB,
        "total_digitos": PI_TOTAL if USAR_LIB else PI_TAMANHO_ARQUIVO,
        "fonte": "pi_lib (C/GMP)" if USAR_LIB else ("pi.txt" if PI_TAMANHO_ARQUIVO > 0 else "fallback mod10")
    })

@app.route('/start_search',methods=['POST'])
def rss():
    motor_seed.parar();motor_seed.resetar();d=request.json
    for _ in range(int(d.get('threads',2))):
        threading.Thread(target=w_seed,args=(int(d.get('comprimento',1000)),int(d.get('min_len',1)),int(d.get('max_len',32)),int(d.get('multiplicador',0)),int(d.get('frequencia',0))),daemon=True).start()
    return jsonify({"status":"started"})
@app.route('/stop_search',methods=['POST'])
def rss2(): motor_seed.parar();return jsonify({"status":"stopped"})
@app.route('/search_status',methods=['GET'])
def rss3(): e=motor_seed.obter_estado();e['melhores_seeds']=e['melhores'];return jsonify(e)

@app.route('/start_search_freq',methods=['POST'])
def rsf():
    motor_freq.parar();motor_freq.resetar();d=request.json
    for _ in range(int(d.get('threads',2))):
        threading.Thread(target=w_freq,args=(d.get('seed',''),int(d.get('comprimento',1000)),int(d.get('multiplicador',0)),int(d.get('freq_min',0)),int(d.get('freq_max',100000))),daemon=True).start()
    return jsonify({"status":"started"})
@app.route('/stop_search_freq',methods=['POST'])
def rsf2(): motor_freq.parar();return jsonify({"status":"stopped"})
@app.route('/search_status_freq',methods=['GET'])
def rsf3(): return jsonify(motor_freq.obter_estado())

@app.route('/start_search_hybrid',methods=['POST'])
def rsh():
    motor_hib.parar();motor_hib.resetar();d=request.json
    for _ in range(int(d.get('threads',2))):
        threading.Thread(target=w_hib,args=(int(d.get('comprimento',1000)),int(d.get('multiplicador',0)),int(d.get('seed_min',1)),int(d.get('seed_max',32)),int(d.get('freq_min',0)),int(d.get('freq_max',100000))),daemon=True).start()
    return jsonify({"status":"started"})
@app.route('/stop_search_hybrid',methods=['POST'])
def rsh2(): motor_hib.parar();return jsonify({"status":"stopped"})
@app.route('/search_status_hybrid',methods=['GET'])
def rsh3(): return jsonify(motor_hib.obter_estado())

@app.route('/start_search_chars',methods=['POST'])
def rsc():
    motor_chars.parar();motor_chars.resetar();d=request.json
    for _ in range(int(d.get('threads',2))):
        threading.Thread(target=w_chars,args=(d.get('texto_alvo',''),int(d.get('comprimento',1000)),int(d.get('multiplicador',0)),int(d.get('seed_min',1)),int(d.get('seed_max',32)),int(d.get('freq_min',0)),int(d.get('freq_max',100000))),daemon=True).start()
    return jsonify({"status":"started"})
@app.route('/stop_search_chars',methods=['POST'])
def rsc2(): motor_chars.parar();return jsonify({"status":"stopped"})
@app.route('/search_status_chars',methods=['GET'])
def rsc3(): return jsonify(motor_chars.obter_estado())

@app.route('/start_search_filtro',methods=['POST'])
def rsfl():
    motor_filtro.parar(); d=request.json
    cands=d.get('candidatos',[]); alvo=d.get('texto_alvo','')
    comp=int(d.get('comprimento',1000)); mult=int(d.get('multiplicador',0))
    c100=[c for c in cands if float(c.get('cobertura',0))>=99.9]
    if not c100: return jsonify({"status":"error","msg":f"Nenhum 100%. Recebidos:{len(cands)}"})
    best=c100[0]; seed=best.get('seed',''); freq=best.get('frequencia',0)
    tx=gerar_texto(seed,comp,mult,freq)
    print(f"FILTRO: seed='{seed}' freq={freq} tx={tx[:50]}...")
    motor_filtro.resetar(tx,seed,freq,alvo)
    threading.Thread(target=w_filtro,daemon=True).start()
    return jsonify({"status":"started","seed":seed,"freq":freq})
@app.route('/stop_search_filtro',methods=['POST'])
def rsfl2(): motor_filtro.parar();return jsonify({"status":"stopped"})
@app.route('/search_status_filtro',methods=['GET'])
def rsfl3(): return jsonify(motor_filtro.obter_estado())