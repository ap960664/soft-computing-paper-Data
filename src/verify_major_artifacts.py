from pathlib import Path
import json,csv,hashlib,zipfile,re
from openpyxl import load_workbook
from docx import Document
R=Path(__file__).resolve().parents[1];out=[]
def ck(label,value):
    out.append({'check':label,'passed':bool(value)})
    assert value,label
counts=json.loads((R/'logs/selection_counts.json').read_text())
ck('15 included + 6 pending + 3 excluded = 24 candidates, plus3 surveys',counts['included_primary']==15 and counts['pending_primary']==6 and counts['excluded_primary']==3 and counts['primary_candidates']==24 and counts['registry_records']==27)
matrix=load_workbook(R/'Complete_Literature_Matrix.xlsx',read_only=True,data_only=True)
ck('14 canonical matrix tabs',len(matrix.sheetnames)==14)
rows=list(matrix['Primary_Studies'].values)
ck('21 primary matrix records',len([x for x in rows[1:] if x[0]])==21)
ck('New fulltext P023 retained',any('P023' in x for x in rows[1:]))
ck('Expanded448metric rows',len(list(matrix['Expanded_Results'].values))-1==448)
ck('Expanded28stability rows',len(list(matrix['Expanded_Stability'].values))-1==28)
for title in ['Expanded_Results','Expanded_Stability']:
    vals=list(matrix[title].values);ck(title+' numerical values remain numeric',all(isinstance(x[3 if title=='Expanded_Results' else 2],(float,int)) for x in vals[1:]))
samplepath=R/'outputs/01a11ce9-c69d-77d1-86a7-82e828ff3742/Literature_Matrix_Sample_Format.xlsx'
sample=load_workbook(samplepath,read_only=True,data_only=True)
supplied=load_workbook(R/'Samples/Sample_idea_19 _ Hritik Mandoliya _ Machine Learning-Based Improvement of COCOMO Software Cost Estimates.xlsx',read_only=True)
vals=list(sample.active.values)
ck('Sampleexact13headings',list(vals[0])==list(next(supplied.active.values))[:13])
ck('Sample21populatedrecords,one tab',len(vals)==22 and len(sample.sheetnames)==1 and all(all(x is not None for x in row) for row in vals[1:]))
ck('Sampleall21sourceDOIs',all('doi.org/' in str(row[12]).lower() for row in vals[1:]))
author=load_workbook(R/'Author_Verification_Worksheet.xlsx',read_only=True,data_only=True)
ck('Author10tabs',len(author.sheetnames)==10)
ck('Author29manualchecks',len(list(author['Manual_Source_Checks'].values))==30)
ck('Author68numericalevidence',len(list(author['Numerical_Evidence'].values))==69)
ck('Author6pending',len(list(author['Pending_Sources'].values))==7)
ck('Author new claim spacing',all('420newrecords' not in str(x) for row in author['Manual_Source_Checks'].values for x in row))
for wb in [matrix,sample,author]:
    ck('No Excel error values in '+wb.path if hasattr(wb,'path') else 'No Excel error values',not any(str(v) in ['#REF!','#VALUE!','#DIV/0!','#NAME?','#N/A'] for sh in wb for row in sh.values for v in row))
doc=Document(R/'Final_Research_Paper.docx');text='\n'.join(p.text for p in doc.paragraphs)
ck('DOCX4tables',len(doc.tables)==4)
ck('DOCXcontainsnewmethods/420records',all(x in text for x in ['420','CGCO','CGMO','Iris','Digits','Jaccard']))
refs=json.loads((R/'references/numbered_references.json').read_text())
ck('23references',len(refs)==23)
with zipfile.ZipFile(R/'Final_Research_Paper.docx') as z:
    xml=z.read('word/document.xml').decode();ck('10imageobjects/3Wordcrops',xml.count('<wp:inline')==10 and xml.count('<a:srcRect')==3)
ck('18renderedpages',len(list((R/'tmp/major_revision_ready').glob('page-*.png')))==18)
ck('Originalexperimentalpreservation',json.loads((R/'reports/major_revision_preservation.json').read_text())['all_unchanged'])
manifest=json.loads((R/'Results_and_Graphs/major_revision/manifest.json').read_text())
ck('Executedalgorithmcodeunchanged',all(hashlib.sha256((R/'src'/name).read_bytes()).hexdigest()==h for name,h in manifest['code_sha256'].items()))
audit=json.loads((R/'Results_and_Graphs/major_revision/audit.json').read_text())
ck('Currentrawshaagreeswithverifiedaudit',hashlib.sha256((R/'Results_and_Graphs/major_revision/raw_metrics.csv').read_bytes()).hexdigest()==audit['raw_sha256'])
(R/'reports/major_revision_artifact_verification.json').write_text(json.dumps({'checks':out,'status':'PASS'},indent=2))
print(f'{len(out)} artifact checks PASS')
