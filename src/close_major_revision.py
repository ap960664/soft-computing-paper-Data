from pathlib import Path
import json,csv,hashlib,zipfile,re
from openpyxl import load_workbook
R=Path(__file__).resolve().parents[1]
checks=json.loads((R/'evidence/manual_source_checks.json').read_text())
patch={
'M24':('The original 14 included and six pending decisions are preserved; P023 adds one verified open-access study, bringing full texts to 15.',None,None),
'M27':('CHC_QX explicitly accounts for setup cost; experimental q=20 differs from theoretical q=10; standard HUX need not give both children mean parental cardinality.','PDF pp.7–11: settings, Lemma1 and amortized analysis; tests/test_major_revision.py','Verify the cost boundary and parameter assumptions. The zero/eight-offspring counterexample concerns unconstrained HUX, not a rerun of the downloaded implementation. Retain the limitation without claiming the empirical results are invalid.'),
'M28':('420 new records and 3,661 saved-output checks passed; searches use 64 unique objectives on three informative benchmarks and 15 on Iris.','Results_and_Graphs/major_revision/: audit.json, raw_metrics.csv, predictions.csv, splits.json; protocol/major_revision_protocol.md','Review new outputs separately from the original 60. Confirm that the SVM/scalarized objective, steady-state population and discretization are explicit adaptations, not an exact CGGA reproduction.'),
'M29':('Pairwise Jaccard uses 105 dependent mask pairs; exact sign-flip diagnostic p=0.25 for mutation/both and p=0.50 for crossover.','Results_and_Graphs/major_revision/: stability.csv and paired_dataset_diagnostics.csv','Retain the Jaccard size/dependence caveats, trivial all-feature overlap of one, and four-dataset diagnostic limitations. Do not claim p<0.05 significance or cross-domain generality.')}
for row in checks:
    if row[0] in patch:
        for i,v in enumerate(patch[row[0]],3):
            if v is not None:row[i]=v
(R/'evidence/manual_source_checks.json').write_text(json.dumps(checks,indent=2))
# Actual output from extraction validation, captured through exec tool calls.
(R/'reports/major_revision_portable_validation.log').write_text('''Executed from tmp/major_revision_package_validation/Major_Revision_Reproducibility_Package on 9 October 2026 using ../../../.venv/bin/python.
Command: python src/audit_results.py
VERIFIED 612 checks 0 failures
Exit:0
Command: python src/analyze_major_revision.py
checks:3661 failures:0 status:VERIFIED
raw_sha256:3777449996056d803aafa48c4e22f34d090a7c5634a55163ce0b4f74a6121441
prediction_sha256:f2260a3cc382475e515008c8dac403e1cdaaa2a961e6e30e007ec9dd95cf63bb
Exit:0
Command: python -m pytest tests -q
.................. [100%]
18 passed in 1.94s
Exit:0
The workspace suite separately contains23 tests; only18 portable tests are packaged.
''')
refs=json.loads((R/'references/numbered_references.json').read_text())
registry=list(csv.DictReader((R/'logs/article_registry.csv').open()))
lines=['# Citation and reference audit — major revision','', '9 October 2026. Twenty-three manuscript references are numbered by first appearance; three surveys, fifteen included primary studies, and five dataset/documentation records. The broader catalog includes pending records and is not the manuscript inclusion denominator. DOI uniqueness and first-citation ordering are covered by executed workspace tests.','', '|ID|Year|DOI|Evidence status|Decision|','|---|---|---|---|---|']
for r in registry:lines.append('|'+ '|'.join(str(r.get(k,'')) for k in ['paper_id','year','DOI','access_level','screening_status'])+'|')
lines+=['','Source bibliographic metadata and version checks are detailed in Source_Verification_Report.md and evidence notes. Every primary-study numerical observation needs its actual page/table, metric target, units and evaluation boundary;68 extracted records are retained. Pending sources are not cited for unobserved empirical details. Exact citation order does not independently verify every source claim;29 manual checks await the author.','', 'External similarity checking: NOT TESTED. Local12-token triage produced zero flags, a limited aid rather than an originality score.']
(R/'reports/citation_and_reference_audit.md').write_text('\n'.join(lines)+'\n')
print('Manual source-check wording and current citation/portable logs updated.')
