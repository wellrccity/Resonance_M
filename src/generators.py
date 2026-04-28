# ============================================================
# FUNÇÕES BASE
# ============================================================
import random
from src.pi_loader import pi_d, PI_TOTAL, USAR_LIB, PI_TAMANHO_ARQUIVO

def seed_hash(s):
    h = 0
    for c in s: h = (h*31+ord(c)) & 0xFFFFFFFFFFFFFFFF
    return h

def mix(a, b):
    x = ((a+1)*2654435761+(b+1)*2246822519) & 0xFFFFFFFFFFFFFFFF
    x ^= x>>17; x=(x*0xbf58476d1ce4e5b9)&0xFFFFFFFFFFFFFFFF
    x ^= x>>31; x=(x*0x94d049bb133111eb)&0xFFFFFFFFFFFFFFFF
    x ^= x>>32; return x

ALFA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
SZ = len(ALFA)
FREQ_PT = {c:i for i,c in enumerate('eaosrindmutclpvgqbfhzjxkwy')}

def gerar_texto_bruto(seed_text, comp, freq=0):
    if freq==-1: return "".join(ALFA[pi_d(i)%SZ] for i in range(comp))
    if not seed_text: seed_text="a"
    sh=seed_hash(seed_text); r=[]
    pi_total = PI_TOTAL if USAR_LIB else PI_TAMANHO_ARQUIVO
    pi_mod = max(1, pi_total)
    for i in range(comp):
        pp=mix(i,sh+freq)
        dp=pi_d(pp % pi_mod)
        ch=seed_text[i%len(seed_text)]; sc=mix(ord(ch),i+sh)%SZ
        r.append(ALFA[(dp+sc)%SZ])
    return "".join(r)

def calcular_caos(mult):
    if mult>=0: return min(1.0, mult/100.0), 0.0
    else: return 0.0, min(1.0, abs(mult)/100.0)

def gerar_tamanhos_palavras(total, sv, caos, rig):
    tams=[]; usado=0; i=0; ult=0
    while usado<total:
        h=mix(i,sv)
        if caos>0.8: tam=1+(h%max(2,int(total*caos)))
        elif rig>0.5: tam=3+(h%3)
        else:
            if ult>=5: tam=2+(h%3)
            elif ult<=3 and ult>0: tam=4+(h%5)
            else: tam=2+(h%7)
        rest=total-usado
        if rest<=0: break
        tam=min(tam,rest)
        if rest-tam>0 and rest-tam<2: tam=rest
        if tam<=0: break
        tams.append(tam); ult=tam; usado+=tam; i+=1
    return tams

def filtrar_char_caos(c, pos, caos, rig, sv):
    h=mix(pos,sv); p=(h%1000)/1000.0
    if c.isdigit():
        if rig>0 and p<(0.5+rig*0.5): return 'eaosrindmutclp'[int(c)%14]
        if caos<0.5 and p<(0.8-caos*0.6): return 'eaosrindmutclp'[int(c)%14]
        return c
    if c.isupper():
        if rig>0 and p<(0.9+rig*0.1): return c.lower()
        if caos<0.3 and p<0.95: return c.lower()
        elif caos<0.7 and p<(0.7-caos*0.5): return c.lower()
        return c
    return c

def montar_silabas(chars, padrao='cv'):
    vog=[c for c in chars if c.lower() in 'aeiou']
    con=[c for c in chars if c.isalpha() and c.lower() not in 'aeiou']
    dig=[c for c in chars if c.isdigit()]
    if not vog: vog=['a']
    if not con: con=['n']
    slots=len(chars)-len(dig)
    if slots<=0: return ''.join(dig[:len(chars)])
    ix=[0,0]
    def pv(): c=vog[ix[0]%len(vog)]; ix[0]+=1; return c
    def pc(): c=con[ix[1]%len(con)]; ix[1]+=1; return c
    r=[]
    if padrao=='raw':
        for c in chars:
            if c.isalpha() and len(r)<slots: r.append(c)
    elif padrao=='vc':
        while len(r)<slots:
            r.append(pv())
            if len(r)<slots: r.append(pc())
    elif padrao=='cvc':
        while len(r)<slots:
            r.append(pc())
            if len(r)<slots: r.append(pv())
            if len(r)<slots: r.append(pc())
    elif padrao=='cvcv':
        while len(r)<slots:
            for fn in [pc,pv,pc,pv]:
                if len(r)<slots: r.append(fn())
    elif padrao=='vcv':
        while len(r)<slots:
            for fn in [pv,pc,pv]:
                if len(r)<slots: r.append(fn())
    elif padrao=='alt':
        uc=True
        while len(r)<slots: r.append(pc() if uc else pv()); uc=not uc
    else:
        while len(r)<slots:
            r.append(pc())
            if len(r)<slots: r.append(pv())
    r=r[:slots]+dig
    return ''.join(r[:len(chars)])

def aplicar_pontuacao(palavras, sv, caos, rig):
    if len(palavras)<3 or caos>0.7: return palavras
    res=[]; dv=0; dp=0
    for i,p in enumerate(palavras):
        dv+=1; dp+=1; h=mix(i,sv+777); prob=h%100
        if i==0 or (res and res[-1][-1]=='.'):
            if p and p[0].isalpha(): p=p[0].upper()+p[1:]
        res.append(p)
        lp=max(5,int(12-rig*6)); lv=max(2,int(5-rig*2))
        if dp>=lp and prob<(dp*4): res[-1]+='.'; dp=0; dv=0
        elif dv>=lv and prob<(dv*6): res[-1]+=','; dv=0
    return res

def gerar_texto(seed_text, comp, mult=0, freq=0):
    caos,rig=calcular_caos(mult)
    bruto=gerar_texto_bruto(seed_text,comp,freq)
    if caos>=1.0: return bruto
    sh=seed_hash(seed_text or 'a')+freq
    bf=''.join(filtrar_char_caos(c,i,caos,rig,sh) for i,c in enumerate(bruto))
    tams=gerar_tamanhos_palavras(comp,sh,caos,rig)
    if caos>0.7:
        palavras=[]; pos=0
        for tam in tams: palavras.append(bf[pos:pos+tam]); pos+=tam
        return ' '.join(palavras)
    palavras=[]; pos=0
    for i,tam in enumerate(tams):
        fatia=list(bf[pos:pos+tam])
        if not fatia: break
        h=mix(i,sh)
        if caos>0.4: pads=['cv','raw','alt','vc','raw','raw']
        elif rig>0.5: pads=['cv','cv','cv','cvc','cv']
        else: pads=['cv','cv','cv','cvc','cvcv','vc','alt']
        palavras.append(montar_silabas(fatia,pads[h%len(pads)]))
        pos+=tam
    if caos<0.5: palavras=aplicar_pontuacao(palavras,sh,caos,rig)
    return ' '.join(palavras)