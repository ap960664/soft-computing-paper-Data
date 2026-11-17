from pathlib import Path
import csv, hashlib, json
from pypdf import PdfReader
from openpyxl import load_workbook

root=Path(__file__).resolve().parents[1]
for folder in ['notes','protocol','literature/incoming','literature/verified','requests','evidence','logs','references','configs','src','tests','results','figures','reports','drafts','deliverables','tmp/pdf_text','tmp/pdf_views']:
    (root/folder).mkdir(parents=True,exist_ok=True)
rows=[]
for path in sorted(root.rglob('*')):
    if not path.is_file() or path.suffix.lower() not in ['.pdf','.xlsx','.md']: continue
    if any(part in ['tmp','notes','reports','logs','protocol','evidence'] for part in path.relative_to(root).parts): continue
    row=dict(filepath=str(path.relative_to(root)),kind=path.suffix,pages_or_sheets='',purpose='supplied input',readable=True,notes='SHA256 '+hashlib.sha256(path.read_bytes()).hexdigest())
    if path.suffix=='.pdf':
        reader=PdfReader(path); row['pages_or_sheets']=len(reader.pages)
        texts=[p.extract_text(extraction_mode='layout') for p in reader.pages]
        (root/'tmp/pdf_text'/f'{path.stem}.txt').write_text('\n\n'.join(f'=== PDF PAGE {i+1} ===\n{t}' for i,t in enumerate(texts)))
        row['readable']=all(len(t.strip())>30 for t in texts)
        print(path.name, len(texts),'pages',sum(len(t) for t in texts),'characters',row['readable'])
    elif path.suffix=='.xlsx':
        wb=load_workbook(path,data_only=False)
        row['pages_or_sheets']='; '.join(wb.sheetnames)
        data={s.title:{'rows':s.max_row,'columns':s.max_column,'values':list(s.values),'freeze':s.freeze_panes,'merged':[str(r) for r in s.merged_cells.ranges]} for s in wb}
        (root/'tmp'/f'{path.stem}.json').write_text(json.dumps(data,indent=2,default=str))
        print(path.name,[(s.title,s.max_row,s.max_column) for s in wb])
    rows.append(row)
with (root/'logs/input_inventory.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
