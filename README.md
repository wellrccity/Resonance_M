# Resonance M — Gerador Determinístico π

Um sistema de "geração" e busca de texto determinístico baseado nos dígitos de π (pi), que implementa uma versão computacional da Biblioteca de Babel de Jorge Luis Borges com regras linguísticas de idiomas latinos.

## O que é

Dado um conjunto de parâmetros — **seed**, **frequência**, **caos** e **ordem** — o sistema gera sempre o mesmo texto pronunciável. Isso significa que qualquer texto possível tem um "endereço" único nesse espaço paramétrico.

O sistema não armazena textos. Ele os **calcula** deterministicamente a partir de π.

## Como funciona

```
Seed + Frequência → mix com π → chars brutos (base62)
                                      ↓
                              Caos (controle de restrição)
							  ↓ ajusta distribuição de caracteres
							  ↓ relaxa/impõe padrões fonéticos
                              ↓ aplica padrões silábicos (CV, CVC, VCV...)
                              ↓ gera tamanhos de palavras (ritmo latino)
                              ↓ insere pontuação
                                      ↓
                              Texto pronunciável
                                      ↓
                              Ordem (EE-RR-FF)
                              ↓ reseleciona chars
                              ↓ remonta sílabas com regras diferentes
                              ↓ aplica filtro de preferência
                                      ↓
                              Texto final
```

### Indexação do Espaço 

Este sistema não é apenas um gerador de texto.

Ele define uma função determinística:

f(seed, frequência, caos, ordem, N) → texto

Isso transforma o espaço de todos os textos possíveis em um espaço indexável.

Cada combinação de parâmetros é uma coordenada.

Ou seja:

- não há armazenamento
- não há busca linear
- há acesso direto

O texto não é encontrado.

Ele é calculado.

### Parâmetros

| Parâmetro | Tipo | Função |
|-----------|------|--------|
| **Seed** | texto livre | Chave primária de geração |
| **Frequência** | inteiro | Deslocamento no espaço de π |
| **Caos** | -100 a 100 | -100=rigidez máxima, 0=normal, 100=caos total |
| **Comprimento** | inteiro | Quantidade de caracteres gerados |
| **Ordem** | código | Reorganização estrutural (ex: `35-51-a`) |

### Formato da Ordem: `EE-RR-FF`

```
EE = Estrutura (tamanhos das palavras)
     1-9: direto, a-z: 10-35
     Ex: "35" = palavra de 3 + palavra de 5

RR = Regras (2 chars)
     1º char: seleção de caracteres
       0=original 1=alfa 2=alfa↓ 3=vogais1º 4=cons1º
       5=freqPT 6=freqPT↓ 7=sonoridade↑ 8=sonoridade↓
     2º char: padrão silábico
       0=raw 1=CV 2=CVC 3=VC 4=VCV 5=CVCV
       d=Title e=UPPER f=lower

FF = Filtro (base36)
     Muda quais chars são preferidos na seleção
     Cada valor gera combinação diferente
```

### Controle de Caos (Multiplicador)

```
-100 ←————————————— 0 ——————————————→ 100
 Rigidez máxima    Normal           Caos total
 
 Só minúsculas     Padrão latino    Texto bruto
 Sem dígitos       Com pontuação    Sem regras
 CV perfeito       Ritmo natural    Sem espaços
 Frases curtas     Alternância      Aleatório
```

## Funcionalidades

### Gerador Principal
- Gera texto pronunciável em tempo real
- Regras fonéticas de idiomas latinos integradas
- Padrões silábicos: CV, CVC, VCV, CVCV
- Pontuação automática (vírgulas, pontos)
- Capitalização contextual (após pontos)
- Alternância de tamanho de palavras (ritmo)

### Buscadores

#### 🟢 Busca por Caracteres
Encontra seeds cujo texto gerado contenha os caracteres de um texto alvo. Para resultados com 100% de cobertura, testa automaticamente 256 combinações de regras de ordem e mostra a similaridade com o alvo.

#### 🔄 Busca por Filtro
Pega o melhor candidato com 100% de cobertura e percorre o terceiro parâmetro da ordem (filtro) com todas as combinações de regras, buscando match exato com o texto alvo.

#### 🔶 Busca por Frequência
Fixa a seed e varia a frequência para encontrar palavras do arquivo de referência.

#### 🟣 Busca Híbrida
Varia seed e frequência simultaneamente.

#### 🔵 Busca por Seed
Fixa a frequência e varia a seed.

### Sistema de Score

```
Cobertura < 90%:  score = cobertura×80 + proximidade×20
Cobertura ≥ 90%:  score = cobertura×50 + proximidade×20 + ordem×30
Cobertura = 100%: score = 1000 + similaridade×5 + bônus

Bônus seed pequena: 2.0 / (1 + (tamanho-1) × 0.1)
```

Resultados com 100% de cobertura **sempre** ficam acima de qualquer resultado com menos de 100%.

## Regras Linguísticas Implementadas

### Fonética
- Classificação: vogais (aeiou), consoantes, dígitos
- Sonoridade: plosivas(1) → fricativas(2) → nasais(3) → líquidas(4) → vogais(5)
- Ponto de articulação: labiais → dentais → velares → vogais
- Harmonia vocálica: agrupamento a,e / i / o,u

### Estrutura
- Taxa de vogais ~40-50%
- Tamanho médio de palavras: 2-8 chars
- Alternância longa-curta (ritmo)
- Padrão silábico dominante: CV

### Pontuação
- Vírgula a cada 3-7 palavras
- Ponto a cada 8-20 palavras
- Maiúscula após ponto e no início

### Caos
- Dígitos filtrados proporcionalmente
- Maiúsculas controladas
- Padrões silábicos relaxados progressivamente
- Espaços reduzidos com caos alto

## Instalação

### Requisitos
- Python 3.8+
- Flask
- Compilador C(opcional)

### Setup

```bash
pip install flask
```

### Arquivos necessários

```
projeto/
├── src/
│   ├── analyzers.py
│    ├── pi.txt              # dígitos de π (quanto mais, melhor, ou compile o pi_lib.c)
│   ├── generators.py
│   ├── engines.py
│   ├── order.py
│   ├── pi_lib.c
│   ├── pi_loader.py
│   ├── routes.py
│   ├── word_loader.py
│   └── workers.py
├── templates/
│   └── index.html      # interface
├── app.py              # servidor
├── palavras.txt         # palavras de referência (opcional, testes)
└── pi_lib.c             # biblioteca para calcular pi em tempo real

```

### Obter dígitos de π

pi_lib.c gera os digitos na hora
Compile com: gcc -O2 -shared -o pi_lib.dll pi_lib.c 

Arquivo `pi.txt` como fallback caso não queira usar a biblioteca em c, o arquivo deve conter dígitos de π sem formatação:
```
31415926535897932384626433832795028841971...
```

### Executar

```bash
python app.py
```

Acesse `http://127.0.0.1:5000`

## Exemplos

### Texto com caos 0 (normal)
```
Seed: teste
Freq: 0
Caos: 0

→ "Jafpa ra nafa duvazuma ya yochuwzo yana..."
```

### Texto com caos -100 (rígido)
```
Seed: teste
Freq: 0
Caos: -100

→ "Jaf maw lanaf, dava nuc yay yocoh zur..."
```

### Texto com caos 100 (caos total)
```
Seed: teste
Freq: 0
Caos: 100

→ "jFP8WrLNFjvdvZ8nUc1aYyCHwouzRynpjVfKxDM82Hz9HVH..."
```

### Aplicando ordem (O comprimento também influencia nesse caso)
```
Seed: teste
Freq: 0
Caos: 0
Ordem: 35-1d
Comprimento: 1000

→ "Nan Naran"  (3+5 chars, CV, Title case)

Caos: 100
→ "Nan Laral"

Caos: -100
→ "Nan Lamal"

```

## Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────→│  Flask API   │────→│  Gerador π  │
│  (HTML/JS)  │←────│  (rotas)     │←────│  (funções)  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  Workers    │
                    │  (threads)  │
                    └─────────────┘
                    │ seed │ freq │
                    │ hib  │ chars│
                    │ filtro      │
                    └─────────────┘
```

### Determinismo

A mesma combinação de parâmetros **sempre** gera o mesmo texto:

```python
gerar_texto("abc", 100, 0, 42)  # sempre igual
gerar_texto("abc", 100, 0, 42)  # idêntico
```

Isso é garantido porque:
1. `seed_hash()` é determinístico
2. `mix()` é determinístico (Murmur-like)
3. π é constante
4. Regras linguísticas são determinísticas

## Base Matemática

### Geração de caracteres

```
Para cada posição i:
  pos_pi = mix(i, seed_hash + frequência)
  dígito = π[pos_pi mod |π|]
  contribuição = mix(seed[i mod |seed|], i + seed_hash) mod 62
  char = ALFA[(dígito + contribuição) mod 62]
```

### Funções de mistura

```
mix(a, b):
  x = (a+1)×2654435761 + (b+1)×2246822519
  x ^= x >> 17
  x *= 0xbf58476d1ce4e5b9
  x ^= x >> 31
  x *= 0x94d049bb133111eb
  x ^= x >> 32
```
🥴

Baseado em finalizers de Murmur3/SplitMix64.

### Espaço total

Com base62, comprimento N, e frequência discreta F:

Textos possíveis ≈ 62^N × |F|

Para N=1000, F=100000:

≈ 10^(1792 + 9.3)
≈ 10^1801 😵

F ∈ ℤ

Cada valor de F gera uma projeção pseudo-independente do espaço,
devido ao uso de funções de mistura com propriedade de avalanche.

Na prática, isso transforma o sistema em um espaço paramétrico indexável,
não apenas combinatório.


---

### Densidade de Informação (Filtro de Caos)

Na Biblioteca de Borges, a esmagadora maioria dos textos é ruído puro.

Este sistema não gera o espaço completo para depois filtrar.
Ele constrói diretamente sequências dentro de um subespaço linguístico,
utilizando restrições fonéticas durante a geração (CV, padrões silábicos, etc).

Ou seja:
- não existe "lixo descartado"
- o lixo simplesmente nunca é gerado

O parâmetro de caos define um contínuo:

- Caos = 0 → máxima estrutura (texto pronunciável)
- Caos = 100 → espaço completo (base62 bruto)

Isso garante:

> Cobertura total do espaço no limite superior


---

### Expansão Arbitrária (N dinâmico)

Diferente da Biblioteca de Babel, que possui tamanho fixo,
o comprimento N aqui é uma variável livre.

Para N ≈ 1.025.000:

62^N ≈ 10^1.837.200

Biblioteca de Babel:
≈ 10^1.834.000

✔️ Ultrapassa

E continua crescendo indefinidamente


---

### Paradigma Computacional

Borges:
- espaço fixo
- não computável na prática
- precisa "existir"

Resonance:
- espaço paramétrico
- determinístico
- computável sob demanda

Cada texto é acessado por índice, não armazenado.


---

### Comparação de "Poder de Fogo" 

| Recurso               | Borges (Babel)                     | Resonance  |
|----------------------|----------------------------------|-------------|
| Alfabeto             | 25 caracteres                    | 62 caracteres + regras |
| Tamanho do Texto     | Fixo (~1.3M chars)               | Dinâmico (N arbitrário)  |
| Espaço Total         | ~10^1.834.000                    | ~62^N × 2×10^9 → ex: N=1000 ≈ 10^1801  |
| Fonte                | Abstração matemática             | π + hash determinístico |
| Geração              | Implícita                        | Computável sob demanda  |
| Navegação            | Espaço físico (salas)            | Indexação direta  |
| Estrutura            | Caos puro                        | Gradiente (Caos ↔ Ordem) |
| Densidade Linguística| ~0% útil                         | Ajustável (0% → 100%)  |
| Cobertura            | Total (fixa)                     | Total (paramétrica)  |
| Acesso               | Inviável                         | O(1) por coordenada  |
| Armazenamento        | Necessário (teórico)             | Zero  |
---

### Diferença Fundamental 

Borges descreve uma biblioteca que precisa existir fisicamente.

Este sistema descreve uma biblioteca que existe matematicamente —
e pode ser acessada diretamente por coordenadas.

Não é exploração de um espaço.

É acesso determinístico a ele.

## Licença

MIT

## Inspiração

- **Andrey Markov** — pela inspiração nas cadeias de Markov aplicadas ao ritmo e às transições do texto.
- **Biblioteca de Babel** — Jorge Luis Borges (1941)
- **Library of Babel** — Jonathan Basile (libraryofbabel.info)
- **π** — a constante matemática como fonte de pseudo-aleatoriedade