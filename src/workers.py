# ============================================================
# WORKERS
# ============================================================
import random
import time
import traceback
from src.generators import gerar_texto, ALFA
from src.analyzers import avaliar, avaliar_caracteres, analisar_caracteres, calcular_score_caracteres
from src.order import aplicar_ordem, codificar_filtro
from src.engines import motor_seed, motor_freq, motor_hib, motor_chars, motor_filtro, R1, R2

def w_seed(comp,mn,mx,mult,ff):
    m=motor_seed
    while m.ativo:
        t=random.randint(mn,mx); s=''.join(random.choices(ALFA,k=t))
        sc,info,tx=avaliar(s,ff,comp,mult); pp=info[0]['posicao'] if info else 999999
        m.atualizar_resultado({'seed':s,'frequencia':ff,'score':sc,'qtd_palavras':len(info),
            'pos_primeira':pp,'palavras_info':info,'texto':tx,'tamanho_seed':len(s)})

def w_freq(sf,comp,mult,fmin,fmax):
    m=motor_freq
    while m.ativo:
        f=random.randint(fmin,fmax); sc,info,tx=avaliar(sf,f,comp,mult)
        pp=info[0]['posicao'] if info else 999999
        m.atualizar_resultado({'seed':sf,'frequencia':f,'score':sc,'qtd_palavras':len(info),
            'pos_primeira':pp,'palavras_info':info,'texto':tx,'tamanho_seed':len(sf)})

def w_hib(comp,mult,smin,smax,fmin,fmax):
    m=motor_hib
    while m.ativo:
        t=random.randint(smin,smax); s=''.join(random.choices(ALFA,k=t))
        f=random.randint(fmin,fmax); sc,info,tx=avaliar(s,f,comp,mult)
        pp=info[0]['posicao'] if info else 999999
        m.atualizar_resultado({'seed':s,'frequencia':f,'score':sc,'qtd_palavras':len(info),
            'pos_primeira':pp,'palavras_info':info,'texto':tx,'tamanho_seed':len(s)})

def w_chars(ta,comp,mult,smin,smax,fmin,fmax):
    m=motor_chars
    palavras_alvo=[p for p in ta.split(' ') if p]
    tamanhos=[len(p) for p in palavras_alvo]
    est=''
    for t in tamanhos:
        if 1<=t<=9: est+=str(t)
        elif 10<=t<=35: est+=chr(ord('a')+t-10)
        else: est+='z'
    while m.ativo:
        t=random.randint(smin,smax); s=''.join(random.choices(ALFA,k=t))
        f=random.randint(fmin,fmax)
        tx=gerar_texto(s,comp,mult,f); enc=analisar_caracteres(tx,ta)
        ach=[e for e in enc if e['encontrado']]
        pp=ach[0]['pos_gerado'] if ach else 999999
        cob_raw=len(ach)/max(1,sum(1 for c in ta if c!=' '))
        mc=''; mr=''; mm=False; ms=-1
        if cob_raw>=0.999:
            al=ta.lower()
            for r1c in R1:
                if mm: break
                for r2c in R2:
                    code=f"{est}-{r1c}{r2c}"
                    try: res=aplicar_ordem(tx,code)
                    except: continue
                    if res==ta: mc=code; mr=res; mm=True; break
                    rl=res.lower().replace(' ',''); al_l=al.replace(' ','')
                    if len(rl)==len(al_l):
                        sim=sum(1 for a,b in zip(rl,al_l) if a==b)
                        if sim>ms: ms=sim; mc=code; mr=res
                        if rl==al_l: mm=True
        sim_pct=round((ms/max(1,len(ta.replace(' ',''))))*100,1) if ms>0 else 0
        sc,cob,ord_=analyzers.calcular_score_caracteres(enc,ta,comp,len(s),sim_pct)
        m.atualizar_resultado({
            'seed':s,'frequencia':f,'score':sc,'encontrados':enc,
            'total_encontrados':len(ach),'total_alvo':len(ta),
            'cobertura':cob,'ordem':ord_,'texto':tx,'texto_alvo':ta,
            'tamanho_seed':len(s),'pos_primeira':pp,
            'ordem_code':mc,'ordem_result':mr,'ordem_match':mm,'similaridade':sim_pct
        })

def w_filtro():
    mf=motor_filtro
    print(">>> WORKER FILTRO INICIOU")
    try:
        with mf.lock:
            tx=str(mf.texto_gerado); seed=str(mf.seed_usado)
            freq=int(mf.freq_usado); alvo=str(mf.texto_alvo)
        if not tx or not alvo:
            mf.add_log("ERRO: vazio"); mf.ativo=False; return
        palavras_alvo=[p for p in alvo.split(' ') if p]
        tamanhos=[len(p) for p in palavras_alvo]
        est=''
        for t in tamanhos:
            if 1<=t<=9: est+=str(t)
            elif 10<=t<=35: est+=chr(ord('a')+t-10)
            else: est+='z'
        al_limpo=alvo.lower().replace(' ',''); tc=len(al_limpo)
        mf.add_log(f"Seed='{seed}' freq={freq} est={est}")
        mf.add_log(f"Alvo: '{alvo}' ({tc} chars)")
        local_testados=0; local_melhor=0; local_res=[]; local_matches=[]; local_logs=[]
        fv=0
        while mf.ativo:
            for r1c in R1:
                if not mf.ativo: break
                for r2c in R2:
                    if not mf.ativo: break
                    fs=order.codificar_filtro(fv); code=f"{est}-{r1c}{r2c}-{fs}"
                    try: res=aplicar_ordem(tx,code)
                    except: continue
                    local_testados+=1
                    rl=res.lower().replace(' ','')
                    if len(rl)==tc and tc>0:
                        sim=sum(1 for a,b in zip(rl,al_limpo) if a==b)
                        sp=round((sim/tc)*100,1)
                        if sp>local_melhor:
                            local_melhor=sp; local_logs.append(f"Sim {sp}% f={fs} r={r1c}{r2c} -> '{res}'")
                            print(f">>> MELHOR: {sp}% {code} -> '{res}'")
                        if res==alvo:
                            local_matches.append({'seed':seed,'frequencia':freq,'ordem_code':code,'resultado':res,'tamanho_seed':len(seed)})
                            local_logs.append(f"*** MATCH *** {code}"); print(f">>> MATCH: {code}")
                        if sp>20:
                            local_res.append({'seed':seed,'frequencia':freq,'ordem_code':code,'resultado':res,'similaridade':sp,'match':res==alvo,'tamanho_seed':len(seed)})
                            local_res.sort(key=lambda x:-x['similaridade'])
                            if len(local_res)>10: local_res=local_res[:10]
            with mf.lock:
                mf.filtro_atual=fv; mf.filtros_testados=local_testados; mf.melhor_sim=local_melhor
                mf.resultados=list(local_res); mf.matches=list(local_matches)
                for lg in local_logs: mf.log.append(lg)
                if len(mf.log)>100: mf.log=mf.log[-100:]
                local_logs=[]
            if fv%10==0: print(f">>> Filtro {fv} | {local_testados} | melhor={local_melhor}%")
            fv+=1
            if fv>999999: break
            time.sleep(0.005)
        with mf.lock: mf.log.append(f"Fim. Total: {local_testados}")
    except Exception as e:
        print(f">>> ERRO: {traceback.format_exc()}"); mf.add_log(f"ERRO: {e}")
    finally:
        mf.ativo=False; print(">>> WORKER FILTRO FIM")