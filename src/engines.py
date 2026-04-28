# ============================================================
# MOTORES
# ============================================================
import threading
import math

class MotorBusca:
    def __init__(self):
        self.lock=threading.Lock(); self.ativo=False
        self.melhores=[]; self.testadas=0; self.melhor_score_global=0.0
    def resetar(self):
        with self.lock: self.melhores=[]; self.testadas=0; self.melhor_score_global=0.0; self.ativo=True
    def parar(self): self.ativo=False
    def atualizar_resultado(self,e):
        mel=False; sc=e.get('score',0); pp=e.get('pos_primeira',999999)
        with self.lock:
            self.testadas+=1
            if len(self.melhores)<10:
                self.melhores.append(e); self._r(); mel=True
            else:
                p=self.melhores[-1]
                if sc>p['score'] or (sc==p['score'] and pp<p.get('pos_primeira',999999)):
                    self.melhores.append(e); self._r(); self.melhores=self.melhores[:10]; mel=True
            if sc>self.melhor_score_global: self.melhor_score_global=sc
        return mel
    def _r(self): self.melhores.sort(key=lambda x:(-x['score'],x.get('pos_primeira',999999)))
    def obter_estado(self):
        with self.lock:
            return {"busca_ativa":self.ativo,"melhores":[self._l(m) for m in self.melhores],
                    "testadas":self.testadas,"melhor_score":self.melhor_score_global}
    def _l(self,m):
        l={}
        for k,v in m.items():
            if isinstance(v,float) and (math.isinf(v) or math.isnan(v)): l[k]=999999
            else: l[k]=v
        return l

class MotorFiltro:
    def __init__(self):
        self.lock=threading.Lock(); self.ativo=False
        self.texto_gerado=""; self.seed_usado=""; self.freq_usado=0
        self.texto_alvo=""; self.resultados=[]; self.matches=[]
        self.filtro_atual=0; self.filtros_testados=0; self.melhor_sim=0; self.log=[]
    def resetar(self,tg,seed,freq,alvo):
        with self.lock:
            self.texto_gerado=tg; self.seed_usado=seed; self.freq_usado=freq
            self.texto_alvo=alvo; self.resultados=[]; self.matches=[]
            self.filtro_atual=0; self.filtros_testados=0; self.melhor_sim=0; self.log=[]; self.ativo=True
    def parar(self): self.ativo=False
    def add_log(self,msg):
        with self.lock:
            self.log.append(msg)
            if len(self.log)>100: self.log=self.log[-100:]
    def obter_estado(self):
        with self.lock:
            return {"busca_ativa":self.ativo,"seed":self.seed_usado,"freq":self.freq_usado,
                    "matches":list(self.matches),"resultados":list(self.resultados[:10]),
                    "filtro_atual":self.filtro_atual,"filtros_testados":self.filtros_testados,
                    "melhor_sim":self.melhor_sim,"log":list(self.log[-30:]),"texto_alvo":self.texto_alvo}

motor_seed=MotorBusca(); motor_freq=MotorBusca()
motor_hib=MotorBusca(); motor_chars=MotorBusca()
motor_filtro=MotorFiltro()

R1="0123456789abcdef"
R2="0123456789abcdef"