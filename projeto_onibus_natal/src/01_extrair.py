"""Etapa 1 - Extração bruta das tabelas de itinerário (PDFs da Viação Cidade das Dunas).
Saída: data/paradas_raw.csv (uma linha por parada listada em cada itinerário, na ordem original)."""
import re, sys, glob, os
import pdfplumber, pandas as pd

PDF_DIR = sys.argv[1] if len(sys.argv) > 1 else "pdfs"
OUT = "data/paradas_raw.csv"

def linha_do_titulo(texto):
    m = re.search(r"Linha\s+([\d.]+)\s*[–-]\s*(.+)", texto)
    return (m.group(1), m.group(2).strip()) if m else (None, None)

rows = []
for pdf_path in sorted(glob.glob(os.path.join(PDF_DIR, "linha*.pdf"))):
    with pdfplumber.open(pdf_path) as pdf:
        codigo, titulo = linha_do_titulo(pdf.pages[0].extract_text() or "")
        for pagina, page in enumerate(pdf.pages, start=1):
            for tabela in page.extract_tables():
                for r in tabela:
                    cel = [c.strip().replace("\n", " ") for c in r if c and c.strip()]
                    if len(cel) < 3 or not cel[0].isdigit():
                        continue
                    rows.append(dict(linha=codigo, titulo_linha=titulo,
                                     seq=int(cel[0]), nome_raw=cel[1], endereco_raw=cel[-1],
                                     arquivo=os.path.basename(pdf_path), pagina=pagina))
df = pd.DataFrame(rows).sort_values(["linha", "seq"]).reset_index(drop=True)
df.to_csv(OUT, index=False, encoding="utf-8")
print(df.groupby(["linha", "titulo_linha"]).agg(n=("seq", "size"), seq_min=("seq", "min"), seq_max=("seq", "max")))
