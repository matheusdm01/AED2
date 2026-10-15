"""Modelagens alternativas da rede (parte 6).
  v1: original (ida e volta separadas; um nó = nome + endereço)
  v2: ida e volta fundidas por local (mesmo nome limpo e mesma via normalizada = mesmo nó)
  v3: v2 + todos os 'terminais' unificados em um só nó
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, networkx as nx
from metricas import normaliza_via

TERMINAIS = {"TERMINAL", "TERMINAL DE NOVA PARNAMIRIM"}

def chaves(variante, P):
    if variante == "v1":
        return {i: i for i in P.index}
    k = {i: f"{P.loc[i, 'nome']} | {normaliza_via(P.loc[i, 'via'])}" for i in P.index}
    if variante == "v3":
        k = {i: ("TERMINAL (unificado)" if P.loc[i, "nome"] in TERMINAIS else v) for i, v in k.items()}
    return k

def montar(variante, IT, P):
    """devolve (grafo dirigido ponderado, dict parada_id -> nó da variante)"""
    k = chaves(variante, P)
    arestas = {}
    for linha, g in IT.groupby("linha"):
        seq = [k[i] for i in g.sort_values("ordem").parada_id]
        for a, b in zip(seq, seq[1:]):
            if a != b: arestas.setdefault((a, b), set()).add(linha)
    G = nx.DiGraph()
    for pid, no in k.items(): G.add_node(no, nome=P.loc[pid, "nome"], via=normaliza_via(P.loc[pid, "via"]))
    for (a, b), ls in arestas.items(): G.add_edge(a, b, weight=len(ls), linhas=",".join(sorted(ls)))
    return G, k
