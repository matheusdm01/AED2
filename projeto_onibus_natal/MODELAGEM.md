# Modelagem da rede (versão 1)

Rascunho da seção "Modelagem" do README. Fonte: PDFs "Linhas e Itinerários" da Viação Cidade das Dunas (linhas 97, 98, 738, 740, 745.1 e 745.2), pasta `pdfs/`.

## 1. Escopo: as seis linhas juntas

Usar as seis linhas em uma única rede. Uma linha isolada é quase um caminho (cada parada só se liga à seguinte), e nesse caso toda medida de centralidade sai trivial. A análise só faz sentido onde as linhas se sobrepõem e compartilham trechos. Nas seis linhas, 55 das 202 paradas são usadas por 3 ou mais linhas e 2 paradas (Estação Via Direta e Estação Carrefour) são usadas pelas seis.

## 2. Modelo principal (espaço L): rede de paradas dirigida e ponderada

| elemento | definição |
|---|---|
| nó | uma parada, identificada por (nome limpo, endereço normalizado) |
| aresta A → B | B aparece logo depois de A no itinerário de pelo menos uma linha |
| direção | sim; os itinerários têm sentido (ida e volta) |
| peso | número de linhas distintas que fazem o trecho A → B |
| atributos do nó | via, bairro (extraído do texto do endereço), número e lista de linhas |

**Fica de fora:** horários, frequência, demanda, tempo de viagem, distância, conexões a pé entre paradas próximas, outras empresas, e os pontos entre duas paradas listadas.

## 3. Modelo complementar (rede bipartida linha × parada)

Matriz de incidência em `data/incidencia_linha_parada.csv` (6 × 202). Serve para a projeção (semana 6): duas paradas se ligam se compartilham linhas, ou duas linhas se ligam se compartilham paradas. É a segunda alternativa de modelagem a discutir no README.

## 4. Decisões de limpeza (tudo reproduzível em `src/02_limpar_e_construir.py`)

- Extração das tabelas com `pdfplumber` (448 registros, ordem e número de sequência preservados).
- Nome limpo: caixa alta, sem acento, sem prefixos "PARADA", "PARDA" (erro de digitação) e "EM FRENTE A", sem sufixos IDA/VOLTA e sem ponto final. 206 nomes brutos viraram 186 nomes limpos.
- Nome sozinho não identifica parada: "ESPAÇO REDUZIDO" existe na Abel Cabral e no Tirol, "NORDESTÃO" na Maria Lacerda e na Salgado Filho, "EXTRA" na Maria Lacerda e na Roberto Freire. Por isso o identificador é nome + endereço.
- O mesmo endereço aparece escrito de formas diferentes entre PDFs; três equivalências foram resolvidas à mão (Kero Kero na Salgado Filho, CEPE na Ayrton Senna, Nordestão na Maria Lacerda). A tabela de auditoria com todos os nomes que geraram mais de um nó está em `data/auditoria_nomes.csv`.
- "PRAIA SHOPPING" na 745.1 tem endereço genérico (sem número) e foi mantido separado por linha, por causa do sentido oposto.
- Nenhum laço (A → A) e nenhuma aresta duplicada; o peso conta linhas, não passagens.

## 5. Resultado da versão 1

202 nós, 227 arestas, densidade 0,0056, uma única componente fraca (WCC = 1) e 79 componentes fortes (SCC). Pesos de aresta: 90 arestas com peso 1, 96 com peso 2, 18 com 3, 9 com 4 e 14 com 5.

Os 14 trechos de peso 5 formam o corredor da Av. Senador Salgado Filho: na ida, de Kero Kero até a Estação Via Direta; na volta, da Estação Carrefour até o Atacadão. Nenhuma aresta tem peso 6. As centralidades de intermediação mais altas na primeira sondagem caem nesse corredor e nas duas paradas do Natal Shopping. O resultado é esperado; a análise de verdade ainda vem.

## 6. Problemas conhecidos (para tratar ou declarar como limitação)

1. **Ida e volta são nós diferentes.** Paradas em lados opostos da avenida só se fundem quando têm o mesmo nome e endereço. Por isso a rede tem 79 componentes fortes e diâmetro grande. Alternativa a testar: fundir ida e volta por local e comparar as medidas.
2. **Três "terminais".** "Terminal de Nova Parnamirim" (Rua Cupuaçu) é a origem de cinco linhas, mas a 745.2 usa "TERMINAL" na Av. Gastão Mariz de Faria, e as linhas 738 e 740 têm "Terminal ida" e "Terminal volta" no mesmo trecho. Não sei se é o mesmo local físico; mantive separados e sinalizei.
3. **Numeração com salto** na 745.1 (falta o número 29, entre Estação Via Direta e PN329). Só afeta uma aresta, também presente na 745.2 sem salto.
4. **Linha 738** termina em "Em frente a Kero Kero" depois de "Terminal volta", o que parece erro do cadastro. Não há aresta de fechamento do circuito nas linhas circulares.
5. **Só topologia.** Sem coordenadas, horários ou demanda, "ponto crítico" aqui significa estrutural, e a resposta precisa dizer isso.
6. **Bairro por expressão regular** sobre o texto do endereço, sem geocodificação.

## 7. Próximos passos (semana de 05/10: análise com as ferramentas do curso)

| ferramenta (semana) | uso no problema |
|---|---|
| grau de entrada e saída, matriz de adjacência (2, 3) | quais paradas concentram trechos |
| BFS/DFS e caminhos mínimos, diâmetro, eficiência (3, 4) | efeito de remover um nó ou trecho sobre distâncias |
| componentes WCC, GCC, SCC (4) | fragmentação após bloqueios |
| betweenness, closeness (4) | trechos de passagem obrigatória |
| k-core, k-shell, onion layers (5) | núcleo do corredor da Salgado Filho |
| bipartida, projeção, Jaccard (6) | similaridade entre linhas e entre paradas |
