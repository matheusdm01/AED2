"""Parte 3 - Centralidades: grau, closeness, betweenness (nós e trechos) e eigenvector; hubs x pontes. (semana 4)"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, networkx as nx
from scipy.stats import spearmanr
from metricas import carregar

G = carregar(); P = pd.read_csv("data/paradas.csv").set_index("parada_id")
und = G.to_undirected()
for u, v, d in und.edges(data=True): d["weight"] = int(d["weight"])

C = pd.DataFrame(index=G.nodes)
C["grau_total"] = pd.Series(dict(G.degree()))
C["forca_total"] = pd.Series(dict(G.degree(weight="weight")))
# closeness dirigida (distância de chegada, com correção para grafos não fortemente conectados) e não dirigida
C["closeness_dir"] = pd.Series(nx.closeness_centrality(G, wf_improved=True))
C["closeness_nao_dir"] = pd.Series(nx.closeness_centrality(und))
# betweenness (nº de caminhos mínimos dirigidos que passam pelo nó, normalizado), sem e com sentido
C["betweenness_dir"] = pd.Series(nx.betweenness_centrality(G, normalized=True))
C["betweenness_nao_dir"] = pd.Series(nx.betweenness_centrality(und, normalized=True))
# eigenvector: só faz sentido na versão não dirigida (no grafo dirigido, o autovetor concentra-se na SCC grande e zera o resto)
C["eigenvector_nao_dir"] = pd.Series(nx.eigenvector_centrality_numpy(und, weight="weight")).abs().round(10)   # abs(): o autovetor de Perron é não negativo (evita "-0.0"); round: ruído de 1e-14 mudaria desempates de ranking
C = P[["nome", "bairro", "via", "n_linhas", "linhas"]].join(C)
C.round(10).to_csv("data/analise/p3_centralidades.csv")

pd.set_option("display.width", 200)
def top(col, k=10):
    t = C.sort_values(col, ascending=False).head(k)
    print(f"\n-- top {k} por {col}"); print(t[["nome", "bairro", "n_linhas", col]].round(3).to_string())
for c in ["grau_total", "closeness_dir", "betweenness_dir", "eigenvector_nao_dir"]: top(c)

# --- hubs x pontes: as medidas apontam as mesmas paradas? ---
print("\n== correlação de Spearman entre medidas ==")
cols = ["grau_total", "forca_total", "closeness_dir", "betweenness_dir", "betweenness_nao_dir", "eigenvector_nao_dir"]
rho = C[cols].corr(method="spearman").round(2); print(rho.to_string()); rho.to_csv("data/analise/p3_spearman.csv")

print("\n== sobreposição entre os 20 primeiros de cada medida ==")
t20 = {c: set(C.sort_values(c, ascending=False).head(20).index) for c in ["grau_total", "closeness_dir", "betweenness_dir", "eigenvector_nao_dir"]}
for a in t20:
    print(a, {b: len(t20[a] & t20[b]) for b in t20 if b != a})

# hubs (grau alto) que NÃO são pontes e pontes (betweenness alto) com grau baixo
hubs = C[C.grau_total >= 4]; pontes = C[C.betweenness_dir >= C.betweenness_dir.quantile(0.9)]
print(f"\nnós com grau >= 4: {len(hubs)}; mediana do betweenness deles = {hubs.betweenness_dir.median():.3f} vs mediana geral {C.betweenness_dir.median():.3f}")
print("top 10% por betweenness (20 nós): grau total mediano =", pontes.grau_total.median(), "| nº de linhas mediano =", pontes.n_linhas.median())
print("pontes com grau 2 (só passagem, sem entroncamento):", int((pontes.grau_total == 2).sum()), "de", len(pontes))

# --- betweenness de trechos (arestas) ---
eb = nx.edge_betweenness_centrality(G, normalized=True)
EB = pd.DataFrame([{"origem": u, "destino": v, "de": P.loc[u, "nome"], "para": P.loc[v, "nome"], "peso_linhas": G[u][v]["weight"],
                    "linhas": G[u][v]["linhas"], "betweenness_trecho": b} for (u, v), b in eb.items()]).sort_values("betweenness_trecho", ascending=False)
EB.to_csv("data/analise/p3_betweenness_trechos.csv", index=False)
print("\n-- top 10 trechos por betweenness"); print(EB.head(10)[["de", "para", "peso_linhas", "betweenness_trecho"]].round(3).to_string(index=False))
print("correlação (Spearman) betweenness do trecho x peso (nº de linhas):", round(spearmanr(EB.betweenness_trecho, EB.peso_linhas)[0], 2))

# --- betweenness ponderada: peso = nº de linhas -> custo menor onde há mais linhas (custo = 1/peso) ---
H = G.copy()
for u, v, d in H.edges(data=True): d["custo"] = 1 / int(d["weight"])
bw = pd.Series(nx.betweenness_centrality(H, weight="custo", normalized=True))
print("\ncorrelação betweenness (sem peso) x (peso=1/nº linhas):", round(spearmanr(C.betweenness_dir, bw.loc[C.index])[0], 2))
C["betweenness_dir_ponderada"] = bw; C.round(10).to_csv("data/analise/p3_centralidades.csv")
print("top 5 ponderada:", [P.loc[i, "nome"] for i in bw.sort_values(ascending=False).head(5).index])
