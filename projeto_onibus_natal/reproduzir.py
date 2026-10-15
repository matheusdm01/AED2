"""Reproduz TODO o projeto do zero: PDFs -> dados limpos -> rede -> análise -> figuras.
Uso:  python reproduzir.py      (ou ./run_all.sh, que cria o ambiente virtual antes)
Saídas: data/, data/analise/, figs/, rede_*.graphml e o log completo em data/analise/log_execucao.txt"""
import os, subprocess, sys, time

RAIZ = os.path.dirname(os.path.abspath(__file__)); os.chdir(RAIZ)
for pasta in ("data", "data/analise", "figs"):
    os.makedirs(pasta, exist_ok=True)

ETAPAS = [
    ("coleta: extrai as tabelas dos PDFs",             ["src/01_extrair.py", "pdfs"]),
    ("limpeza e construção da rede v1",                ["src/02_limpar_e_construir.py"]),
    ("figura de conferência da rede v1",               ["src/03_primeira_analise.py"]),
    ("parte 1: descrição da rede",                     ["src/04_parte1_descricao.py"]),
    ("parte 2: conectividade e distâncias",            ["src/05_parte2_conectividade.py"]),
    ("parte 3: centralidades",                         ["src/06_parte3_centralidades.py"]),
    ("parte 4: remoção de paradas, trechos e grupos",  ["src/07_parte4_remocao.py"]),
    ("parte 5: núcleos (k-core, onion, k-truss)",      ["src/08_parte5_nucleos.py"]),
    ("parte 6: modelagens alternativas e bipartida",   ["src/09_parte6_alternativas.py"]),
]
env = dict(os.environ, MPLBACKEND="Agg", PYTHONHASHSEED="0")
with open("data/analise/log_execucao.txt", "w", encoding="utf-8") as log:
    for i, (nome, args) in enumerate(ETAPAS, 1):
        t = time.time(); print(f"[{i}/{len(ETAPAS)}] {nome} ...", flush=True)
        r = subprocess.run([sys.executable, *args], capture_output=True, text=True, env=env, encoding="utf-8")
        log.write(f"\n{'=' * 78}\n[{i}] {nome}\n{'=' * 78}\n{r.stdout}{r.stderr}")
        if r.returncode:
            print(r.stdout[-1500:], r.stderr[-2500:]); sys.exit(f"falhou na etapa {i}: {nome}")
        print(f"      ok ({time.time() - t:.0f}s)")
print("\nPronto. Figuras em figs/, tabelas em data/analise/, log em data/analise/log_execucao.txt")
