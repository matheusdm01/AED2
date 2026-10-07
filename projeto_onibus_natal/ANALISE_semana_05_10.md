# Análise (semana de 05/10): partes 0 a 8

Todos os números abaixo vêm de `rede_v1.graphml` e podem ser reproduzidos com `./run_all.sh`. As tabelas completas estão em `data/analise/`.

## Parte 0. Pergunta e definição de dano

**Pergunta (proposta, pode ser ajustada):** quais paradas e trechos da rede das seis linhas que partem de Nova Parnamirim, se bloqueados (por exemplo, por alagamento), mais prejudicam a operação, e o corredor da Av. Senador Salgado Filho é de fato o ponto crítico?

**Quem se beneficia:** quem planeja a operação da empresa (desvios, linhas de reserva) e os usuários que dependem dessas linhas.

**Por que depende da estrutura:** o bloqueio de um ponto só pesa na proporção em que outras rotas faltam, e isso é propriedade da rede (caminhos, componentes, sobreposição de linhas).

**Medidas de dano** (funções em `src/metricas.py`):

1. **Alcançabilidade** R(H): número de pares ordenados (A, B) com caminho dirigido de A a B.
2. **Dano de uma remoção S** = 1 − R(G−S) / R0, onde R0 conta só os pares que já eram conectados em G e cujos dois extremos não estão em S. Assim a perda trivial dos nós removidos não conta como dano.
3. **Eficiência global** (média de 1/distância sobre todos os pares), como medida complementar de alongamento de caminhos.

Distância aqui é o **número de arestas** (paradas). O peso (número de linhas) não é distância; ele mede redundância.

## Parte 1. Descrição da rede (semanas 2 e 3)

- 202 nós e 227 arestas dirigidas. Densidade 0,0056. A matriz de adjacência (202 × 202) tem 0,56% das entradas não nulas; a soma das linhas bate com o grau de saída e o traço é zero (sem laços).
- Grau de entrada e de saída têm média 1,12 e quase todos os nós têm grau 1 nos dois (175 e 176 de 202): a rede é feita de longas cadeias. Grau total: 162 nós com 2, 26 com 3, 10 com 4 e 2 com 5. Os dois de grau 5 são a Estação Carrefour e o Grupo Conrado.
- Fontes (grau de entrada 0): Terminal de Nova Parnamirim e "Terminal" (da 745.2). Único sumidouro: Igreja Guerreiros da Oração (fim da 745.1).
- Reciprocidade 0: nenhum trecho existe nos dois sentidos, porque ida e volta usam nós diferentes (decisão de modelagem do `MODELAGEM.md`).
- Pesos das arestas: 90 de peso 1, 96 de 2, 18 de 3, 9 de 4 e 14 de 5.
- Sub-redes por linha: a 738 tem 100% das paradas compartilhadas com outras linhas, a 740 98,8%, a 97 94,0% e a 98 94,4%; a 745.1 tem 59,2% e a 745.2 só 40,7%. As circulares da Ponta Negra são as mais independentes.

## Parte 2. Conectividade e distâncias (semana 4)

- **Uma componente fraca** (WCC = 1): a rede toda é conexa se ignorarmos o sentido.
- **79 componentes fortes (SCC):** uma gigante com 124 nós e 78 componentes de um só nó (38,6% das paradas). A condensação é um DAG, como esperado. Esses nós isolados provavelmente são trechos percorridos em um só sentido (a conferir na parte 6, quando ida e volta forem fundidas).
- **Alcançabilidade:** 66,24% dos pares ordenados têm caminho dirigido (26.896 de 40.602).
- **Distâncias (pares alcançáveis):** média 25,3 arestas, mediana 25, diâmetro dirigido 64. Na versão não dirigida: média 18,6 e diâmetro 51.
- **Eficiência global:** 0,045 (dirigida) e 0,091 (não dirigida).
- **Triângulos e clustering:** 7 triângulos, transitividade 0,066 e clustering médio 0,043. A rede é quase uma árvore de cadeias, sem estrutura de bairro triangulada.
- **Pontos de articulação:** 47 (23% dos nós) e 46 pontes (20% das arestas) na versão não dirigida. Isso já antecipa a parte 4: muitos pontos, se removidos, desconectam a rede.

**Cuidado de interpretação:** o par mais distante da rede (51 arestas) é "Terminal de Nova Parnamirim" ↔ "Terminal". É consequência de tratá-los como nós diferentes. Se forem o mesmo local físico, o diâmetro e a eficiência mudam, e isso deve ser testado na parte 6.

## Parte 3. Centralidades (semana 4)

Medidas calculadas: grau e força, closeness (dirigida e não dirigida), betweenness (dirigida e não dirigida, de nós e de trechos) e eigenvector (só não dirigido, porque no grafo dirigido o autovetor se concentra na SCC gigante e zera o resto).

- **Betweenness (dirigida), top 3:** Estação Via Direta (0,373), Estação Carrefour (0,313) e Kero Kero (0,287). Seguem, quase empatados em ~0,28, todos os nós do corredor Kero Kero → Açaí → Atacadão → Motel Vision → Sam's Club → Passarela de Néopolis → Hyundai → PG Prime.
- **Betweenness dos trechos:** os 8 primeiros são todos de peso 5 e todos nesse mesmo corredor, na ida, entre Kero Kero e Via Direta. Na volta (Carrefour → Antiga Salinas), o valor cai para 0,22. Hipótese a testar na parte 4: o sentido de ida é mais crítico que o de volta.
- **Valores quase iguais no corredor** acontecem porque as paradas são consecutivas numa cadeia: todo caminho que usa uma usa as outras. Ou seja, a betweenness identifica o **corredor**, e não uma parada específica dentro dele.
- **Eigenvector:** o topo é Sam's Club, Passarela de Néopolis, Motel Vision e Hyundai, de novo o meio do corredor.
- **Hubs não são pontes.** O grau tem correlação baixa com as outras medidas (Spearman 0,21 com betweenness e 0,24 com closeness). Grupo Conrado tem grau 5, mas só 3 linhas. Dos 21 nós de maior betweenness (10%), 15 têm grau 2: são paradas de passagem, não de entroncamento. Por outro lado, os 12 nós de grau ≥ 4 têm betweenness mediano de 0,166, contra 0,050 na rede toda.
- **Betweenness e eigenvector concordam** (17 dos 20 primeiros em comum), e a closeness reparte o topo entre o corredor e paradas de Capim Macio (Cidade Jardim e Santander), servidas só pela 745.1.
- **Ponderar pelo número de linhas** (custo = 1/peso) quase não muda o ranking (Spearman 0,99 com a versão sem peso).

## Parte 4. Teste de remoção (semanas 3 e 4)

Figuras: `figs/p4_dano_paradas.png`, `figs/p4_grupos.png`, `figs/p4_curvas_ataque.png`. Tabelas: `data/analise/p4_*.csv`.

**Uma parada.** Remover a Estação Via Direta destrói 56,4% dos pares conectados (a rede se parte em 2 componentes fracas, a maior com 87% das paradas). A Estação Carrefour vem com 47,4%, e as paradas do corredor Kero Kero → PG Prime ficam entre 42,4% e 43,4%. Também aparecem Espaço Reduzido (35,7%, parada da Abel Cabral usada por 3 linhas, logo antes do corredor) e Antiga Salinas (33,5%). O dano mediano é 5,6%; 190 das 202 paradas causam algum dano e 47 dividem a rede em mais de uma componente. A betweenness prevê bem o dano (Spearman 0,75), o grau não (0,17) e o número de linhas prevê parcialmente (0,41). O dano médio por número de linhas que passam pela parada cresce rápido: 5,3% (1 linha), 5,1% (2), 7,9% (3), 24,6% (4), 34,0% (5) e 51,9% (6).

**Um trecho.** Os oito trechos mais danosos são todos de peso 5 e formam a ida do corredor, de Kero Kero até a Estação Via Direta (dano de 42,4% a 43,4%). Na volta, o trecho Carrefour → Antiga Salinas causa 33,8%. O dano médio por peso é 4,4% (peso 1), 5,2% (2), 5,7% (3), 28,9% (4) e 38,9% (5).

**Grupos (alagamento de uma região).** Remover as 16 paradas do tronco (trechos com 5 ou mais linhas) causa 74,9% de dano e divide a rede em 5 componentes, com a maior retendo 41,9% das paradas. A via Av. Senador Salgado Filho inteira (24 paradas) causa 81,2% e o bairro Lagoa Nova (21), 75,9%. Os dois sentidos do tronco, separados, causam 56,8% (ida, 9 paradas) e 46,2% (volta, 7 paradas).

Para saber se isso é especial ou só efeito de tamanho, comparei com duas referências de 500 sorteios cada (sementes fixas):

- **Janelas contíguas** de mesmo tamanho dentro de um itinerário, que imitam um alagamento num trecho de rua. O tronco completo supera 96,4% delas (a média das janelas é 43,5%); a via Salgado Filho, 92,8%; Lagoa Nova, 94,6%.
- **Paradas aleatórias** do mesmo tamanho. Aqui o tronco fica no percentil 33,4: removidas ao acaso, 16 paradas espalhadas cortam as cadeias em vários pontos e causam, em média, 77% de dano.

Leitura: o corredor é pior que bloquear um trecho contíguo qualquer, mas não pior que cortar a rede em muitos pontos. Como um alagamento atinge vizinhança, a referência adequada é a das janelas contíguas. Em contraste, a Av. Abel Cabral (24 paradas, 50,8%) fica no percentil 25 e não se destaca. Para grupos muito grandes (bairro Nova Parnamirim, 56 paradas) a janela deixa de ser comparável, porque cobre mais da metade de uma linha.

**Ataques progressivos** (alcançabilidade restante após remover k paradas):

| estratégia | k = 5 | k = 10 | k = 20 |
|---|---|---|---|
| betweenness (estático) | 21,6% | 21,5% | 12,1% |
| betweenness (adaptativo) | 11,9% | 5,2% | 2,4% |
| grau (estático) | 19,3% | 9,4% | 4,2% |
| aleatório (média de 100) | 59,4% | 34,5% | 13,8% |

A betweenness estática estagna entre k = 5 e 10 porque as paradas seguintes da lista são consecutivas na mesma cadeia e removê-las acrescenta pouco. O ataque adaptativo recalcula a cada remoção e acerta pontos diferentes: Via Direta, Carrefour, Igreja Evangélica Cristã, CIA, Grupo Conrado, DIVEP, Kero Kero, MID e outros.

## Parte 5. Núcleos (semana 5)

Figura: `figs/p5_nucleos.png`. Tabela: `data/analise/p5_nucleos.csv`. Grafo para o Gephi com os atributos: `rede_v1_nucleos.graphml`.

- **Degeneracy = 2.** O 2-core tem 156 nós (77%) e o 1-shell, 46. Os 46 nós do 1-shell são ramos pendentes servidos só pelas circulares 745.2 (26 paradas) e 745.1 (20), na Ponta Negra, Capim Macio e UFRN. Há 30 camadas onion.
- **O núcleo não isola o corredor.** As 16 paradas do tronco estão todas no 2-core, mas representam só 10% dele. A correlação do core number com o dano de remoção é −0,06 e com a betweenness, 0,18. A camada onion mais profunda é Espaço Reduzido, Atacadão e DIVEP (região Abel Cabral / Nova Parnamirim), não a Salgado Filho.
- **O que o núcleo mede aqui** é periferia versus centro: o core number tem correlação 0,68 com o número de linhas, e a camada onion, 0,77 com o grau.
- **k-truss:** o 3-truss tem 19 nós e 20 arestas (terminais, Condomínio Itatiaia, CEPE, Carrefour, entre outros) e o 4-truss é vazio, coerente com os 7 triângulos da parte 2.

Lição para o projeto: o corredor é crítico pela **posição** (betweenness e remoção), não pela **densidade**. A decomposição em núcleos é a ferramenta errada para esta pergunta, e isso vale como resultado, porque justifica a escolha das outras.

## Parte 6. Modelagens alternativas (semana 6)

Figura: `figs/p6_alternativas.png`. Grafos: `rede_v2.graphml` e `rede_v3.graphml`. Tabelas: `data/analise/p6_*.csv`.

**Variantes.** v1 é a original. A v2 funde ida e volta quando o nome limpo e a via normalizada coincidem (10 locais, 21 paradas da v1, lista em `p6_fusoes_v2.csv`). A v3 soma a unificação dos terminais. Os conjuntos "tronco" e "corredor" são os mesmos da v1, mapeados em cada variante, para o dano ser comparável.

| | v1 | v2 | v3 |
|---|---|---|---|
| nós / arestas | 202 / 227 | 191 / 225 | 190 / 223 |
| SCC / maior SCC | 79 / 124 | 13 / 179 | 12 / 179 |
| pares alcançáveis | 66,2% | 93,9% | 94,4% |
| eficiência | 0,0448 | 0,0619 | 0,0620 |
| 1ª betweenness | Via Direta (0,37) | Atacadão (0,57) | Atacadão (0,57) |
| dano ao remover o tronco | 74,9% | 68,9% | 69,1% |
| dano ao remover o corredor Salgado Filho | 80,4% | 69,0% | 69,2% |
| maior dano de uma só parada | 56,4% | 41,6% | 41,8% |

**O que resiste e o que não resiste à modelagem:**

- **Resiste:** o corredor continua sendo o ponto crítico. Removê-lo causa de 69% a 80% de dano em qualquer variante. A distância média e o diâmetro quase não mudam.
- **Não resiste:** a alcançabilidade absoluta (66% contra 94%) e o número de componentes fortes dependem de tratar ida e volta como nós separados; esses números não devem ser lidos como propriedade da cidade. O ranking de paradas individuais também muda: Spearman 0,78 entre v1 e v2, e o primeiro lugar passa de Estação Via Direta para Atacadão. Na v2, Atacadão vira nó de passagem entre ida e volta (artefato da regra de fusão, que trata os dois lados da avenida como a mesma parada).

**Rede bipartida linha × parada (v1).** 6 linhas, 202 paradas, 448 arestas, densidade bipartida 0,370. Pelo Jaccard, as linhas mais parecidas são 738–740 (0,53), 738–98 (0,49) e 97–98 (0,47); a 745.2 é a mais isolada (0,03 a 0,14 com as demais). Os valores praticamente não mudam na v2 (diferença máxima de 0,06). Os conjuntos de linhas por parada mostram a estrutura: 745.2 sozinha (32 paradas), 738+98 (26, "via Alecrim"), 740+97 (23, "via Praça"), 745.1 sozinha (20), 97+98 (19) e 738+740+745.1 (14, Maria Lacerda). Na projeção sobre paradas, o esqueleto de pares com 5 ou mais linhas em comum tem 18 paradas e 1 componente, e 16 delas são exatamente o tronco encontrado pela ordem das paradas. Duas ferramentas independentes apontam o mesmo corredor.

## Parte 7. Figuras finais (geradas por `src/10_parte7_figuras.py`)

| figura | o que mostra | uso sugerido |
|---|---|---|
| `figs/f1_rede_dano.png` | a rede inteira com cada parada colorida pelo dano de sua remoção e o tronco em destaque | abertura do resultado no vídeo e no README |
| `figs/f2_modelagem_exemplo.png` | trecho real do corredor (ida) com nó, aresta dirigida, peso e linhas | explicar a modelagem (minutos 2 a 5 do vídeo) |
| `figs/f3_resumo_resultados.png` | painel com (a) as 10 paradas mais críticas, (b) o tronco contra 500 trechos contíguos, (c) ataques progressivos, (d) robustez à modelagem | síntese da resposta |
| `figs/f4_assinaturas_linhas.png` | combinações de linhas que compartilham cada parada | mostrar a estrutura "via Alecrim" e "via Praça" |

Além dessas, as figuras de cada parte (`p1_`, `p4_`, `p5_`, `p6_`) servem de apoio na seção de análise.

## Parte 8. Interpretação e limitações

### Resposta à pergunta

**Quais paradas e trechos mais prejudicam a operação se bloqueados, e o corredor da Salgado Filho é o ponto crítico?** Sim, do ponto de vista estrutural.

1. **O corredor é o ponto crítico.** Os trechos do eixo Kero Kero → Estação Via Direta (ida) e Estação Carrefour → Atacadão (volta) são usados por 5 das 6 linhas. Bloquear essas 16 paradas elimina 75% dos pares de paradas antes conectados e divide a rede em 5 componentes, com a maior retendo 42% das paradas. O resultado é mais forte que o de um trecho contíguo qualquer de mesmo tamanho (percentil 95 a 96 nos sorteios) e se mantém quando o corte do tronco muda: com o limiar de 3, 4 ou 5 linhas por trecho o dano é de 90%, 80% e 75% (percentil de 100, 92 e 95; `p8_sensibilidade_limiar.csv`).
2. **Dentro do corredor, o que pesa é o trecho, não a parada.** As paradas do corredor têm dano quase igual (42% a 43%), porque são consecutivas numa cadeia: cortar qualquer uma interrompe o mesmo fluxo. As duas estações do Natal Shopping se destacam (56% e 47%) por ficarem onde as seis linhas se encontram.
3. **A ida pesa mais que a volta.** O tronco da ida causa 56,8% de dano; o da volta, 46,2%. O trecho mais danoso individual (43,4%) está na ida.
4. **Grau não é criticidade.** O grau quase não prevê o dano de uma parada (Spearman 0,17), a betweenness prevê bem (0,75). Ou seja, "parada com mais ligações" não é o critério certo; a posição na rede é.
5. **A concentração de risco é o achado de planejamento:** cinco linhas dependem do mesmo eixo, enquanto a 745.2 compartilha só 41% de suas paradas com as demais. Uma rota alternativa pré-definida para esse eixo (principalmente no sentido de ida) seria a medida de maior efeito esperado. Isso é uma hipótese a validar com demanda, porque a rede só mostra topologia.

### O que NÃO se sustenta (e deve ser dito no vídeo)

- O nível absoluto de conectividade (66% dos pares alcançáveis) é consequência de tratar ida e volta como nós distintos; na v2 e v3 é 94%.
- O ranking de paradas individuais muda com a modelagem (Spearman 0,78 entre v1 e v2; o primeiro lugar passa de Estação Via Direta para Atacadão).
- A decomposição em núcleos não identifica o corredor (degeneracy 2).

### Limitações e artefatos

- **Só topologia.** Sem demanda, horários, frequência, tempo ou distância, "crítico" significa estrutural. Um trecho com poucos passageiros pesa igual a um lotado.
- **Recorte da rede.** São seis linhas de uma empresa, a partir de um terminal. Sem as demais linhas e vias de Natal, o corredor parece mais insubstituível do que seria na cidade real (efeito de fronteira). Como o recorte é definido pelo terminal, não pode ser lido como amostra da cidade.
- **Significado de "bloqueio".** Remover um nó supõe que o ônibus não passa por ali. Se só a parada fosse interditada, o ônibus poderia seguir sem parar; e os passageiros não têm desvio a pé nem baldeação entre paradas próximas no modelo.
- **Modelagem de ida e volta e dos terminais** (ver tabela da parte 6): afeta SCC, alcançabilidade, diâmetro e ranking individual.
- **Qualidade dos dados.** Os PDFs têm salto de numeração (745.1), itinerário terminando fora do terminal (738), nomes repetidos em ruas diferentes, endereços genéricos e grafias diferentes para o mesmo local. A limpeza usa regras e três equivalências manuais; a v2 funde por nome e via e pode juntar paradas distintas.
- **Distância em número de paradas**, não em quilômetros; sem coordenadas ou geocodificação.
- **Estatística dos sorteios:** 500 repetições por grupo e semente fixa; os percentis têm margem de poucos pontos (o tronco aparece no percentil 96,4 na parte 4 e 95,0 na parte 7, por sequências de sorteio diferentes).
- **Sem validação externa:** não há dados de alagamentos reais para confrontar o modelo.

### Próximos passos

1. Geocodificar as paradas e usar distâncias e tempos reais nas arestas.
2. Obter demanda (bilhetagem) para ponderar o dano por passageiros.
3. Incluir as demais linhas de Natal (ex.: GTFS), para medir se existe desvio real do corredor.
4. Confrontar o ranking com pontos de alagamento conhecidos da cidade.
5. Modelar horários (rede temporal ou multicamada) e a baldeação entre paradas próximas.

## Linhas para a tabela do README ("conteúdo do curso utilizado")

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

