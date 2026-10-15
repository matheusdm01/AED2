"""Parte 5 - Decomposição em núcleos: k-core, k-shell, core number, degeneracy, onion layers, k-truss. (semana 5)
Trabalha na versão não dirigida e sem laços da rede (a decomposição em núcleos usa o grau total)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from metricas import carregar

G = carregar(); P = pd.read_csv("data/paradas.csv").set_index("parada_id")
C = pd.read_csv("data/analise/p3_centralidades.csv").set_index("parada_id")
R = pd.read_csv("data/analise/p4_remocao_nos.csv").set_index("parada_id")
und = nx.Graph(G.to_undirected()); und.remove_edges_from(nx.selfloop_edges(und))
pd.set_option("display.width", 200)

core = nx.core_number(und); onion = nx.onion_layers(und)
D = P[["nome", "bairro", "n_linhas", "linhas"]].copy()
D["core_number"] = pd.Series(core); D["onion_layer"] = pd.Series(onion)
D["grau_nao_dir"] = pd.Series(dict(und.degree())); D["betweenness_dir"] = C.betweenness_dir; D["dano_remocao"] = R.dano
kmax = max(core.values())
print("== k-core (não dirigido) ==")
print("degeneracy (maior k com núcleo não vazio):", kmax)
tam = {k: len(nx.k_core(und, k)) for k in range(0, kmax + 1)}; shell = D.core_number.value_counts().sort_index()
print("tamanho do k-core:", tam); print("tamanho da k-shell:", shell.to_dict())
print("camadas onion: de", D.onion_layer.min(), "a", D.onion_layer.max())

print(f"\n-- núcleo máximo (k = {kmax}) tem {tam[kmax]} nós; as 10 camadas onion mais profundas ficam em:")
print(D.sort_values("onion_layer", ascending=False).head(10)[["nome", "bairro", "n_linhas", "onion_layer"]].to_string())
print("\n-- n_linhas médio por k-shell:", D.groupby("core_number").n_linhas.mean().round(2).to_dict())
print("-- dano médio de remoção por k-shell:", D.groupby("core_number").dano_remocao.mean().round(3).to_dict())
print("-- betweenness média por k-shell:", D.groupby("core_number").betweenness_dir.mean().round(3).to_dict())
for c in ["betweenness_dir", "dano_remocao", "n_linhas", "grau_nao_dir"]:
    print(f"Spearman core_number x {c}: {spearmanr(D.core_number, D[c])[0]:.2f} | onion_layer x {c}: {spearmanr(D.onion_layer, D[c])[0]:.2f}")

# o núcleo coincide com o corredor? (tronco = nós de arestas com peso >= 5)
tronco = {n for u, v, d in G.edges(data=True) if int(d["weight"]) >= 5 for n in (u, v)}
nucleo2 = set(D[D.core_number >= 2].index)
print(f"\ntronco (peso>=5): {len(tronco)} nós | no 2-core: {len(tronco & nucleo2)} | no k-core máximo: {len(tronco & set(D[D.core_number == kmax].index))}")
print(f"2-core: {len(nucleo2)} nós; destes, {len(tronco & nucleo2)} ({len(tronco & nucleo2) / len(nucleo2):.0%}) são do tronco")
print("1-shell (fora do 2-core, 'pontas pendentes'):", int((D.core_number == 1).sum()), "nós; linhas que os servem:", D[D.core_number == 1].linhas.value_counts().to_dict())

# --- k-truss (arestas em >= k-2 triângulos) ---
print("\n== k-truss ==")
for k in range(3, 6):
    T = nx.k_truss(und, k)
    print(f"{k}-truss: {T.number_of_nodes()} nós, {T.number_of_edges()} arestas", "->", [P.loc[n, "nome"] for n in T.nodes][:10])

D.to_csv("data/analise/p5_nucleos.csv")
# exporta para o Gephi (semana 5): atributos de núcleo no grafo original
H = nx.read_graphml("rede_v1.graphml")
for n in H.nodes: H.nodes[n]["core_number"] = int(core[n]); H.nodes[n]["onion_layer"] = int(onion[n])
nx.write_graphml(H, "rede_v1_nucleos.graphml")

# --- figuras ---
fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
ks = sorted(shell.index); ax[0].bar(ks, [shell[k] for k in ks], color="#2f7078"); ax[0].set_xlabel("core number (k-shell)"); ax[0].set_ylabel("nº de paradas"); ax[0].set_title("Tamanho de cada k-shell")
ax[1].scatter(D.core_number + np.random.default_rng(42).uniform(-.12, .12, len(D)), D.betweenness_dir, s=14, c=D.n_linhas, cmap="viridis"); ax[1].set_xlabel("core number"); ax[1].set_ylabel("betweenness"); ax[1].set_title("Núcleo x betweenness (cor = nº de linhas)")
ax[2].scatter(D.onion_layer, D.dano_remocao, s=14, color="#5d4fa0"); ax[2].set_xlabel("camada onion"); ax[2].set_ylabel("dano ao remover a parada"); ax[2].set_title("Camada onion x dano")
fig.tight_layout(); fig.savefig("figs/p5_nucleos.png", dpi=150)
