"""Etapa 2 - Limpeza, identificação de paradas (nós) e construção da rede (v1).
Entrada : data/paradas_raw.csv
Saídas  : data/itinerarios_limpo.csv, data/paradas.csv, data/arestas.csv,
          data/incidencia_linha_parada.csv, data/auditoria_nomes.csv, rede_v1.graphml
"""
import re, unicodedata
import pandas as pd, networkx as nx

raw = pd.read_csv("data/paradas_raw.csv", dtype={"linha": str})

def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

# ---------- 1. nome limpo ----------
def limpar_nome(s):
    s = sem_acento(s.upper()).strip()
    s = re.sub(r"[.]+$", "", s)
    # prefixos de rotulagem ("PARADA", "PARDA" [erro de digitação], "PRAIA" [erro de "PARADA"])
    s = re.sub(r"^(PARADA|PARDA|PRAIA)\s+", "", s)
    s = re.sub(r"^(EM\s+FREN(TE|E)|DE\s+FRENTE)\s+(A|AO|DA|DO|A\s+O)\s+", "", s)
    s = re.sub(r"^(DO|DA|DE)\s+", "", s)
    return re.sub(r"\s+", " ", s).strip()

def sentido(s):
    m = re.search(r"\b(IDA|VOLTA)\b\s*\.?$", sem_acento(s.upper()).strip())
    return m.group(1).lower() if m else None

raw["nome_limpo"] = raw.nome_raw.map(limpar_nome).str.replace(r"\s+(IDA|VOLTA)$", "", regex=True)
raw["sentido_no_nome"] = raw.nome_raw.map(sentido)

# ---------- 2. endereço normalizado (chave) e atributos ----------
def chave_endereco(s):
    s = sem_acento(s.lower())
    s = re.sub(r"republica federativa do brasil|,?\s*brasil$", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()

def parse_endereco(s):
    via = re.split(r",| - ", s)[0].strip()
    if "UFRN" in s or "Natal Shopping" in s:      # endereços que começam pelo nome do local
        m = re.search(r"(?:Av\.?|Avenida|Rua|R\.)\s[^,]+", s); via = m.group(0).strip() if m else via
    bairro = None
    m = re.search(r",\s*([^,()]+?)\s*\(([^)]+)\)\s*$", s)              # "..., Bairro (Município)"
    if m: bairro = m.group(1)
    else:
        ms = re.findall(r"([^,\-]+?),\s*[^,\-]+?\s-\sRN", s)             # "Bairro, Cidade - RN"
        ms2 = re.findall(r"\s-\s([^,]+?),\s*RN", s)                      # "- Bairro, RN"
        bairro = (ms or ms2 or [None])[-1]
        if bairro: bairro = bairro.strip()
    return pd.Series({"via": via, "bairro": bairro})

raw["end_chave"] = raw.endereco_raw.map(chave_endereco)
raw[["via", "bairro"]] = raw.endereco_raw.apply(parse_endereco)

# ---------- 3. aliases manuais (mesma parada física, texto diferente entre PDFs) ----------
# (nome_limpo, chave_do_endereço_variante) -> chave do endereço canônico
ALIAS_ENDERECO = {
    # mesma parada física, texto de endereço diferente entre PDFs
    ("KERO KERO", chave_endereco("Av Sen. Salgado Filho, Rio Grande Do Norte, Candelaria (Natal)")):
        chave_endereco("Av. Sen. Salgado Filho - Pitimbu, Natal - RN, 59086-000, Brasil"),
    # Av. Ayrton Senna, 5628 está dentro da faixa 5320-5724
    ("CEPE", chave_endereco("Av Ayrton Senna, 5628, Rio Grande Do Norte, Neopolis (Parnamirim)")):
        chave_endereco("Av. Ayrton Senna, 5320-5724 - Parque dos Eucaliptos, Parnamirim - RN, 59088-100, Brasil"),
    # Av. Maria Lacerda Montenegro, 2092 está dentro da faixa 2028-2168, mesma posição na sequência
    ("NORDESTAO", chave_endereco("Av Maria Lacerda Montenegro, 2092, Rio Grande Do Norte, Nova Parnamirim (Parnamirim)")):
        chave_endereco("Av. Maria Lacerda Montenegro, 2028-2168 - Parque dos Eucaliptos, Parnamirim - RN, 59152-600, Brasil"),
}
raw["end_chave"] = [ALIAS_ENDERECO.get((n, e), e) for n, e in zip(raw.nome_limpo, raw.end_chave)]

# endereço genérico (sem número) usado em sentidos opostos por duas linhas: separar por linha
SEPARAR_POR_LINHA = {("745.1", "PRAIA SHOPPING")}
raw["end_chave"] = [e + f" #{l}" if (l, n) in SEPARAR_POR_LINHA else e
                    for l, n, e in zip(raw.linha, raw.nome_limpo, raw.end_chave)]

# ---------- 4. identificador de parada = (nome limpo, endereço normalizado) ----------
raw["parada_key"] = raw.nome_limpo + " | " + raw.end_chave
chaves = {k: i for i, k in enumerate(raw.parada_key.drop_duplicates(), start=1)}
raw["parada_id"] = raw.parada_key.map(chaves).map(lambda i: f"P{i:03d}")

# auditoria: mesmo nome, mais de um nó -> revisão manual
aud = (raw.groupby(["nome_limpo", "parada_id"])
          .agg(endereco=("endereco_raw", "first"), linhas=("linha", lambda x: ",".join(sorted(set(x)))), registros=("seq", "size"))
          .reset_index())
aud = aud[aud.groupby("nome_limpo").parada_id.transform("nunique") > 1]
aud.to_csv("data/auditoria_nomes.csv", index=False)

# ---------- 5. arquivos limpos ----------
raw = raw.sort_values(["linha", "seq"]).reset_index(drop=True)
raw["ordem"] = raw.groupby("linha").cumcount() + 1
raw["salto_seq"] = raw.groupby("linha").seq.diff().fillna(1).astype(int) != 1   # PDF pulou um número
itin = raw[["linha", "titulo_linha", "ordem", "seq", "parada_id", "nome_raw", "nome_limpo", "sentido_no_nome", "salto_seq"]]
itin.to_csv("data/itinerarios_limpo.csv", index=False)

paradas = (raw.groupby("parada_id")
    .agg(nome=("nome_limpo", "first"), endereco=("endereco_raw", "first"), via=("via", "first"),
         bairro=("bairro", "first"), n_linhas=("linha", "nunique"),
         linhas=("linha", lambda x: ",".join(sorted(set(x)))),
         sentido=("sentido_no_nome", lambda x: x.dropna().iloc[0] if x.notna().any() else None))
    .reset_index())
paradas.to_csv("data/paradas.csv", index=False)

# ---------- 6. rede: nó = parada; aresta A->B = B vem logo após A em algum itinerário ----------
arestas = {}
for linha, g in raw.groupby("linha"):
    ids = list(g.parada_id); saltos = list(g.salto_seq)
    for i in range(len(ids) - 1):
        a, b = ids[i], ids[i + 1]
        if a == b: continue                         # sem laços (parada repetida em sequência)
        d = arestas.setdefault((a, b), {"linhas": set(), "salto": False})
        d["linhas"].add(linha); d["salto"] |= saltos[i + 1]
E = pd.DataFrame([{"origem": a, "destino": b, "peso": len(d["linhas"]),
                   "linhas": ",".join(sorted(d["linhas"])), "seq_com_salto": d["salto"]}
                  for (a, b), d in arestas.items()])
E.to_csv("data/arestas.csv", index=False)

# incidência linha x parada (rede bipartida, semana 6)
inc = pd.crosstab(raw.linha, raw.parada_id).clip(upper=1)
inc.to_csv("data/incidencia_linha_parada.csv")

G = nx.DiGraph()
for _, r in paradas.iterrows():
    G.add_node(r.parada_id, nome=r.nome, via=str(r["via"]), bairro=str(r.bairro), n_linhas=int(r.n_linhas), linhas=r.linhas)
for _, r in E.iterrows():
    G.add_edge(r.origem, r.destino, weight=int(r.peso), linhas=r.linhas)
nx.write_graphml(G, "rede_v1.graphml")

print(f"registros brutos: {len(raw)} | paradas únicas (nós): {G.number_of_nodes()} | arestas: {G.number_of_edges()}")
print(f"nomes brutos distintos: {raw.nome_raw.nunique()} -> nomes limpos distintos: {raw.nome_limpo.nunique()}")
print(f"nomes com >1 nó (ver data/auditoria_nomes.csv): {aud.nome_limpo.nunique()}")
