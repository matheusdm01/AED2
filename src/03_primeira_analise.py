"""Etapa 3 - Sanidade da rede v1: estatísticas básicas e figura. (Não é a análise final.)"""
import pandas as pd, networkx as nx, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

G = nx.read_graphml("rede_v1.graphml")
P = pd.read_csv("data/paradas.csv").set_index("parada_id")

und = G.to_undirected()
gcc = max(nx.connected_components(und), key=len)
resumo = {
    "nos": G.number_of_nodes(), "arestas": G.number_of_edges(), "densidade": round(nx.density(G), 4),
    "WCC": nx.number_weakly_connected_components(G), "SCC": nx.number_strongly_connected_components(G),
    "diametro_nao_dirigido_GCC": nx.diameter(und.subgraph(gcc)),
    "grau_medio_total": round(sum(d for _, d in G.degree()) / G.number_of_nodes(), 2),
}
print(resumo)

# betweenness só para conferir se a rede "faz sentido" (top 8)
bc = nx.betweenness_centrality(G, weight=None, normalized=True)
top = sorted(bc, key=bc.get, reverse=True)[:8]
for n in top:
    print(f"{bc[n]:.3f}  {n}  {P.loc[n,'nome']:<28} {P.loc[n,'bairro']:<18} linhas={P.loc[n,'linhas']}")

# figura: cor = nº de linhas que passam; espessura = peso
pos = nx.spring_layout(und, seed=42, k=0.15, iterations=200)
fig, ax = plt.subplots(figsize=(12, 9))
w = [G[u][v]["weight"] for u, v in G.edges()]
nx.draw_networkx_edges(G, pos, ax=ax, width=[0.4 + 0.6 * x for x in w], alpha=0.5, arrows=False, edge_color="#7a8899")
nl = [P.loc[n, "n_linhas"] for n in G.nodes()]
sc = nx.draw_networkx_nodes(G, pos, ax=ax, node_size=[20 + 25 * x for x in nl], node_color=nl, cmap="viridis", linewidths=0.3, edgecolors="k")
plt.colorbar(sc, ax=ax, shrink=0.6, label="nº de linhas que passam pela parada")
ax.set_title("Rede v1: paradas das linhas 97, 98, 738, 740, 745.1 e 745.2 (Viação Cidade das Dunas)")
ax.axis("off"); fig.tight_layout(); fig.savefig("figs/rede_v1.png", dpi=150)
