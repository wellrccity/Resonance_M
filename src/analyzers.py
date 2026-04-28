# ============================================================
# ANÁLISE
# ============================================================
import math
from src.word_loader import PALAVRAS
from src.generators import gerar_texto

def analisar_palavras(texto):
    tl=texto.lower(); enc=[]
    for p in PALAVRAS:
        pos=tl.find(p)
        if pos!=-1: enc.append({'palavra':p,'posicao':pos,'tamanho':len(p)})
    enc.sort(key=lambda x:x['posicao']); return enc

def calcular_score(pi_info,ct,ts=1):
    if not pi_info: return 0.0
    s=0.0; f=max(1,ct*0.1)
    for i in pi_info: s+=(i['tamanho']**1.5)*math.exp(-i['posicao']/f)
    s+=len(pi_info)*0.5; s*=2.0/(1.0+(ts-1)*0.1); return round(s,4)

def analisar_caracteres(tg,ta):
    if not ta or not tg: return []
    al=ta.lower(); gl=tg.lower(); usado=set(); enc=[]
    for pa,ca in enumerate(al):
        if ca==' ': continue
        ok=False
        for pg in range(len(gl)):
            if pg not in usado and gl[pg]==ca:
                usado.add(pg); ok=True
                enc.append({'char':ca,'char_real':ca,'pos_gerado':pg,'pos_alvo':pa,'encontrado':True}); break
        if not ok:
            enc.append({'char':ca,'char_real':ca,'pos_gerado':-1,'pos_alvo':pa,'encontrado':False})
    return enc

def calcular_score_caracteres(enc,ta,cg,ts,similaridade=0):
    if not enc or not ta: return 0.0,0.0,0.0
    total=sum(1 for c in ta if c!=' ')
    ach=[e for e in enc if e['encontrado']]; n=len(ach)
    if n==0 or total==0: return 0.0,0.0,0.0
    cob=n/total; f=max(1,cg*0.1)
    prox=sum(math.exp(-e['pos_gerado']/f) for e in ach)/n
    if n>=2:
        po=sum(1 for i in range(n-1) if ach[i]['pos_gerado']<ach[i+1]['pos_gerado'])
        orr=po/(n-1)
    else: orr=1.0
    of=orr*cob; bs=2.0/(1.0+(ts-1)*0.1)
    if cob>=1.0: sc=1000+(similaridade*5)+(prox*20+of*30)*bs
    elif cob>=0.9: sc=(cob*50+prox*20+of*30)*bs
    else: sc=(cob*80+prox*20)*bs
    return round(sc,4),round(cob*100,1),round(of*100,1)

def avaliar(seed,freq,comp,mult):
    tx=gerar_texto(seed,comp,mult,freq); pi_info=analisar_palavras(tx)
    return calcular_score(pi_info,comp,len(seed)),pi_info,tx

def avaliar_caracteres(seed,freq,comp,mult,ta):
    tx=gerar_texto(seed,comp,mult,freq); enc=analisar_caracteres(tx,ta)
    sc,cob,ord_=calcular_score_caracteres(enc,ta,comp,len(seed))
    return sc,cob,ord_,enc,tx