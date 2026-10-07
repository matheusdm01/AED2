"""Parte 7 - Figuras finais (para o README e o vídeo) e checagem de sensibilidade do limiar do tronco (parte 8).
Todas as figuras saem em figs/f*.png e são geradas inteiramente pelo código."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from metricas import carregar, Avaliador

SEED, N_NULO = 42, 500
G = carregar(); P = pd.read_csv("data/paradas.csv").set_index("parada_id")
RN = pd.read_csv("data/analise/p4_remocao_nos.csv").set_index("parada_id")
IT = pd.read_csv("data/itinerarios_limpo.csv", dtype={"linha": str})
CUR = pd.read_csv("data/analise/p4_curvas_ataque.csv", index_col=0)
VAR = pd.read_csv("data/analise/p6_variantes.csv")
AV = Avaliador(G); und = nx.Graph(G.to_undirected())
tronco_arestas = [(u, v) for u, v, d in G.edges(data="weight") if int(d) >= 5]
tronco = sorted({x for e in tronco_arestas for x in e})
COR = {"tronco": "#c0562b", "base": "#2f7078", "roxo": "#5d4fa0", "cinza": "#9aa5ae"}
nome = lambda n: P.loc[n, "nome"].title().replace("Estacao", "Estação").replace("Acai", "Açaí").replace("Atacadao", "Atacadão").replace("Neopolis", "Néopolis").replace("Sams Club", "Sam's Club").replace("Pg Prime", "PG Prime").replace(" De ", " de ").replace("Espaco", "Espaço")

# ============ F1: rede com o dano de cada parada e o tronco em destaque ============
pos = nx.kamada_kawai_layout(und)
fig, ax = plt.subplots(figsize=(12, 9))
w = [0.4 + 0.5 * int(G[u][v]["weight"]) for u, v in G.edges()]
nx.draw_networkx_edges(G, pos, ax=ax, width=w, edge_color=COR["cinza"], alpha=.55, arrows=False)
nx.draw_networkx_edges(G, pos, edgelist=tronco_arestas, ax=ax, width=3.2, edge_color=COR["tronco"], arrows=False)
dano = RN.dano.loc[list(G.nodes)]
sc = nx.draw_networkx_nodes(G, pos, ax=ax, node_size=28 + 150 * dano.values, node_color=100 * dano.values, cmap="YlOrRd", vmin=0, edgecolors="k", linewidths=.3)
cb = plt.colorbar(sc, ax=ax, shrink=.55, pad=.01); cb.set_label("dano ao remover a parada (% dos pares conectados perdidos)")
por_nome = lambda nm, via=None: next(n for n in G if P.loc[n, "nome"] == nm and (via is None or via in str(P.loc[n, "via"])))
rotulos = {dano.idxmax(): (-25, -48), dano.drop(dano.idxmax()).idxmax(): (-110, 28), por_nome("KERO KERO"): (34, 24), por_nome("SAMS CLUB"): (-30, 30),
           por_nome("ESPACO REDUZIDO", "Abel Cabral"): (50, -42), por_nome("TERMINAL DE NOVA PARNAMIRIM"): (-150, -28)}
for n, off in rotulos.items():
    via = " (Abel Cabral)" if P.loc[n, "nome"] == "ESPACO REDUZIDO" else ""
    ax.annotate(f"{nome(n)}{via}\n{100 * dano[n]:.0f}%", pos[n], xytext=off, textcoords="offset points", fontsize=8.5, arrowprops=dict(arrowstyle="-", color="k", lw=.7), bbox=dict(boxstyle="round,pad=.25", fc="w", ec="#888", alpha=.95), zorder=10)
ax.legend(handles=[Line2D([0], [0], color=COR["tronco"], lw=3, label="tronco: trechos usados por 5 das 6 linhas"), Line2D([0], [0], color=COR["cinza"], lw=1.5, label="demais trechos (espessura = nº de linhas)")], loc="lower left", fontsize=9)
ax.set_title("Rede de 202 paradas (6 linhas, Terminal de Nova Parnamirim): onde um bloqueio dói mais"); ax.axis("off")
fig.tight_layout(); fig.savefig("figs/f1_rede_dano.png", dpi=150); plt.close(fig)

# ============ F2: exemplo de modelagem com trecho real do corredor ============
comp = sorted(nx.weakly_connected_components(nx.DiGraph(tronco_arestas)), key=len, reverse=True)[0]
sub = nx.DiGraph(tronco_arestas).subgraph(comp)
ordem = list(nx.topological_sort(sub))
ant = [p for p in G.predecessors(ordem[0])][:1]; suc = [s for s in G.successors(ordem[-1])][:1]
cad = ant + ordem + suc
fig, ax = plt.subplots(figsize=(13, 3.6)); x = {n: i for i, n in enumerate(cad)}
for u, v in zip(cad, cad[1:]):
    wgt = int(G[u][v]["weight"]); ax.annotate("", xy=(x[v] - .16, 0), xytext=(x[u] + .16, 0), arrowprops=dict(arrowstyle="-|>", lw=1 + wgt, color=COR["tronco"] if wgt >= 5 else COR["cinza"]))
    ax.text((x[u] + x[v]) / 2, .22, f"{wgt} linha{'s' if wgt > 1 else ''}", ha="center", fontsize=8); ax.text((x[u] + x[v]) / 2, -.28, G[u][v]["linhas"].replace(",", " "), ha="center", fontsize=7, color="#555")
for n in cad:
    ax.scatter([x[n]], [0], s=420, color=COR["base"], zorder=3); ax.text(x[n], -.62, nome(n).replace(" ", "\n", 1), ha="center", va="top", fontsize=8)
ax.set_xlim(-.6, len(cad) - .4); ax.set_ylim(-1.3, .7); ax.axis("off")
ax.set_title("Modelagem (trecho real, sentido de ida): nó = parada, aresta dirigida A → B = B vem logo depois de A, peso = nº de linhas no trecho", fontsize=10)
fig.tight_layout(); fig.savefig("figs/f2_modelagem_exemplo.png", dpi=150); plt.close(fig)

# ============ F3: painel-resumo dos resultados ============
rng = np.random.default_rng(SEED); seqs = [list(g.sort_values("ordem").parada_id) for _, g in IT.groupby("linha")]
def janela(k):
    cand = [s for s in seqs if len(s) >= k]; s = cand[rng.integers(len(cand))]; i = rng.integers(len(s) - k + 1); return list(set(s[i:i + k]))
nulo = np.array([AV.remover_nos(janela(len(tronco)))["dano"] for _ in range(N_NULO)]); obs = AV.remover_nos(tronco)["dano"]
fig, ax = plt.subplots(2, 2, figsize=(13, 8.6))
t = RN.sort_values("dano", ascending=False).head(10).iloc[::-1]
ax[0, 0].barh([f"{nome(i)} ({int(P.loc[i, 'n_linhas'])} linhas)" for i in t.index], 100 * t.dano, color=COR["roxo"]); ax[0, 0].set_xlabel("dano (%)"); ax[0, 0].set_title("(a) As 10 paradas mais críticas", fontsize=10)
ax[0, 1].hist(100 * nulo, bins=25, color=COR["cinza"], edgecolor="w"); ax[0, 1].axvline(100 * obs, color=COR["tronco"], lw=2.5)
ax[0, 1].text(100 * obs - 1.5, ax[0, 1].get_ylim()[1] * .62, f"tronco: {100 * obs:.0f}%\n(percentil {100 * (nulo < obs).mean():.0f})", color=COR["tronco"], ha="right", fontsize=9, bbox=dict(fc="w", ec="none", alpha=.85))
ax[0, 1].set_xlabel("dano (%)"); ax[0, 1].set_ylabel("nº de janelas"); ax[0, 1].set_title(f"(b) Tronco x {N_NULO} trechos contíguos de {len(tronco)} paradas", fontsize=10)
for c, est in [("betweenness (estático) | alcancabilidade", "betweenness (estático)"), ("betweenness (adaptativo) | alcancabilidade", "betweenness (adaptativo)"), ("grau (estático) | alcancabilidade", "grau (estático)"), ("aleatório (média de 100) | alcancabilidade", "aleatório (média de 100)")]:
    ax[1, 0].plot(CUR.index, CUR[c], marker="o", ms=3, label=est)
ax[1, 0].set_xlabel("paradas removidas"); ax[1, 0].set_ylabel("alcançabilidade restante"); ax[1, 0].legend(fontsize=8); ax[1, 0].grid(alpha=.3); ax[1, 0].set_title("(c) Ataques progressivos", fontsize=10)
xx = np.arange(3); ww = .38; ax[1, 1].bar(xx - ww / 2, 100 * VAR.dano_corredor_Salgado_Filho, ww, color=COR["base"], label="dano ao remover o corredor"); ax[1, 1].bar(xx + ww / 2, VAR.pares_alcancaveis_pct, ww, color=COR["cinza"], label="pares alcançáveis (%)")
ax[1, 1].set_xticks(xx); ax[1, 1].set_xticklabels(["v1 original", "v2 ida/volta\nfundidas", "v3 + terminais\nunificados"]); ax[1, 1].set_ylabel("%"); ax[1, 1].legend(fontsize=8, loc="lower right"); ax[1, 1].set_title("(d) O corredor resiste à modelagem; o nível absoluto não", fontsize=10)
fig.suptitle("Resumo: o corredor da Av. Senador Salgado Filho é o ponto crítico estrutural da rede", fontsize=12); fig.tight_layout(); fig.savefig("figs/f3_resumo_resultados.png", dpi=150); plt.close(fig)

# ============ F4: estrutura das linhas (conjuntos de linhas por parada) ============
sig = P.linhas.value_counts().head(8).iloc[::-1]
fig, ax = plt.subplots(figsize=(8, 4.2)); ax.barh([f"linhas {s.replace(',', ' + ')}" for s in sig.index], sig.values, color=COR["base"])
for i, v in enumerate(sig.values): ax.text(v + .3, i, str(v), va="center", fontsize=9)
ax.set_xlabel("nº de paradas"); ax.set_title("Que linhas compartilham cada parada (8 combinações mais frequentes)"); fig.tight_layout(); fig.savefig("figs/f4_assinaturas_linhas.png", dpi=150); plt.close(fig)

# ============ sensibilidade do limiar do tronco (parte 8) ============
rows = []
for lim in (3, 4, 5):
    S = sorted({x for u, v, d in G.edges(data="weight") if int(d) >= lim for x in (u, v)}); o = AV.remover_nos(S)["dano"]
    nl = np.array([AV.remover_nos(janela(len(S)))["dano"] for _ in range(N_NULO)])
    rows.append({"limiar_peso": lim, "k_paradas": len(S), "dano": round(o, 3), "dano_medio_janelas": round(nl.mean(), 3), "percentil_vs_janelas": round(100 * (nl < o).mean(), 1)})
SENS = pd.DataFrame(rows); SENS.to_csv("data/analise/p8_sensibilidade_limiar.csv", index=False)
print("== sensibilidade ao limiar que define o tronco =="); print(SENS.to_string(index=False))
print("top 10 paradas por dano:", [(nome(i), round(100 * d, 1)) for i, d in RN.dano.sort_values(ascending=False).head(10).items()])
print("tronco:", [nome(n) for n in tronco])
