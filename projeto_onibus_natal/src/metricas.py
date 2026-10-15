"""Funções compartilhadas pelas etapas de análise (partes 0 a 3 em diante).

Definições da parte 0 (ver ANALISE_semana_05_10.md):
  alcancabilidade R(H)  = nº de pares ordenados (u, v), u != v, com caminho dirigido u -> v em H
  eficiencia global E(H)= média de 1/d(u, v) sobre todos os pares ordenados de H (1/d = 0 se não há caminho)
  dano(S)               = 1 - R(G - S) / R0, onde R0 é o nº de pares conectados em G
                          cujos dois extremos NÃO estão em S (assim a perda trivial dos
                          extremos removidos não conta como dano)
"""
import networkx as nx

def carregar(path="rede_v1.graphml"):
    return nx.read_graphml(path)

def pares_alcancaveis(G):
    """conjunto de pares (u, v), u != v, com caminho dirigido u -> v"""
    out = set()
    for u in G:
        for v in nx.descendants(G, u):
            out.add((u, v))
    return out

def alcancabilidade(G):
    return sum(len(nx.descendants(G, u)) for u in G)

def eficiencia_global(G):
    n = G.number_of_nodes()
    if n < 2:
        return 0.0
    s = 0.0
    for u, dist in nx.all_pairs_shortest_path_length(G):
        s += sum(1.0 / d for v, d in dist.items() if v != u)
    return s / (n * (n - 1))

def dano(G, S, base_pairs=None):
    """dano estrutural da remoção do conjunto de nós S (ver docstring do módulo)"""
    S = set(S)
    if base_pairs is None:
        base_pairs = pares_alcancaveis(G)
    r0 = sum(1 for (u, v) in base_pairs if u not in S and v not in S)
    H = G.copy(); H.remove_nodes_from(S)
    r1 = alcancabilidade(H)
    return 1 - r1 / r0 if r0 else 0.0


# ---------------------------------------------------------------------------
# Versão rápida (matrizes esparsas): usada nas simulações de remoção (parte 4 em diante).
# Calcula as mesmas quantidades das funções acima, mas com scipy.sparse.csgraph.
# ---------------------------------------------------------------------------
import re, unicodedata
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path, connected_components

def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")

def normaliza_via(s):
    """'Av. Sen. Salgado Filho' e 'Avenida Senador Salgado Filho' -> 'av sen salgado filho'"""
    s = sem_acento(s).lower()
    s = re.sub(r"[.,]", " ", s)
    s = re.sub(r"\b(avenida|av)\b", "av", s)
    s = re.sub(r"\b(rua|r)\b", "rua", s)
    s = re.sub(r"\b(senador|sen)\b", "sen", s)
    s = re.sub(r"\b(engenheiro|eng)\b", "eng", s)
    return re.sub(r"\s+", " ", s).strip()

def normaliza_bairro(s):
    return re.sub(r"\s+", " ", sem_acento(s).lower()).strip()


class Avaliador:
    """Avalia o dano estrutural da remoção de nós ou arestas (definição da parte 0)."""

    def __init__(self, G):
        self.nodes = list(G.nodes)
        self.idx = {n: i for i, n in enumerate(self.nodes)}
        n = len(self.nodes)
        self.A = np.zeros((n, n), dtype=np.int8)
        for u, v in G.edges():
            self.A[self.idx[u], self.idx[v]] = 1
        D0 = self._dist(self.A)
        self.D0 = D0
        self.reach0 = np.isfinite(D0) & ~np.eye(n, dtype=bool)
        self.inv0 = np.where(self.reach0, 1.0 / np.where(D0 > 0, D0, 1), 0.0)

    @staticmethod
    def _dist(A):
        return shortest_path(csr_matrix(A), directed=True, unweighted=True)

    def _medir(self, A_sub, keep):
        k = int(keep.sum())
        D = self._dist(A_sub)
        reach = np.isfinite(D) & ~np.eye(k, dtype=bool)
        inv = np.where(reach, 1.0 / np.where(D > 0, D, 1), 0.0)
        ix = np.ix_(keep, keep)
        r0 = int(self.reach0[ix].sum()); e0 = self.inv0[ix].sum()
        r1 = int(reach.sum()); e1 = inv.sum()
        ncomp, lab = connected_components(csr_matrix(A_sub), directed=True, connection="weak")
        gcc = np.bincount(lab).max() / k if k else 0.0
        return {"dano": 1 - r1 / r0 if r0 else 0.0,
                "perda_eficiencia": 1 - e1 / e0 if e0 else 0.0,
                "alcancabilidade_restante": r1 / int(self.reach0.sum()),
                "n_wcc": int(ncomp), "gcc_frac": float(gcc)}

    def remover_nos(self, S):
        keep = np.ones(len(self.nodes), dtype=bool)
        for n in S: keep[self.idx[n]] = False
        return self._medir(self.A[np.ix_(keep, keep)], keep)

    def remover_arestas(self, edges):
        A = self.A.copy()
        for u, v in edges: A[self.idx[u], self.idx[v]] = 0
        return self._medir(A, np.ones(len(self.nodes), dtype=bool))
