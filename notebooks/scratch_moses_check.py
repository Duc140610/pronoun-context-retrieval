import gzip
import xml.etree.ElementTree as ET

XML_PATH = "data/raw/en-vi.xml.gz"
MOSES_EN = "data/raw/en.txt"
OUT = "data/processed/doc_ids.txt"

n_links = 0
doc = None
with gzip.open(XML_PATH, "rb") as f, open(OUT, "w", encoding="utf-8") as out:
    for ev, el in ET.iterparse(f, events=("start", "end")):
        if ev == "start" and el.tag == "linkGrp":
            doc = el.get("fromDoc")
        elif ev == "end" and el.tag == "link":
            out.write(f"{doc}\n")
            n_links += 1
            el.clear()

with open(MOSES_EN, encoding="utf8") as f:
    n_lines = sum(1 for _ in f)

print("so link trong XML:", n_links)
print("so dong Moses     :", n_lines)
print("KHOP" if n_links == n_lines else "LECH, khong dung")