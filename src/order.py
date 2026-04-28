# ============================================================
# ORDEM
# ============================================================
from src.generators import mix, montar_silabas, FREQ_PT

def sonoridade(c):
    cl=c.lower()
    if cl in 'aeiou': return 5
    if cl in 'lr': return 4
    if cl in 'mn': return 3
    if cl in 'fvszh': return 2
    return 1

def filtrar_chars_ordem(todos, qtd, fv):
    if not todos or qtd<=0: return []
    scored=[]
    for i,c in enumerate(todos):
        sc=0.0; cl=c.lower()
        if cl in 'aeiou': sc=100.0+{'a':10,'e':9,'o':8,'i':7,'u':6}.get(cl,5)
        elif cl in 'rstlnm': sc=80.0
        elif cl in 'dcpbvf': sc=70.0
        elif c.isalpha(): sc=50.0
        elif c.isdigit(): sc=5.0
        else: sc=1.0
        if fv>0: h=mix(i,fv); sc*=((h%1000)/1000.0)*0.6+0.7
        scored.append((sc,i,c))
    scored.sort(key=lambda x:-x[0])
    sel=[]; us=set()
    mv=max(1,int(qtd*0.4)); mc=max(1,int(qtd*0.3)); vs=0; cs=0
    for sc,i,c in scored:
        if vs>=mv: break
        if c.lower() in 'aeiou': sel.append((i,c)); us.add(i); vs+=1
    for sc,i,c in scored:
        if cs>=mc: break
        if i not in us and c.isalpha() and c.lower() not in 'aeiou':
            sel.append((i,c)); us.add(i); cs+=1
    for sc,i,c in scored:
        if len(sel)>=qtd: break
        if i not in us: sel.append((i,c)); us.add(i)
    sel.sort(key=lambda x:x[0])
    return [c for i,c in sel]

def selecionar_chars(chars, regra):
    if not chars or regra=='0': return list(chars)
    if regra=='1': return sorted(chars, key=lambda c:c.lower())
    if regra=='2': return sorted(chars, key=lambda c:c.lower(), reverse=True)
    if regra=='3': return [c for c in chars if c.lower() in 'aeiou']+[c for c in chars if c.lower() not in 'aeiou']
    if regra=='4': return [c for c in chars if c.isalpha() and c.lower() not in 'aeiou']+[c for c in chars if not(c.isalpha() and c.lower() not in 'aeiou')]
    if regra=='5': return sorted(chars, key=lambda c:FREQ_PT.get(c.lower(),99))
    if regra=='6': return sorted(chars, key=lambda c:FREQ_PT.get(c.lower(),99), reverse=True)
    if regra=='7': return sorted(chars, key=lambda c:sonoridade(c))
    if regra=='8': return sorted(chars, key=lambda c:sonoridade(c), reverse=True)
    return list(chars)

PADROES={'0':'raw','1':'cv','2':'cvc','3':'vc','4':'vcv','5':'cvcv',
         '6':'alt','7':'cv','8':'alt','9':'cv','a':'cv','b':'cv',
         'c':'cv','d':'cv','e':'cv','f':'cv'}

def decodificar_filtro(s):
    v=0
    for c in s:
        if c.isdigit(): v=v*36+int(c)
        elif 'a'<=c<='z': v=v*36+ord(c)-ord('a')+10
        elif 'A'<=c<='Z': v=v*36+ord(c)-ord('A')+10
    return v

def codificar_filtro(val):
    if val==0: return '0'
    ch=[]
    while val>0: r=val%36; ch.append(str(r) if r<10 else chr(ord('a')+r-10)); val//=36
    return ''.join(reversed(ch))

def aplicar_ordem(texto, ordem_str):
    if not ordem_str or ordem_str=='0': return texto
    ordem_str=str(ordem_str)
    if '-' in ordem_str:
        partes=ordem_str.split('-')
        est=partes[0]; regras=partes[1] if len(partes)>1 else '00'
        fs=partes[2] if len(partes)>2 else '0'
        tams=[]
        for c in est:
            if c.isdigit(): tams.append(int(c))
            elif 'a'<=c<='z': tams.append(ord(c)-ord('a')+10)
        if not tams: return texto
        r1=regras[0] if len(regras)>0 else '0'
        r2=regras[1] if len(regras)>1 else '0'
        fv=decodificar_filtro(fs)
        todos=[c for c in texto if c not in ' .,!?;:']
        total=sum(tams)
        cd=filtrar_chars_ordem(todos,total,fv)
        sel=selecionar_chars(cd,r1)
        pad=PADROES.get(r2,'cv')
        palavras=[]; pos=0
        for tam in tams:
            fatia=sel[pos:pos+tam]
            while len(fatia)<tam: fatia.append('a')
            montado=montar_silabas(fatia,pad)
            rc=list(montado)
            if r2=='d' and rc: rc=[rc[0].upper()]+[c.lower() for c in rc[1:]]
            elif r2=='e': rc=[c.upper() for c in rc]
            elif r2=='f': rc=[c.lower() for c in rc]
            palavras.append(''.join(rc))
            pos+=tam
        return ' '.join(palavras)
    try: n=int(ordem_str)
    except ValueError: return texto
    if n<=0: return texto
    chars=list(texto); ln=len(chars)
    if ln<=1: return texto
    for k in range(n):
        h1=mix(k,n); h2=mix(k+n,k*7+3); i=h1%ln; j=h2%ln
        if i==j: j=(j+1)%ln
        chars[i],chars[j]=chars[j],chars[i]
    return ''.join(chars)