"""Parte 6 - Modelagens alternativas: (a) ida e volta fundidas, terminais unificados; (b) rede bipartida linha x parada, projeção e Jaccard. (semanas 2, 4 e 6)
Pergunta de robustez: as conclusões das partes 3 e 4 sobrevivem à mudança de modelagem?"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from metricas import Avaliador, normaliza_via
from variantes import montar

P = pd.read_csv("data/paradas.csv").set_index("parada_id")
IT = pd.read_csv("data/itinerarios_limpo.csv", dtype={"linha": str})
pd.set_option("display.width", 220)
NOMES = {"v1": "v1 original", "v2": "v2 ida/volta fundidas", "v3": "v3 = v2 + terminais unificados"}

# ===================== 6.1 variantes de modelagem =====================
# Os conjuntos "tronco" e "corredor" são definidos UMA vez, na v1 (paradas físicas), e mapeados para cada variante,
# para que as três modelagens removam as mesmas paradas e o dano seja comparável.
G1, _ = montar("v1", IT, P)
tronco_ids = {x for a, c, w in G1.edges(data="weight") if int(w) >= 5 for x in (a, c)}            # nós de trechos com >= 5 linhas
corredor_ids = tronco_ids | {i for i in P.index if normaliza_via(P.loc[i, "via"]) == "av sen salgado filho"}

res, grafos, mapas, bet = [], {}, {}, {}
for v in ["v1", "v2", "v3"]:
    G, m = montar(v, IT, P); grafos[v], mapas[v] = G, m
    if v != "v1": nx.write_graphml(G, f"rede_{v}.graphml")
    AV = Avaliador(G); n = len(AV.nodes); off = AV.reach0
    d = AV.D0[off]; sccs = list(nx.strongly_connected_components(G)); b = nx.betweenness_centrality(G); bet[v] = b
    tr = {m[i] for i in tronco_ids}; sf = {m[i] for i in corredor_ids}; top1 = max(b, key=b.get)
    res.append({"variante": NOMES[v], "nos": n, "arestas": G.number_of_edges(), "WCC": nx.number_weakly_connected_components(G), "SCC": len(sccs), "maior_SCC": max(map(len, sccs)),
                "pares_alcancaveis_pct": round(100 * off.sum() / (n * (n - 1)), 1), "dist_media": round(d.mean(), 1), "diametro": int(d.max()), "eficiencia": round(AV.inv0.sum() / (n * (n - 1)), 4),
                "top1_betweenness": f"{G.nodes[top1]['nome']} ({b[top1]:.2f})",
                "dano_tronco": round(AV.remover_nos(tr)["dano"], 3), "k_tronco": len(tr),
                "dano_corredor_Salgado_Filho": round(AV.remover_nos(sf)["dano"], 3), "k_corredor": len(sf),
                "dano_max_1_parada": round(max(AV.remover_nos([x])["dano"] for x in AV.nodes), 3)})
R = pd.DataFrame(res); R.to_csv("data/analise/p6_variantes.csv", index=False)
print("== 6.1 variantes de modelagem ==")
print(R.set_index("variante").T.to_string())

# fusões feitas na v2 (para auditoria manual)
k2 = mapas["v2"]; aud = pd.DataFrame({"parada_id": list(k2), "no_v2": list(k2.values())}); aud["nome"] = aud.parada_id.map(P.nome); aud["endereco"] = aud.parada_id.map(P.endereco)
aud = aud[aud.groupby("no_v2").parada_id.transform("size") > 1].sort_values("no_v2"); aud.to_csv("data/analise/p6_fusoes_v2.csv", index=False)
print(f"\nv2 fundiu {aud.no_v2.nunique()} locais (a partir de {len(aud)} paradas da v1); lista em data/analise/p6_fusoes_v2.csv")
tam = aud.groupby("no_v2").size().value_counts().to_dict(); print("tamanho dos grupos fundidos (nº de paradas v1 por nó v2):", tam)

# o ranking de betweenness se mantém entre v1 e v2? (por nó v2: maior betweenness entre os membros da v1)
b1 = pd.Series(bet["v1"]); m2 = pd.Series(mapas["v2"]); b1_por_v2 = b1.groupby(m2).max(); b2 = pd.Series(bet["v2"]).loc[b1_por_v2.index]
print(f"Spearman betweenness v1 (máx. dos membros) x v2: {spearmanr(b1_por_v2, b2)[0]:.2f}")
t5 = lambda b: [G.nodes[x]["nome"] for x, _ in sorted(b.items(), key=lambda t: -t[1])[:6]]
for v in ["v1", "v2", "v3"]:
    G = grafos[v]; print(f"top 6 betweenness {v}:", t5(bet[v]))

# ===================== 6.2 rede bipartida linha x parada =====================
print("\n== 6.2 rede bipartida linha x parada ==")
for v in ["v1", "v2"]:
    k = mapas[v]; df = IT.assign(no=IT.parada_id.map(k))[["linha", "no"]].drop_duplicates()
    M = pd.crosstab(df.linha, df.no).clip(upper=1); M.to_csv(f"data/analise/p6_incidencia_{v}.csv")
    X = M.values; inter = X @ X.T; tam = X.sum(1); J = inter / (tam[:, None] + tam[None, :] - inter)
    Jd = pd.DataFrame(J, index=M.index, columns=M.index); Jd.round(3).to_csv(f"data/analise/p6_jaccard_linhas_{v}.csv")
    print(f"\n[{v}] linhas = {M.shape[0]}, paradas = {M.shape[1]}, arestas bipartidas = {int(X.sum())}, densidade = {X.sum() / X.size:.3f}")
    print("paradas por linha:", dict(zip(M.index, tam)))
    print("Jaccard entre linhas (compartilhamento de paradas):"); print(Jd.round(2).to_string())
    pares = sorted(((Jd.loc[a, b], a, b) for i, a in enumerate(M.index) for b in M.index[i + 1:]), reverse=True)
    print("mais parecidas:", [(a, b, round(j, 2)) for j, a, b in pares[:3]], "| menos parecidas:", [(a, b, round(j, 2)) for j, a, b in pares[-3:]])
    if v == "v1": J1 = Jd
    else: J2 = Jd
    # assinaturas: paradas com o mesmo conjunto de linhas
    sig = M.apply(lambda c: ",".join(M.index[c.values == 1]), axis=0); vc = sig.value_counts()
    print(f"[{v}] conjuntos distintos de linhas por parada: {len(vc)}; os 6 mais frequentes:"); print(vc.head(6).to_string())
    # projeção sobre paradas: peso = nº de linhas em comum; esqueleto = pares com >= 5 linhas em comum
    W = X.T @ X; np.fill_diagonal(W, 0); iu = np.triu_indices_from(W, 1)
    S = nx.Graph([(M.columns[i], M.columns[j]) for i, j in zip(*iu) if W[i, j] >= 5])
    comp = sorted(nx.connected_components(S), key=len, reverse=True)
    print(f"[{v}] projeção sobre paradas, esqueleto (>= 5 linhas em comum): {S.number_of_nodes()} paradas, {S.number_of_edges()} pares, componentes: {[len(c) for c in comp]}")
    if v == "v1":
        G1 = grafos["v1"]; tr = {x for a, c, w in G1.edges(data="weight") if int(w) >= 5 for x in (a, c)}
        print(f"    paradas do esqueleto = {S.number_of_nodes()}; do tronco sequencial (peso>=5) = {len(tr)}; em comum = {len(set(S.nodes) & tr)}")

# ===================== figuras =====================
fig, ax = plt.subplots(1, 3, figsize=(14, 4.2), gridspec_kw={"width_ratios": [1, 1, 1.4]})
for a, Jd, t in [(ax[0], J1, "v1 (ida/volta separadas)"), (ax[1], J2, "v2 (ida/volta fundidas)")]:
    im = a.imshow(Jd.values, vmin=0, vmax=1, cmap="viridis"); a.set_xticks(range(6)); a.set_yticks(range(6)); a.set_xticklabels(Jd.columns, rotation=45); a.set_yticklabels(Jd.index); a.set_title(f"Jaccard entre linhas\n{t}", fontsize=10)
    for i in range(6):
        for j in range(6): a.text(j, i, f"{Jd.values[i, j]:.2f}", ha="center", va="center", color="w" if Jd.values[i, j] < .6 else "k", fontsize=7)
fig.colorbar(im, ax=ax[:2], shrink=.8)
x = np.arange(3); w = .27; Rv = R.set_index("variante")
ax[2].bar(x - w, 100 * Rv.dano_tronco, w, label="remover o tronco (peso>=5)", color="#c0562b"); ax[2].bar(x, 100 * Rv.dano_corredor_Salgado_Filho, w, label="remover o corredor Salgado Filho", color="#2f7078")
ax[2].bar(x + w, Rv.pares_alcancaveis_pct, w, label="pares alcançáveis (%)", color="#aaa"); ax[2].set_xticks(x); ax[2].set_xticklabels(["v1", "v2", "v3"]); ax[2].set_ylabel("%"); ax[2].legend(fontsize=7); ax[2].set_title("Robustez da conclusão à modelagem", fontsize=10)
fig.savefig("figs/p6_alternativas.png", dpi=150, bbox_inches="tight")
