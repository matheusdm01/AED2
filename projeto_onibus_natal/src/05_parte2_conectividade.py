"""Parte 2 - Conectividade e distâncias: WCC/GCC/SCC, caminhos mínimos, diâmetro, eficiência, triângulos/clustering. (semana 4)"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, networkx as nx
from collections import Counter
from metricas import carregar, alcancabilidade, eficiencia_global

G = carregar(); P = pd.read_csv("data/paradas.csv").set_index("parada_id")
n = G.number_of_nodes(); und = G.to_undirected()

# --- componentes ---
wcc = list(nx.weakly_connected_components(G)); scc = sorted(nx.strongly_connected_components(G), key=len, reverse=True)
print("== componentes ==")
print("WCC:", len(wcc), "| tamanho da GCC (fraca):", len(max(wcc, key=len)))
tam = Counter(len(c) for c in scc)
print("SCC:", len(scc), "| tamanhos (tamanho: quantidade):", dict(sorted(tam.items(), reverse=True)))
print("maior SCC:", len(scc[0]), "nós ->", [P.loc[x, "nome"] for x in list(scc[0])[:6]])
print("SCC de tamanho 1:", tam[1], f"({tam[1] / n:.1%} dos nós)")
rows = [{"scc": i, "tamanho": len(c), "nos": "; ".join(P.loc[x, "nome"] for x in c)} for i, c in enumerate(scc) if len(c) > 1]
pd.DataFrame(rows).to_csv("data/analise/p2_scc_maiores_que_1.csv", index=False)

# condensação: o grafo de SCCs é um DAG? quantas fontes/sumidouros?
C = nx.condensation(G, scc)
print("condensação:", C.number_of_nodes(), "nós,", C.number_of_edges(), "arestas; é DAG:", nx.is_directed_acyclic_graph(C))

# --- alcançabilidade e distâncias (dirigidas, em nº de paradas/arestas) ---
R = alcancabilidade(G); total = n * (n - 1)
print("\n== alcançabilidade ==")
print(f"pares ordenados com caminho dirigido: {R} de {total} = {R / total:.2%}")
dists = []
for u, d in nx.all_pairs_shortest_path_length(G):
    dists += [x for v, x in d.items() if v != u]
s = pd.Series(dists)
print("distância (nº de arestas) entre pares alcançáveis: média", round(s.mean(), 2), "| mediana", s.median(), "| máx (diâmetro dirigido)", s.max())
print("eficiência global (dirigida):", round(eficiencia_global(G), 4))

# --- visão não dirigida (ignora o sentido; 'ida' e 'volta' ligam-se pelos nós compartilhados) ---
ud = []
for u, d in nx.all_pairs_shortest_path_length(und):
    ud += [x for v, x in d.items() if v != u]
su = pd.Series(ud)
print("\n== visão não dirigida (GCC = rede toda, WCC = 1) ==")
print("distância média:", round(su.mean(), 2), "| diâmetro:", su.max(), "| eficiência global:", round(eficiencia_global(und.to_directed()), 4))

# extremos do diâmetro (par mais distante, não dirigido)
best = max(((u, v, d) for u, dd in nx.all_pairs_shortest_path_length(und) for v, d in dd.items()), key=lambda t: t[2])
print("par mais distante (não dirigido):", P.loc[best[0], "nome"], "<->", P.loc[best[1], "nome"], "=", best[2], "arestas")

# --- triângulos e clustering ---
tri = nx.triangles(und); cl = nx.clustering(und)
print("\n== triângulos / clustering (não dirigido) ==")
print("triângulos:", sum(tri.values()) // 3, "| transitividade:", round(nx.transitivity(und), 4), "| clustering médio:", round(nx.average_clustering(und), 4))

# --- articulações e pontes (conectividade da rede não dirigida; antecipa a parte 4) ---
art = list(nx.articulation_points(und)); br = list(nx.bridges(und))
print("\n== articulações / pontes (não dirigido) ==")
print("pontos de articulação:", len(art), f"({len(art) / n:.0%} dos nós) | pontes:", len(br), f"({len(br) / und.number_of_edges():.0%} das arestas)")
pd.DataFrame({"parada_id": art, "nome": [P.loc[a, "nome"] for a in art], "linhas": [P.loc[a, "linhas"] for a in art],
              "n_linhas": [P.loc[a, "n_linhas"] for a in art]}).to_csv("data/analise/p2_articulacoes.csv", index=False)

pd.DataFrame({"metrica": ["nos", "arestas", "WCC", "SCC", "maior_SCC", "pares_alcancaveis_pct", "dist_media_dirigida", "diametro_dirigido",
                          "eficiencia_dirigida", "dist_media_nao_dirigida", "diametro_nao_dirigido", "eficiencia_nao_dirigida", "transitividade",
                          "pontos_articulacao", "pontes"],
              "valor": [n, G.number_of_edges(), len(wcc), len(scc), len(scc[0]), round(100 * R / total, 2), round(s.mean(), 2), int(s.max()),
                        round(eficiencia_global(G), 4), round(su.mean(), 2), int(su.max()), round(eficiencia_global(und.to_directed()), 4),
                        round(nx.transitivity(und), 4), len(art), len(br)]}).to_csv("data/analise/p2_resumo.csv", index=False)
