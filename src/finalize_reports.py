from pathlib import Path
import csv,json,shutil,hashlib,datetime
R=Path(__file__).resolve().parents[1]
date='2026-10-09 Asia/Kolkata'
counts=json.loads((R/'logs/selection_counts.json').read_text());manifest=json.loads((R/'results/experiment_manifest.json').read_text());testlog=(R/'results/tests_final.log').read_text()
report=f'''# Reproducibility and test report

Checkpoint: {date}. Experiment status: {manifest['status']}.

## Actual execution

Commands executed:

```
.venv/bin/python src/experiment.py configs/experiment_fast.yaml
.venv/bin/python src/experiment.py configs/experiment_full.yaml
.venv/bin/python src/plot_results.py
.venv/bin/python src/plot_evidence.py
.venv/bin/python -m pytest tests -q
```

The declared full run saved {manifest['rows']} rows in {manifest['elapsed_seconds']:.3f} seconds. Four methods × five outer folds × three seeds; no method failures recorded. Configurations, unique evaluation counts, training/search/prediction times, splits, predictions, selected variables and convergence are saved. No independent-trial significance claim is made from correlated CV folds. The algorithm is a custom scalarized binary GA, not a reproduction of each reviewed advanced GA.

Hardware: Apple M4 Pro, 24 GiB. Package versions are in requirements.txt and the manifest. Test outputs include a fresh instrumented smoke experiment in a temporary directory, confirming selector/scaler fitting inside training boundaries. Fixed-seed fitness reproduction and saved-prediction metric recalculation were tested; a second entire full run was not required or claimed. Execution time itself is not deterministic.

## Actual final test output

```
{testlog.strip()}
```

See tests/test_project.py for 17 tests covering masks, operators, dataset/splits, preprocessing/filter fit boundaries, cache and fitness reproducibility, budget/fold comparability, output ranges, prediction-to-metric agreement, raw-to-summary agreement, CSV-driven figures, registry/screening conservation, source/matrix traceability, citation order, numerical provenance and DOCX structure. These tests are integration safeguards, not independent scholarly peer review or external source certification.

Office generation uses the bundled runtimes in logs/runtime_paths.md. Workbook formulas were recalculated and reopened; 12 sheet previews were checked. DOCX was rendered with the bundled renderer and all current pages inspected; details in reports/visual_qa.md. Source preservation fingerprints are in reports/source_preservation.json. No external similarity service was run.
'''
(R/'Reproducibility_and_Test_Report.md').write_text(report);(R/'reports/test_report.md').write_text(report)

registry=list(csv.DictReader((R/'logs/article_registry.csv').open()));rows=[]
for r in registry:
    rows.append(f"|{r['paper_id']}|{r['year']}|{r['kind']}|{r['DOI']}|{r['access_level']}|{r['screening_status']}|")
verification='''# Source verification report

Metadata records were saved from Crossref and cross-checked against publisher records or PDF title pages. The fourteen included full texts match their declared titles/DOIs. Original source PDFs/workbooks were preserved; source fingerprints are logged. Publisher article URLs are in logs/article_registry.csv. A DOI redirect or bibliographic deposit is not a claim of PDF access.

|ID|Year|Kind|DOI|Evidence access|Decision|
|---|---|---|---|---|---|
'''+ '\n'.join(rows)+'''

## Numerical and interpretive traceability

evidence/reported_results.csv stores extracted numerical observations with dataset, units, protocol and physical page/table. The main matrix stores operator/settings/split descriptions and separate appraisal. Per-study notes support the synthesis and reporting codes. The manuscript's tables and plots are generated from those records or actual experiment CSVs. Review-paper citations, primary-study counts and total bibliography counts are distinct pools: three reviews + fourteen primaries + two documentation records = nineteen manuscript references; the full catalog has20 relevant primary publications. Pending records are not cited for unobserved methods or results.

Verified source issues retained: P004 feature-recovery F1 differs from classification F1; P006 Table8 repeat caption/prose inconsistency; P003 Table11 dataset labels differ from Table2; P010 abstract says nine datasets while main benchmark tables show six; P005 detailed crossover/selection should be verified against implementation. Main-text nested validation is unclear in several reports; this is not coded as proven label leakage. Counterexamples to universal superiority are retained.

P009 was an erroneous unchecked DOI lookup that resolved to unrelated clustering. It is excluded and never appears in the bibliography. This is an internal lookup correction, not a fabricated included study. The registry count concerns records handled, not all search hits.

P001, P008 and P011: tool full-text retrieval unsuccessful; the student also reports purchase-only/inaccessible pages. They remain outside the included pool. P007/P019 remain pending; P015 abstract-only; P004 supplementary runtime/details remain NOT VERIFIED. Full-text access limitations do not prove that the papers' methods or results are deficient. No purchase or unauthorized access is requested.

The journal shortlist records initial HTTP403 failures and subsequent official browser reads before the user requested no more browser use. ASOC/Swarm guide sections and Swarm fees/indexing were verified; remaining fields stay unverified. Official general Elsevier AI policy was accessible and linked in AI_Assistance_Record.md. No chosen-journal compliance claim is made.

## Required human verification

Check each DOI/title, source table transcription, quality code, dataset identity and interpretation directly in the original PDF. Review the appendix-level ambiguities and inaccessible evidence before stronger claims. The source audit is an AI-assisted first review, not an independent second-reviewer validation.
'''
(R/'Source_Verification_Report.md').write_text(verification);(R/'reports/citation_and_reference_audit.md').write_text(verification)
method=(R/'protocol/review_protocol.md').read_text()+'\n\n# Executed searches and corpus\n\n'+f"Registry {counts['registry_records']}; reviews3; candidates{counts['primary_candidates']}; included{counts['included_primary']}; pending{counts['pending_primary']}; excluded{counts['excluded_primary']}.\n\n"
method+='|Query|Date|Exact string|Displayed count|\n|---|---|---|---|\n'
for q in csv.DictReader((R/'logs/search_queries.csv').open()):method+=f"|{q['query_id']}|{q['search_date']}|{q['exact_query']}|{q['displayed_count']}|\n"
method+='\nThe search is not exhaustive. Full-text extraction dates and upload provenance are in the registry/evidence notes. Eligibility rules unchanged; newly identified GeFeS was retained pending full text, not silently included. No PRISMA or meta-analysis claim.\n'
(R/'Research_Methodology_and_Search_Log.md').write_text(method)
quality='''# Final quality and submission checklist

Current status: COMPLETE WORKING ARTIFACTS FOR AUTHOR REVIEW — NOT SUBMISSION-READY. The filenames identify the current requested artifacts, not certification of university or journal acceptance. The broader research/publication objective is not fully achieved.

|Gate|Status|Evidence or limitation|
|---|---|---|
|Supplied inputs preserved and audited|PASS|logs/input_inventory.csv; source_preservation.json|
|Syllabus scope|PASS|GA UnitIV, SVM UnitII, CO5; notes/01|
|Three-survey full-text overlap audit|PASS|notes/03 with pages; no novelty claim|
|Protocol and genuine screening records|PASS WITH COVERAGE LIMIT|Structured selected review; native database exports not obtained|
|Verified primary pool|LIMITED|Twenty relevant matrix publications: fourteen full-text included and six pending; two exclusions separate|
|Actual XLSX with required sheets|PASS|Complete_Literature_Matrix.xlsx;12 tabs; source IDs and missingness retained|
|Developed editable manuscript|PASS|Final_Research_Paper.docx; all eight main sections, abstract, tables, figures, references|
|Experiment execution|PASS|60 rows, actual predictions/configs/versions/timing; complete declared laptop run|
|Meaningful automated tests|PASS|17 passed; actual final output saved|
|References/citations/provenance|PASS FOR CURRENT CORPUS|19 references; fourteen primaries and three surveys; source/report audit|
|Visual DOCX/workbook QA|PASS|All current DOCX pages and12 sheet views inspected; see visual_qa.md|
|Originality and external similarity|INTERNAL AUDIT ONLY|No 12-token flags in local screen; qualitative audit; external score NOT TESTED|
|Human authorship/institutional acceptance|NOT SATISFIED|University prohibits AI-authored final prose; independent student authorship required|
|Publication differentiation|NOT ESTABLISHED|Direct2026 review overlap; selected corpus too small for comprehensive claim|
|Journal/indexing/fees/formatting|PENDING|No journal selected;partial official verification completed;shortlist is conditional|
|Final author verification and submission|PENDING|No upload/submission performed|

## Next actions requiring human input or external access

Independently author/revise university prose in a way permitted by the institution, verify every source interpretation and numerical transcription, and approve the final manuscript;author/affiliation details and sole authorship were confirmed. Resolve unavailable primary/supplemental PDFs if a legitimate access route becomes available; no purchase is requested. Choose a journal after expanding literature coverage and confirming a differentiated contribution. Verify its current fees, indexing, review article eligibility and instructions, then add the truthful AI declaration and required Methods/caption disclosures. Review and approve the final version explicitly before any submission.

The local fourteen-study manuscript can be evaluated as a developed AI-assisted manuscript for author review and technical demonstration. It cannot be represented as a comprehensive2020-2026 systematic review, a validated novel algorithm, or compliant final university prose without the remaining human work. The approximately20-record matrix target is achieved, but fourteen studies have complete full-text extraction. Full-text inclusion of the remaining six is unresolved rather than inferred.
'''
(R/'Final_Quality_and_Submission_Checklist.md').write_text(quality);(R/'reports/final_quality_gate.md').write_text(quality)
shutil.copy2(R/'references/literature_catalog.bib',R/'Research_Paper_References.bib')
legacy=R/'deliverables';legacy.mkdir(exist_ok=True)
shutil.copy2(R/'Final_Research_Paper.docx',legacy/'GA_Feature_Selection_Review_Paper.docx')
shutil.copy2(R/'Complete_Literature_Matrix.xlsx',legacy/'GA_Feature_Selection_Literature_Matrix.xlsx')
code=R/'Experimental_Source_Code';code.mkdir(exist_ok=True)
for name in ['ga.py','experiment.py','plot_results.py','plot_evidence.py']:shutil.copy2(R/'src'/name,code/name)
shutil.copy2(R/'requirements.txt',code/'requirements.txt');shutil.copytree(R/'configs',code/'configs',dirs_exist_ok=True)
(code/'README.md').write_text('Exported current code snapshot. Run from the project root with `.venv/bin/python Experimental_Source_Code/experiment.py Experimental_Source_Code/configs/experiment_full.yaml`. Output paths are relative to the working directory. Canonical integration tests remain tests/test_project.py because they also check the literature matrix and DOCX. Office builders are in src/.\n')
export=R/'Results_and_Graphs';export.mkdir(exist_ok=True)
for p in (R/'results').iterdir():
    if p.is_file():shutil.copy2(p,export/p.name)
shutil.copytree(R/'figures',export/'figures',dirs_exist_ok=True)
progress=f'''# Agent progress

Checkpoint: {date}. Overall objective: IN PROGRESS / LIMITED BY EVIDENCE AND AUTHOR COMPLIANCE. All requested working artifact types exist; final submission acceptance is not claimed.

- COMPLETED: Entire supplied instruction.md and pasted writing requirements read; syllabus, samples and three surveys audited. Originals preserved.
- COMPLETED: Survey overlap audit and protocol; verified metadata, screening logs and page-grounded extraction for fourteen primaries.
- COMPLETED:12-tab populated XLSX; fully developed DOCX;19 IEEE-numbered references and BibTeX.
- COMPLETED: Executed smoke/full GA-SVM demonstrations,60 rows, plots, environment, predictions, splits and features.
- COMPLETED:17 tests passed; integrity/citation/corpus accounting and all-page visual checks.
- COMPLETED: Requested root reports and code/results exports; conditional three-journal shortlist.
- BLOCKED: P001, P008 and P011 inaccessible to agent/student; P015 inaccessible; TAGA accepted manuscript and P018 XML now included; P007/P019 pending; P004 supplements not obtained.
- NOT SATISFIED: Exhaustive search and full-text coverage of all twenty matrix studies, publication differentiation, human authorship/verification and journal-specific preparation.

Next concrete research action: expand the primary corpus and resolve a legitimate full-text route for GeFeS and missing operator studies; extraction can resume automatically when PDFs arrive. University submission requires independent student prose under the supplied rule. No external similarity service or submission has been run.
'''
(R/'AGENT_PROGRESS.md').write_text(progress)
print('Exported all requested working artifacts and reports')
