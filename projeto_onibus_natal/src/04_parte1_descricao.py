"""Parte 1 - Descrição da rede: grau, distribuição de grau, densidade, matriz de adjacência, sub-redes por linha. (semanas 2 e 3)"""
import numpy as np, pandas as pd, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from collections import Counter

G = nx.read_graphml("rede_v1.graphml")
P = pd.read_csv("data/paradas.csv").set_index("parada_id")
E = pd.read_csv("data/arestas.csv")

# --- graus ---
df = pd.DataFrame({"grau_entrada": dict(G.in_degree()), "grau_saida": dict(G.out_degree()),
                   "forca_entrada": dict(G.in_degree(weight="weight")), "forca_saida": dict(G.out_degree(weight="weight"))})
df["grau_total"] = df.grau_entrada + df.grau_saida
df["forca_total"] = df.forca_entrada + df.forca_saida
df = P[["nome", "bairro", "via", "n_linhas", "linhas"]].join(df)
df.sort_values("grau_total", ascending=False).to_csv("data/analise/p1_graus.csv")

print("== grau (dirigido) ==")
print(df[["grau_entrada", "grau_saida", "grau_total", "forca_total"]].describe().round(2).loc[["mean", "50%", "max"]])
dist_in = Counter(df.grau_entrada); dist_out = Counter(df.grau_saida); dist_tot = Counter(df.grau_total)
print("distribuição grau de entrada :", dict(sorted(dist_in.items())))
print("distribuição grau de saída   :", dict(sorted(dist_out.items())))
print("distribuição grau total      :", dict(sorted(dist_tot.items())))
print("fontes (entrada 0):", list(df[df.grau_entrada == 0].nome), "| sumidouros (saída 0):", list(df[df.grau_saida == 0].nome))
print("nós com grau total > 2 ('encruzilhadas'):", int((df.grau_total > 2).sum()))
print(df[df.grau_total > 2][["nome", "grau_entrada", "grau_saida", "grau_total", "n_linhas"]].sort_values("grau_total", ascending=False).head(12).to_string())

# --- densidade e reciprocidade ---
print("\n== densidade ==", round(nx.density(G), 5), "| reciprocidade:", round(nx.reciprocity(G), 4))
print("grau médio de entrada = grau médio de saída =", round(G.number_of_edges() / G.number_of_nodes(), 3))

# --- matriz de adjacência (dirigida, binária e ponderada) ---
nodes = list(G.nodes)
A = nx.to_numpy_array(G, nodelist=nodes, weight=None, dtype=int)
Aw = nx.to_numpy_array(G, nodelist=nodes, weight="weight", dtype=int)
pd.DataFrame(Aw, index=nodes, columns=nodes).to_csv("data/analise/p1_matriz_adjacencia_ponderada.csv")
print(f"\n== matriz de adjacência {A.shape}: {A.sum()} entradas não nulas = {A.sum() / A.size:.4%} (esparsa); soma das linhas = grau de saída ✓" if (A.sum(1) == df.loc[nodes, 'grau_saida'].values).all() else "ERRO adjacência")
print("tr(A)=", np.trace(A), "(sem laços) | pesos:", dict(sorted(Counter(Aw[Aw > 0]).items())))

# --- sub-redes (uma por linha) ---
rows = []
for linha in sorted(E.linhas.str.split(",").explode().unique()):
    ed = E[E.linhas.str.split(",").map(lambda x: linha in x)]
    H = nx.DiGraph(); H.add_edges_from(zip(ed.origem, ed.destino))
    rows.append({"linha": linha, "nos": H.number_of_nodes(), "arestas": H.number_of_edges(),
                 "densidade": round(nx.density(H), 4),
                 "nos_compartilhados_com_outras": sum(1 for n in H if P.loc[n, "n_linhas"] > 1),
                 "pct_compartilhado": round(100 * sum(1 for n in H if P.loc[n, "n_linhas"] > 1) / H.number_of_nodes(), 1)})
sub = pd.DataFrame(rows); sub.to_csv("data/analise/p1_subredes_por_linha.csv", index=False)
print("\n== sub-redes por linha =="); print(sub.to_string(index=False))

# --- figura: distribuição de grau ---
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
ks = sorted(dist_tot); ax[0].bar(ks, [dist_tot[k] for k in ks], color="#2f7078"); ax[0].set_xlabel("grau total (entrada + saída)"); ax[0].set_ylabel("nº de paradas"); ax[0].set_title("Distribuição de grau")
ks = sorted(df.n_linhas.unique()); c = Counter(df.n_linhas); ax[1].bar(ks, [c[k] for k in ks], color="#5d4fa0"); ax[1].set_xlabel("nº de linhas que passam pela parada"); ax[1].set_title("Compartilhamento entre linhas")
fig.tight_layout(); fig.savefig("figs/p1_distribuicao_grau.png", dpi=150)
