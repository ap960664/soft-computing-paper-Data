"""Build a new portable revision package; never replace the earlier archive."""
from pathlib import Path
import shutil,json,hashlib,zipfile
R=Path(__file__).resolve().parents[1];P=R/'tmp/Major_Revision_Reproducibility_Package'
if P.exists():shutil.rmtree(P)
P.mkdir()
def copy(rel):
    a=R/rel;b=P/rel;b.parent.mkdir(parents=True,exist_ok=True)
    if a.is_dir():shutil.copytree(a,b,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    else:shutil.copy2(a,b)
for rel in ['requirements.txt','README.md','AI_Assistance_Record.md','Reproducibility_and_Test_Report.md','Source_Verification_Report.md','Final_Quality_and_Submission_Checklist.md','Research_Methodology_and_Search_Log.md','Research_Paper_References.bib','Final_Research_Paper.docx','Complete_Literature_Matrix.xlsx','Author_Verification_Worksheet.xlsx','Publication_Positioning_and_Improvement_Plan.md','results','figures','configs','protocol','Results_and_Graphs/major_revision','Results_and_Graphs/publication_revision']:
    copy(rel)
for name in ['ga.py','experiment.py','plot_results.py','audit_results.py','major_ga.py','major_experiment.py','analyze_major_revision.py','plot_major_revision.py','update_publication_figures.py']:
    copy('src/'+name)
for name in ['major_revision_full.log','major_revision_smoke.log','major_revision_smoke_attempt1.log']:
    copy('logs/'+name)
for name in ['major_revision_all_tests.log','major_revision_tests_final.log','major_revision_result_audit.log','major_revision_preservation.json','major_revision_visual_qa.md','originality_and_similarity_review.md','major_revision_portable_validation.log','citation_and_reference_audit.md','major_revision_final_artifact_tests.log','major_revision_artifact_verification.json','visual_qa.json']:
    copy('reports/'+name)
copy('evidence/manual_source_checks.json')
for name in ['evidence_quality.csv','quality_definitions.json','P002_notes.md']:
    copy('evidence/'+name)
for name in ['selection_counts.json','article_registry.csv','search_and_screening.csv']:
    copy('logs/'+name)
copy('notes/03_survey_overlap_audit.md')
copy('reports/publication_revision_qa.json')
(P/'tests').mkdir()
shutil.copy2(R/'tmp/repro_package/tests/test_experiments.py',P/'tests/test_experiments.py')
shutil.copy2(R/'tests/test_major_revision.py',P/'tests/test_major_revision.py')
shutil.copytree(R/'tmp/repro_package/data',P/'data')
shutil.copy2(R/'outputs/01a11ce9-c69d-77d1-86a7-82e828ff3742/Literature_Matrix_Sample_Format.xlsx',P/'Literature_Matrix_Sample_Format.xlsx')
(P/'README.md').write_text('''# Portable major-revision reproducibility package

9 October 2026. Latest export includes final27-record study-selection and15-study reporting-quality figures, the publication positioning plan and updated manuscript. Contains original60 records plus separately executed420 records on four datasets/seven methods. No valid experimental values were changed and no source PDFs are redistributed. All29 manual author-verification checks remain visible and outstanding in Author_Verification_Worksheet.xlsx and evidence/manual_source_checks.json. Complete university/journal approval and independent student prose authorship remain outstanding; see AI_Assistance_Record.md and the final checklist.

Use Python 3.14 and requirements.txt. From this extracted directory, after installing dependencies:

```bash
python src/audit_results.py
python src/analyze_major_revision.py
python -m pytest tests -q
python src/plot_major_revision.py
python src/update_publication_figures.py
```

The portable suite has18 tests:12 original executable tests plus6 major-revision tests. The five additional workspace research-artifact tests depend on the full source/evidence workspace and are deliberately excluded, not reported as portable passes. Original saved audit612checks and new saved audit3661checks have distinct pools. New macro-F1 differs from original benign-positive binary F1. SD/stability are descriptive over dependent folds/pairs. CGGA operators are adapted, not exact published-method reproductions. See protocol/major_revision_protocol.md for choices/deviations before execution.

Expanded output location: Results_and_Graphs/major_revision/. It includes raw_metrics.csv (420 rows), predictions.csv, masks.json, splits.json, convergence.csv, manifest.json, datasets.json, data snapshots, summary_tidy.csv, stability.csv, seed_means.csv and paired_dataset_diagnostics.csv. All recorded timing components are columns of raw_metrics.csv. audit_checks.csv retains all 3,661 check outcomes; audit.json contains the check/failure counts and raw/prediction hashes; recomputed_metrics.csv retains 420 confusion-count recalculations. Configurations are configs/major_revision_full.yaml and major_revision_smoke.yaml; implementations are src/major_ga.py and major_experiment.py. Runtime and software versions are manifest data, not newly remeasured observations. Run analyze_major_revision.py to verify saved records without refitting models.

Optional refit (preserve Results_and_Graphs/major_revision/ first, because outputs are overwritten):

```bash
python src/major_experiment.py configs/major_revision_full.yaml
python src/analyze_major_revision.py
python src/plot_major_revision.py
```

Data snapshots/DESCR and originalWDBC snapshot are retained. Full run uses local pinned sklearn loaders; compare datasets.json hashes. Hardware timing will differ; score/mask equality depends on the exact environment. HASHES.json records package files before extraction validation. No purchase, browser, submission or similarity-check service is necessary to execute these commands.
''')
hashes={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in P.rglob('*') if f.is_file()}
(P/'HASHES.json').write_text(json.dumps(hashes,indent=2))
z=R/'Complete_Reproducibility_Package_Major_Revision.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as arc:
    for f in sorted(P.rglob('*')):
        if f.is_file():arc.write(f,str(Path(P.name)/f.relative_to(P)))
with zipfile.ZipFile(z) as arc:
    assert arc.testzip() is None
    dest=R/'tmp/major_revision_package_validation';dest.mkdir(exist_ok=True)
    arc.extractall(dest)
checks={p:hashlib.sha256((dest/P.name/p).read_bytes()).hexdigest()==h for p,h in hashes.items()}
assert all(checks.values())
(R/'reports/major_revision_package_verification.json').write_text(json.dumps({'archive':z.name,'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'zip_crc':'PASS','files_hashed':len(hashes),'all_extracted_hashes_match':all(checks.values()),'portable_test_log':'reports/major_revision_portable_validation.log'},indent=2))
print(f'Archive built, CRC passed, {len(hashes)} extracted file hashes matched.')
