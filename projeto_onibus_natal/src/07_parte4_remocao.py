"""Parte 4 - Teste de remoção: dano de cada parada, de cada trecho, de grupos (alagamento) e curvas de ataque. (semanas 3 e 4)
Dano = fração dos pares conectados que deixam de ser (definição da parte 0, ver src/metricas.py)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from metricas import carregar, Avaliador, normaliza_via, normaliza_bairro

SEED, N_NULO = 42, 500
rng = np.random.default_rng(SEED)
G = carregar(); P = pd.read_csv("data/paradas.csv").set_index("parada_id")
IT = pd.read_csv("data/itinerarios_limpo.csv", dtype={"linha": str})
C = pd.read_csv("data/analise/p3_centralidades.csv").set_index("parada_id")
AV = Avaliador(G); nodes = AV.nodes
pd.set_option("display.width", 200)

# ===== 4.1 remoção de cada parada =====
rows = [{"parada_id": n, "nome": P.loc[n, "nome"], "bairro": P.loc[n, "bairro"], "n_linhas": P.loc[n, "n_linhas"], **AV.remover_nos([n])} for n in nodes]
RN = pd.DataFrame(rows).set_index("parada_id")
RN["betweenness_dir"] = C.betweenness_dir; RN["grau_total"] = C.grau_total
RN.sort_values("dano", ascending=False).to_csv("data/analise/p4_remocao_nos.csv")
top = RN.sort_values("dano", ascending=False)
print("== 4.1 remoção de uma parada ==")
print(top.head(12)[["nome", "n_linhas", "dano", "perda_eficiencia", "n_wcc", "gcc_frac"]].round(3).to_string())
print(f"dano mediano: {RN.dano.median():.3f} | máximo: {RN.dano.max():.3f} | nós com dano > 0: {(RN.dano > 0).sum()} de {len(RN)} | com n_wcc > 1: {(RN.n_wcc > 1).sum()}")
for c in ["betweenness_dir", "grau_total", "n_linhas"]:
    print(f"Spearman dano x {c}: {spearmanr(RN.dano, RN[c])[0]:.2f}")
# o dano de uma parada depende de quantas linhas a usam? (dano médio por nº de linhas)
print("dano médio por nº de linhas que passam pela parada:", RN.groupby("n_linhas").dano.mean().round(3).to_dict())

# ===== 4.2 remoção de cada trecho =====
rows = [{"origem": u, "destino": v, "de": P.loc[u, "nome"], "para": P.loc[v, "nome"], "peso_linhas": int(d["weight"]), "linhas": d["linhas"], **AV.remover_arestas([(u, v)])}
        for u, v, d in G.edges(data=True)]
RE = pd.DataFrame(rows).sort_values("dano", ascending=False); RE.to_csv("data/analise/p4_remocao_trechos.csv", index=False)
print("\n== 4.2 remoção de um trecho ==")
print(RE.head(10)[["de", "para", "peso_linhas", "dano", "perda_eficiencia"]].round(3).to_string(index=False))
print("dano médio por peso do trecho (nº de linhas):", RE.groupby("peso_linhas").dano.mean().round(3).to_dict())
print(f"Spearman dano x peso: {spearmanr(RE.dano, RE.peso_linhas)[0]:.2f}")

# ===== 4.3 grupos (alagamento de uma região) =====
# tronco = nós das arestas usadas por >= 5 linhas (definido pelos dados, não pelo nome da rua)
tr = nx.DiGraph([(u, v) for u, v, d in G.edges(data=True) if int(d["weight"]) >= 5])
comp = sorted(nx.weakly_connected_components(tr), key=len, reverse=True)
grupos = {f"tronco (peso>=5), parte {i + 1} [{'ida' if i == 0 else 'volta'}]": sorted(c) for i, c in enumerate(comp)}
grupos["tronco completo (peso>=5)"] = sorted(set().union(*comp))
vias = P["via"].map(normaliza_via); bai = P["bairro"].map(normaliza_bairro)
for nome, ids in vias.groupby(vias).groups.items():
    if len(ids) >= 8: grupos[f"via: {nome}"] = list(ids)
for nome, ids in bai.groupby(bai).groups.items():
    if len(ids) >= 8: grupos[f"bairro: {nome}"] = list(ids)

# janelas contíguas de k paradas num itinerário (bloqueio de um trecho de rua) e conjuntos aleatórios
seqs = [list(g.sort_values("ordem").parada_id) for _, g in IT.groupby("linha")]
def janela(k):
    cand = [s for s in seqs if len(s) >= k]; s = cand[rng.integers(len(cand))]; i = rng.integers(len(s) - k + 1)
    return list(set(s[i:i + k]))
def nulo(k, tipo):
    out = []
    for _ in range(N_NULO):
        S = janela(k) if tipo == "janela" else list(rng.choice(nodes, size=k, replace=False))
        out.append(AV.remover_nos(S)["dano"])
    return np.array(out)

rows = []
for nome, S in grupos.items():
    m = AV.remover_nos(S); k = len(S)
    nj, na = nulo(k, "janela"), nulo(k, "aleatorio")
    rows.append({"grupo": nome, "k_paradas": k, "dano": m["dano"], "perda_eficiencia": m["perda_eficiencia"], "n_wcc": m["n_wcc"], "gcc_frac": m["gcc_frac"],
                 "dano_janela_media": nj.mean(), "pct_vs_janelas": 100 * (nj < m["dano"]).mean(),
                 "dano_aleatorio_medio": na.mean(), "pct_vs_aleatorio": 100 * (na < m["dano"]).mean()})
GR = pd.DataFrame(rows).sort_values("dano", ascending=False); GR.to_csv("data/analise/p4_grupos.csv", index=False)
print("\n== 4.3 remoção de grupos (nulos com N =", N_NULO, ") ==")
print(GR.round(3).to_string(index=False))

# ===== 4.4 curvas de ataque =====
KMAX = 20
def curva(ordem):
    r = [1.0]; g = [1.0]; S = []
    for n in ordem[:KMAX]:
        S.append(n); m = AV.remover_nos(S); r.append(m["alcancabilidade_restante"]); g.append(m["gcc_frac"])
    return np.array(r), np.array(g)
bet = list(C.sort_values("betweenness_dir", ascending=False).index)
deg = list(C.sort_values(["grau_total", "forca_total"], ascending=False).index)
S, ad = [], []
H = G.copy()
for _ in range(KMAX):                                    # ataque adaptativo: recalcula a betweenness a cada remoção
    b = nx.betweenness_centrality(H); n = max(b, key=b.get); ad.append(n); H.remove_node(n)
curvas = {"betweenness (estático)": curva(bet), "betweenness (adaptativo)": curva(ad), "grau (estático)": curva(deg)}
alea = [curva(list(rng.permutation(nodes))) for _ in range(100)]
curvas["aleatório (média de 100)"] = (np.mean([a[0] for a in alea], 0), np.mean([a[1] for a in alea], 0))
tab = pd.DataFrame({f"{k} | {m}": v[i] for k, v in curvas.items() for i, m in enumerate(["alcancabilidade", "gcc"])}); tab.index.name = "k_removidos"
tab.to_csv("data/analise/p4_curvas_ataque.csv")
print("\n== 4.4 alcançabilidade restante após remover k paradas (k = 0, 5, 10, 20) ==")
for nm, (r, g) in curvas.items(): print(f"{nm:<28}", [round(float(r[k]), 3) for k in (0, 5, 10, 20)])
print("primeiros 10 do ataque adaptativo:", [P.loc[n, "nome"] for n in ad[:10]])

# ===== figuras =====
fig, ax = plt.subplots(figsize=(8, 5)); t = top.head(15).iloc[::-1]
ax.barh([f"{n} ({int(l)} linhas)" for n, l in zip(t.nome, t.n_linhas)], 100 * t.dano, color="#5d4fa0")
ax.set_xlabel("dano (% dos pares conectados que deixam de ser)"); ax.set_title("As 15 paradas cuja remoção mais prejudica a rede")
fig.tight_layout(); fig.savefig("figs/p4_dano_paradas.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
for nm, (r, g) in curvas.items():
    ax[0].plot(range(KMAX + 1), r, marker="o", ms=3, label=nm); ax[1].plot(range(KMAX + 1), g, marker="o", ms=3, label=nm)
ax[0].set_ylabel("alcançabilidade restante"); ax[1].set_ylabel("fração na maior componente fraca")
for a in ax: a.set_xlabel("paradas removidas (k)"); a.grid(alpha=.3)
ax[0].legend(fontsize=8); fig.suptitle("Ataques à rede: remoção progressiva de paradas"); fig.tight_layout(); fig.savefig("figs/p4_curvas_ataque.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 5)); g = GR.sort_values("dano").tail(14)
y = np.arange(len(g)); ax.barh(y, 100 * g.dano, color="#2f7078", label="grupo observado")
ax.scatter(100 * g.dano_janela_media, y, color="#c0562b", zorder=3, label="média de janelas contíguas do mesmo tamanho")
ax.scatter(100 * g.dano_aleatorio_medio, y, color="k", marker="x", zorder=3, label="média de paradas aleatórias do mesmo tamanho")
ax.set_yticks(y); ax.set_yticklabels([f"{n} (k={k})" for n, k in zip(g.grupo, g.k_paradas)], fontsize=8); ax.set_xlabel("dano (%)")
ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False); ax.set_title("Remoção de grupos de paradas: observado x referência"); fig.tight_layout(); fig.savefig("figs/p4_grupos.png", dpi=150, bbox_inches="tight")
