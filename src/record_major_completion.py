from pathlib import Path
import json,hashlib,shutil,datetime
R=Path(__file__).resolve().parents[1]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=['Final_Research_Paper.docx','Complete_Literature_Matrix.xlsx','Author_Verification_Worksheet.xlsx','outputs/01a11ce9-c69d-77d1-86a7-82e828ff3742/Literature_Matrix_Sample_Format.xlsx']
record={'checked_utc':now,'docx_pages':18,'all_pages_visually_inspected':True,'matrix_tabs':14,'author_tabs':10,'sample_records':21,'included':15,'pending':6,'excluded':3,'sha256':{f:sha(R/f) for f in files},'details':'reports/major_revision_visual_qa.md','artifact_checks':'reports/major_revision_artifact_verification.json'}
for f in ['visual_qa.json','visual_qa.md','final_quality_gate.md','test_report.md','sample_format_matrix_qa.json','local_similarity_source_collection.json']:
    p=R/'reports'/f;a=R/'reports/pre_major_revision'/f
    if p.exists() and not a.exists():shutil.copy2(p,a)
(R/'reports/visual_qa.json').write_text(json.dumps(record,indent=2))
(R/'reports/visual_qa.md').write_text((R/'reports/major_revision_visual_qa.md').read_text())
(R/'reports/final_quality_gate.md').write_text('''# Final quality gate — major revision

9 October 2026. Complete research/reference artifacts for author review, not approved final university/journal submission.

|Gate|Status|Actual evidence or limitation|
|---|---|---|
|Inputs, originals and syllabus|PASS|Supplied inputs unchanged; GA UnitIV/SVM UnitII; original results/figures/ZIP byte-identical.|
|Survey overlap|AUDITED, NOVELTY NOT ESTABLISHED|Three complete surveys and specific page/table comparisons; substantial prior coverage.|
|Search/evidence|PASS WITH COVERAGE LIMIT|15included/6pending/3excluded;27registry;21relevant matrix rows; bounded API exports, not exhaustive PRISMA.|
|Literature/author XLSX|PASS|14/10tabs,29manualchecks,68extracted results; exact13heading sample21rows; numerical fields and traceability checked.|
|Executed experiments|PASS|Original60preserved; separate420records,4datasets,7methods; matched searchNFE and complete guidance costs.|
|Saved-result audits|PASS|612legacy and3661expandedchecks; actual predictions and split/mask/timing data.|
|Executed tests|PASS|23workspace;18portable from extracted package; final artifact tests logged separately.|
|DOCX/reference/visual QA|PASS|18pages,4tables,8figures,2nativeequations,23references; allpages inspected; finalreferencepage filled.|
|External similarity|NOT TESTED|Limited local12token audit0flags is not a percentage or originality certification.|
|Institutional human authorship|NOT SATISFIED|Current prose is AI-generated; student must independently author final submission and truthfully document assistance.|
|Human source/final approval|PENDING|29specific worksheet checks and exact final version approval.|
|Publication differentiation|NOT ESTABLISHED|Selective review, convenience benchmarks, adaptations/untunedSVM/dependentfolds; no guaranteed acceptance.|

Mandatory human tasks and optional journal improvements are separated in Final_Quality_and_Submission_Checklist.md. No paid-access or browser task is required to use these artifacts.
''')
(R/'reports/test_report.md').write_text((R/'Reproducibility_and_Test_Report.md').read_text())
sample=R/files[-1]
(R/'reports/sample_format_matrix_qa.json').write_text(json.dumps({'date':'2026-10-09','sample_preserved':True,'exact_header_match':True,'sheets':1,'columns':13,'primary_records':21,'fulltext_records':15,'pending_records':6,'source_locators':True,'citation_notes':21,'visual_views_inspected':['A1:D3','D1:F3','G1:J3','K1:M3','K19:M21','H11:M11'],'output':str(sample),'sha256':sha(sample)},indent=2))
collection=[{'text_file':str(p.relative_to(R)),'sha256':sha(p)} for p in sorted((R/'tmp/pdf_text').glob('*.txt'))]
(R/'reports/local_similarity_source_collection.json').write_text(json.dumps(collection,indent=2))
with (R/'notes/04_decisions_and_assumptions.md').open('a') as f:f.write('''\n9 October2026 amendment:author details/no coauthors confirmed and university prohibition onAI-authored finalprose supplied. Earlier unknown-author/regulation statements are historical. User major-revision request authorized multiple datasets, guided operators and stability/cost diagnostics under a new pre-execution protocol. One new verifiedOA fulltext adds P023 to the original14; sixpending remain unchanged. No browserUI/purchase. All expanded operators are explicit adaptations, not exact published-method reproduction; novelty remainsunestablished.\n''')
with (R/'AGENT_PROGRESS.md').open('a') as f:f.write('''\n## 9 October 2026 — major revision completed as research/reference artifacts\n\n- Actual supplemental discovery and P02313page fulltext read; P024 regression-only exclusion. Current15fulltext+6pending,3excluded,3surveys;21primary matrixrows.\n- Pre-execution protocol followed: four real datasets,seven methods,420saved records;451.48sfullrun. Basic/guided component comparison,macroF1,maskstability,completecost andlimiteddiagnostics generated from rawdata.\n- 3661expandedchecks pass;23workspace tests pass;extracted package612original+3661expandedchecks and18portabletests pass. Finalartifact checks27pass; finaltargetedresearchtests logged. Originalresults/figures/ZIP unchanged.\n-18page DOCX fullyvisuallychecked;4tables,8semanticfigures,2nativeequations,23references. Mainmatrix14tabs,authorworksheet10tabs with29exactmanualchecks, samplematrix21records/exact13headings.\n- Reports/code/results/BibTeX/checklists/AIrecord exported;new separate major-revision portableZIP built withCRC/extractedhashverification. OriginalZIP remainsfrozen.\n- Universityhuman-authorship rule and29manualsourcechecks/finalapproval unresolved. Sixpending papers do not supportunseenclaims;no paidaccessrequired. SimilarityNOTTESTED;publicationnoveltyNOTESTABLISHED. No browserUI orsubmission.\n''')
print('Current QA receipts and progress updated.')
