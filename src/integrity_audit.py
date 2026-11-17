from pathlib import Path
import re,csv,json,hashlib,zipfile
from collections import Counter
R=Path(__file__).resolve().parents[1]
draft=(R/'drafts/review_draft.md').read_text();body=draft.split('## References')[0]
def words(text):return re.findall(r'[a-z0-9]+',text.lower())
tokens=words(body);n=12;grams={tuple(tokens[i:i+n]):i for i in range(len(tokens)-n+1)};matches=[]
for path in (R/'tmp/pdf_text').glob('*.txt'):
    t=words(path.read_text());found=set()
    for i in range(len(t)-n+1):
        g=tuple(t[i:i+n])
        if g in grams and g not in found:found.add(g);matches.append(dict(source=str(path.relative_to(R)),shared_sequence=' '.join(g),draft_word_offset=grams[g],review='Inspect technical phrasing/title overlap; not a plagiarism score'))
with (R/'reports/close_phrase_matches.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['source','shared_sequence','draft_word_offset','review']);w.writeheader();w.writerows(matches)
inventory=list(csv.DictReader((R/'logs/input_inventory.csv').open()));checks=[]
for row in inventory:
    path=R/row['filepath']
    if path.exists() and row['notes'].startswith('SHA256 '):
        checks.append(dict(path=row['filepath'],unchanged=hashlib.sha256(path.read_bytes()).hexdigest()==row['notes'][7:]))
(R/'reports/source_preservation.json').write_text(json.dumps(checks,indent=2))
report='# Originality and similarity review\n\nExternal similarity score: NOT TESTED — no authorized service available. Turnitin/QuillBot/AI detector was not run; no 2–3% guarantee is made.\n\nAll manuscript prose was generated as fresh synthesis from evidence notes. Literature and local experiments are separated, counterexamples retained, and the claims reviewed for source support. No source abstract was used as a rewrite template.\n\nA local 12-token exact-sequence screen (case/punctuation normalized) compared manuscript text excluding references with extracted source texts. '+str(len(matches))+' candidate sequences were logged in close_phrase_matches.csv. This limited lexical check does not detect conceptual copying, translated overlap, or all close paraphrase and is not an external similarity report. It is a triage aid only.\n\nThe qualitative audit checked method descriptions, metric semantics, timing boundaries, and conclusion language against primary pages. Author verification of citations and expression remains necessary. All generated manuscript paragraphs require independent student authorship under the university rule supplied in this chat; cosmetic synonym changes are not compliance.\n'
(R/'reports/originality_and_similarity_review.md').write_text(report)
print('Exact sequence flags',len(matches),'Original input preservation',all(x['unchanged'] for x in checks))
