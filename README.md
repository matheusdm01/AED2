# Pontos críticos da rede de ônibus de Nova Parnamirim–Natal

## Integrantes

Matheus Dantas Melo  
Larissa Soares de Souza

## Vídeo

PREENCHER: https://youtu.be/... (até 15 min no total; não listado, nunca privado)

## Problema e pergunta

Quais paradas e trechos da rede das seis linhas que partem do Terminal de Nova Parnamirim, se bloqueados (por exemplo, por alagamento), mais prejudicam a operação, e o corredor da Av. Senador Salgado Filho é de fato o ponto crítico? Detalhes e definição de "dano" em [ANALISE_semana_05_10.md](ANALISE_semana_05_10.md) (parte 0).

## Dados

- **Fonte:** PDFs "Linhas e Itinerários" da Viação Cidade das Dunas, linhas 97, 98, 738, 740, 745.1 e 745.2, na pasta `pdfs/`.
- **Como obter:** os PDFs já estão no repositório; `src/01_extrair.py` lê as tabelas e grava `data/paradas_raw.csv` (448 registros).
- **Limpeza:** padronização de nomes, identificação de paradas por nome + endereço, equivalências manuais de endereço, auditoria em `data/auditoria_nomes.csv`. Detalhes em [MODELAGEM.md](MODELAGEM.md).

## Modelagem

PREENCHER com o resumo de [MODELAGEM.md](MODELAGEM.md): nó = parada; aresta A → B se B vem logo após A em algum itinerário; dirigida; peso = número de linhas no trecho; ida e volta como nós distintos (e as variantes v2 e v3 como alternativa); fica de fora: horários, demanda, distâncias, outras empresas.

## Conteúdo do curso utilizado

| conceito | semana | onde aparece | para que serviu |
|---|---|---|---|
| matriz de adjacência, densidade | 2 | `src/04_parte1_descricao.py` | descrever a rede (esparsa, 0,56%) |
| grau de entrada e saída, distribuição de grau | 2, 3 | `src/04_parte1_descricao.py` | mostrar que a rede é feita de cadeias e achar entroncamentos |
| sub-redes por linha | 2 | `src/04_parte1_descricao.py` | medir o compartilhamento entre linhas |
| componentes WCC e SCC | 4 | `src/05_parte2_conectividade.py` | separar ida e volta, medir fragmentação |
| caminhos mínimos, diâmetro, eficiência | 4 | `src/05_parte2_conectividade.py`, `src/metricas.py` | alcançabilidade e base do dano |
| triângulos e clustering | 4 | `src/05_parte2_conectividade.py` | mostrar que não há estrutura local densa |
| closeness, betweenness, eigenvector | 4 | `src/06_parte3_centralidades.py` | achar o corredor crítico e comparar hubs e pontes |
| remoção de nós e arestas, robustez e ataques à rede | 3, 4 | `src/07_parte4_remocao.py`, `src/metricas.py` | medir o dano de cada parada, trecho e grupo (alagamento) |
| k-core, k-shell, core number, degeneracy, onion layers, k-truss | 5 | `src/08_parte5_nucleos.py` | testar se o núcleo coincide com o corredor crítico |
| redes bipartidas, matriz de incidência, projeção, Jaccard | 6 | `src/09_parte6_alternativas.py` | comparar linhas e achar o corredor sem usar a ordem das paradas |
| modelagens alternativas (ida/volta fundidas, terminais unificados) | 2, 6 | `src/variantes.py`, `src/09_parte6_alternativas.py` | testar se as conclusões dependem da modelagem |

## Como executar

Requer Python 3.12. Em uma máquina limpa, **um comando** cria o ambiente virtual, instala as dependências fixadas (`requirements.txt`) e reproduz tudo (cerca de 1 min 30 s):

```bash
./run_all.sh
```

Sem bash (Windows, por exemplo), com as dependências já instaladas (`pip install -r requirements.txt`):

```bash
python reproduzir.py
```

Saídas: tabelas em `data/` e `data/analise/`, **todas as figuras em `figs/` (geradas pelo código)**, grafos `rede_v1.graphml`, `rede_v1_nucleos.graphml`, `rede_v2.graphml` e `rede_v3.graphml` (abrem no Gephi) e o log completo em `data/analise/log_execucao.txt`. Os sorteios usam semente fixa (42), então duas execuções geram tabelas idênticas.

## Estrutura do repositório

```
pdfs/                 itinerários originais (fonte dos dados)
src/                  01_extrair ... 09_parte6_alternativas, metricas.py, variantes.py
data/                 dados extraídos e limpos (paradas, arestas, itinerários, incidência)
data/analise/         tabelas de cada parte da análise e o log de execução
figs/                 figuras geradas pelo código
reproduzir.py         orquestrador (roda todas as etapas em ordem)
run_all.sh            ambiente virtual + dependências + reproduzir.py
MODELAGEM.md          decisões de modelagem e limpeza
ANALISE_semana_05_10.md   resultados e interpretação das partes 0 a 6
```

## Resultados

PREENCHER com a síntese de [ANALISE_semana_05_10.md](ANALISE_semana_05_10.md) quando as partes 7 e 8 estiverem prontas (figuras finais e interpretação).

## Limitações e próximos passos

PREENCHER (ver o fim de [ANALISE_semana_05_10.md](ANALISE_semana_05_10.md)).

## Referências

PREENCHER
