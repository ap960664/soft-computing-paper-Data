"""Finalize dated reports and exports without rerunning or modifying experiments."""
from pathlib import Path
import json,hashlib,shutil,ast,zipfile
R=Path(__file__).resolve().parents[1]
date='9 October 2026'
archive=R/'reports/pre_major_revision';archive.mkdir(exist_ok=True)
names=['Reproducibility_and_Test_Report.md','Source_Verification_Report.md','Source_and_Result_Audit_Report.md','Final_Quality_and_Submission_Checklist.md','Remaining_Issues_and_Resolution_Plan.md','README.md']
for n in names:
    if (R/n).exists() and not (archive/n).exists():shutil.copy2(R/n,archive/n)
def write(name,text):(R/name).write_text(text.strip()+'\n')
baseline=json.loads((R/'reports/author_review_baseline_hashes.json').read_text())
preserved={p:hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in baseline.items() if p.startswith(('results/','figures/')) or p=='Complete_Reproducibility_Package.zip'}
assert all(preserved.values())
write('reports/major_revision_preservation.json',json.dumps({'date':date,'files':preserved,'all_unchanged':all(preserved.values()),'note':'Literature counts and research artifacts deliberately updated after inclusion of P023; original experimental files preserved.'},indent=2))
write('Reproducibility_and_Test_Report.md',f'''# Reproducibility and executed-test report

{date}. Actual executions and saved outputs, not proposed results.

## Original demonstration: preserved

The original 60 records (WDBC; four methods; three seeds × five outer folds) and all files in results/ and figures/ remain byte-identical to the pre-revision hashes. The original Complete_Reproducibility_Package.zip remains a frozen earlier snapshot. Its 612 saved-result checks and 12 portable tests were executed previously; the author also reports an independent rerun and recalculation of all 60 records. No original experiment was rerun to replace timing observations.

## Major revision: new, separately executed experiment

Protocol: protocol/major_revision_protocol.md, written before execution. Four real sklearn datasets: Iris 150×4, Wine 178×13, WDBC 569×30, Digits 1797×64. Seven methods: all-feature SVM, inner-tuned ANOVA, random search, basic GA, crossover-guided GA, mutation-guided GA, and both-guided GA. Guidance operators are controlled adaptations of P002, not exact reproductions of its complete published algorithm. Fixed standardized RBF SVM C=1, gamma=scale; scalar alpha=.9; population12; 64 unique expensive objectives for three datasets, exhaustive15 for Iris; three seeds17/29/43 × five outer × three inner folds. Shared partitions and expensive budgets; ANOVA has fewer candidate objectives, explicitly reported. Inner-training-only guidance/preprocessing, serial rotating method order.

Full run: 420 records, completed in 451.478939 seconds. Actual stdout: logs/major_revision_full.log; manifest and code/environment hashes: Results_and_Graphs/major_revision/manifest.json. Failed first smoke dispatch and its correction are retained in logs/major_revision_smoke_attempt1.log; successful smoke: 28 records. The full run followed the correction.

Audit: **3661 checks, zero failures**, from src/analyze_major_revision.py; reports/major_revision_result_audit.log and Results_and_Graphs/major_revision/audit.json. All 420 accuracy, balanced-accuracy and macro-F1 records were recalculated manually from confusion counts in saved predictions. Checks also cover masks, reduction, component timing identities, objective budgets, classifier-fit counts and saved split boundaries. Arithmetic verification does not independently validate every modeling assumption.

Executed workspace suite: **23 tests passed in1.69s**, reports/major_revision_all_tests.log. Six major-revision tests separately passed in0.99s, reports/major_revision_tests_final.log. They cover guidance mathematics, cached budget/finite space, legal masks, scaler boundaries, saved outputs and a standard-HUX cardinality counterexample. The HUX test examines the premise of P023's bound, not its downloaded implementation.

New portable archive validation is recorded in reports/major_revision_portable_validation.log and reports/major_revision_package_verification.json after extraction; consult those actual results rather than assuming success from this text.

## Reproduction

Use Python3.14 and pinned requirements.txt in an isolated environment. From the project/archive root:

```bash
python -m pip install -r requirements.txt
python src/analyze_major_revision.py
python -m pytest tests -q
python src/plot_major_revision.py
```

For a fresh experiment, first preserve Results_and_Graphs/major_revision/, because this command overwrites its saved records:

```bash
python src/major_experiment.py configs/major_revision_full.yaml
python src/analyze_major_revision.py
python src/plot_major_revision.py
```

The saved datasets and loader descriptions are included. Refit code uses pinned local sklearn loaders; compare data hashes in datasets.json. New timing includes search, final fit and held-out prediction; the original training-only boundary is different. Runtime is hardware-dependent; dependent-fold SD/Jaccard pairs are descriptive, not independent-sample confidence intervals. Four-dataset sign-flip diagnostics (16 assignments) do not support significance claims. No failed full-run record was discarded.
''')
write('Source_Verification_Report.md',f'''# Source verification report

{date}. Current corpus: **15 full-text included studies, six pending, three excluded** among24 primary candidates; three supplied surveys are separate, giving27 registry records. The matrix contains21 relevant primary records, not21 full-text studies. The previous14 included studies and six pending decisions were preserved; P023 is the one new inclusion. P024 is a new regression-only exclusion.

## Verified addition and focused search

P023: Mohammed Ghaith Altarabichi, Slawomir Nowaczyk, Sepideh Pashami, Peyman Sheikholharam Mashhadi, “Fast Genetic Algorithm for feature selection — A qualitative approximation approach,” Expert Systems with Applications211(2023),118528; DOI10.1016/j.eswa.2022.118528. [DOI landing page](https://doi.org/10.1016/j.eswa.2022.118528). Crossref issue year2023 differs from online2022. The actual13-page final journal PDF obtained through its legitimate open arXiv location contains matching title/authors/DOI and a CC-BY statement. All13 pages were read. Full evidence and caveats: evidence/P023_notes.md. Printed code-availability claims are attributed to the paper; source code was not reproduced or independently validated.

Two supplemental Crossref API searches Q21/Q22 returned20 saved records each, with2020–2026 date filters; the second uses Elsevier DOI prefix. These exports are bounded discovery results, not comprehensive database coverage or unique PRISMA totals. Logs/major_revision_crossref_search.json, major_revision_elsevier_search.json and major_revision_fulltext_access.json record discovery/access. OpenAlex metadata was used for legitimate OA locations. No browser UI or paid access was used during this revision. P024's first nine pages establish regression scope; all26 pages were not read and no classification findings are attributed to it.

## Source traceability and unresolved checks

Twenty-three manuscript references are numbered by first citation. The literature-catalog BibTeX also retains pending records; a BibTeX entry does not imply full-text inclusion. The21-paper sample-format matrix has exactly the13 supplied headings and source-specific findings, uncertainty and saved Crossref citation-count dates. Its Abstract column contains original summaries, not copied abstracts.

The author worksheet identifies **29 exact manual checks** with source IDs, DOI/page/table locators, the actual claim and why verification matters. It also contains68 extracted numerical records,240 method fields, manuscript claims, original summaries and expanded results/stability. Important ambiguities include P004 feature-recovery versus classification F1; P003 timing aggregation; P006 repeat counts; P012 accepted-manuscript/demo-code differences; P018 ANN MSE/accuracy semantics; P022 metric labels; and P023 q20 versus q10 and the conditional HUX cardinality premise. The mathematical counterexample for unconstrained HUX is an appraisal, not a reproduction or disproof of P023's empirical results.

P012 uses the41-page accepted manuscript from Loughborough Figshare; pages must refer to that version. P018 uses full journal XML from EuropePMC; section/table locators replace PDF pages. Six pending sources retain NOT VERIFIED method/results fields and do not support unseen empirical claims. No purchase is needed or requested. Source availability bias remains a limitation.

All three supplied surveys already discuss substantial parts of the proposed contribution. See notes/03_survey_overlap_audit.md and manuscriptIII.A. No first-ever, unexplored or publication-novelty claim is established. This is a structured critical review, not an exhaustive systematic review/meta-analysis. The AI source audit is not an independent human second-reviewer verification.
''')
write('Final_Quality_and_Submission_Checklist.md',f'''# Final author-review and submission checklist

{date}. Technical artifacts are assembled and checked. University/journal submission is not approved. Author details and no coauthors are confirmed.

## Mandatory before university submission

- [ ] Independently author the final prose as required by the university. All current manuscript prose/captions remain AI-generated reference material. Keep truthful AI-assistance documentation; changing synonyms is not independent authorship.
- [ ] Complete the **29 Manual_Source_Checks** in Author_Verification_Worksheet.xlsx with decision/date. These identify exact source claims, not a generic request to “verify everything.” Review Numerical_Evidence and Method_Evidence where used in the final student-authored argument.
- [ ] Retain unresolved source caveats or remove stronger claims. Especially check metric targets, repeat denominators, timing boundaries, source-version pages and P023's initialization frequency/conditional bound. Six pending studies must remain outside empirical synthesis.
- [ ] Preserve the correct corpus accounting: original14+newP023=15 included; six pending; three exclusions; three surveys separate. Twenty-one matrix rows do not mean21 full-text studies.
- [ ] Verify interpretation of both experiments. Original60 records retain benign-positive binary F1; expanded420 use macro-F1. Fixed SVM parameters and controlled CGGA adaptations limit generality. Correlated folds/Jaccard pairs cannot be treated as independent trials. Iris is an exhaustive sanity case. No significant universal GA advantage is established.
- [ ] Inspect the exact final student-authored DOCX after revision: citations1–23, captions, tables, equations and readable figure labels; rerender if layout changes. Current18-page version has undergone visual QA, with all23 references together on the final page.
- [ ] Apply actual university formatting/acknowledgement rules and approve the final version. If an authorized similarity report is required, obtain it through approved procedures. Current Turnitin/QuillBot/similarity status: **NOT TESTED**; no percentage is guaranteed. No submission has been made.

## Optional strengthening before future journal submission

1. Broaden question-driven full-text coverage, especially high-dimensional/imbalanced classification, end-to-end cost and nested validation. Legitimate accessible evidence or resolving pending papers would reduce availability bias; paid access and a target count are not mandatory.
2. Expand the survey search beyond the three supplied reviews before asserting a distinct contribution. Their operator, complexity, leakage, benchmarking and GA–SVM discussions overlap directly. P023 already provides amortized cost analysis, so “no prior full-cost accounting” would be false.
3. Consider additional benchmark domains only with a new predefined rationale. Four datasets now improve coverage of size/classes/dimensions but are convenience datasets with at most64 features. High-dimensional/imbalanced data would test a different regime, rather than simply increase the experiment count.
4. Reproduce complete published selectors using verified versions and fair tuning/budgets if algorithm-comparison claims are central. Current operator adaptations isolate guidance components under a common objective; they are not exact reproductions of Zhou/Hua's kNN-based CGGA or P023's CHC_QX. Nested classifier tuning, sensitivity to alpha/budget/discretization and independent multi-dataset uncertainty could strengthen conclusions; no such results are claimed here.
5. Choose a venue after contribution assessment. Verify its current article types, fees, format, data requirements and AI policies. Earlier official-guide observations are dated, not assurances of acceptance/compliance. Obtain independent author verification and expressly approve any submission.

## Focused survey comparison

|Survey|Specific existing contribution|Current project's defensible emphasis|Limit|
|---|---|---|---|
|S01 Aldamani etal2026,10.1016/j.swevo.2026.102318|GA operators Tables4–6pp7/9/11; complexityTable7p12; codeTable8p13; six-method/ten-dataset benchmarkTable11p14.|Page-linked metric/timing/repeat-denominator audit and saved-prediction controlled operator ablation with separate guidance costs.|An experiment, GA taxonomy and complexity comparison already exist. Four convenience datasets do not exceed its breadth or establish novelty.|
|S02 Song etal2024,10.1016/j.swevo.2024.101661|High-dimensional/surrogate costpp9–10; explicit validation leakage§6.1p14 and low-cost design§6.2p14; stabilityp12.|Traceable item-level evidence limitations plus expensive-evaluation versus total-cost comparison.|Leakage, cost and stability are already discussed. This project is narrower across evolutionary families.|
|S03 Moslemi2023,10.1016/j.engappai.2023.107136|GA–SVM Fig5/Eq126p19; hybridsp21; complexityTable4p15; costtradeoffspp24–25.|Focused empirical claim comparability and explicit source-version/access caveats.|Narrower focus alone is not novelty and does not replace the tutorial.|

The manuscript now includes real stability/cost/component analysis and multiple datasets. The original results/figures/archive remain unchanged; new outputs have a separate directory/archive. Publication differentiation remains **NOT ESTABLISHED** and journal acceptance is not guaranteed.
''')
write('Remaining_Issues_and_Resolution_Plan.md','''# Remaining issues and resolution plan

## Mandatory human actions

Independent student authorship under the university's AI-writing restriction; completion of29 source-specific manual worksheet checks; final source/interpretation and institution-format verification; authorized similarity checking if required; approval of the exact submission. Author identity/affiliation/email and absence of coauthors are already confirmed.

## Research limitations retained

Six pending full texts; structured rather than exhaustive search; availability/coding bias;15 included studies; substantial overlap with existing surveys; four convenience datasets (maximum64features); fixed untuned SVM; common-objective operator adaptations rather than full published-method reproductions; dependent repeated folds and size-sensitive stability; timing hardware/order effects; no statistical significance or general algorithm superiority established.

These limitations do not block the technically complete reference/research package but prevent an unqualified publication-ready claim. Further experiments require an explicit question/protocol, not automatic expansion. No purchase, paywall bypass or new browser task is required.
''')
write('Source_and_Result_Audit_Report.md','''# Source and result audit: major revision

See Source_Verification_Report.md for15 included/six pending/three excluded and29 exact manual checks. See Reproducibility_and_Test_Report.md for420 new records,3661 passing saved-output checks and23 passing workspace tests. Original60records and612-check/12-test validation remain distinct and preserved.

New descriptive evidence: both-guided versus basic GA balanced accuracy increases on Wine/WDBC/Digits; the all-feature SVM remains higher on Wine/WDBC, and the Digits difference is small. Guidance costs are larger. Mutation-only supplies much of the descriptive gain; crossover-only is mixed. Jaccard improves with guidance on those datasets but larger masks confound stability. Iris enumerates15masks and cannot distinguish operators. The four-dataset diagnostic does not establish significance. All numerical details derive from saved outputs, not literature values.

P023 demonstrates that computational-cost accounting has prior literature coverage. Its q20 experiment versus q10 bound and unconstrained-HUX cardinality premise are explicitly qualified. No downloaded implementation was executed. Survey overlap remains material; publication novelty is unestablished.

Current DOCX:18pages,4editable tables,8semantic figures (10image objects because original Figure4 has3native Word crops),2native equations,23numbered references. Visual QA and preservation are documented in reports/major_revision_visual_qa.md and major_revision_preservation.json. External similarity checking NOT TESTED; local exact12-token triage is limited and does not certify originality. All AI-written prose requires independent student authorship.
''')
with (R/'Research_Methodology_and_Search_Log.md').open('a') as f:f.write('''\n## Major revision amendment — 9 October 2026\n\nUser requested focused end-to-end cost/leakage synthesis, multiple datasets, guided-GA comparison and stability/uncertainty. Protocol/major_revision_protocol.md predates the full run. Supplemental Q21/Q22 Crossref API exports contain20 returned records each, not exhaustive/unique totals. P023 finaljournal13p was fully read and included; P024 first9p establish regression-only exclusion. Current27registry=3reviews+24candidates, with15included+6pending+3excluded. Previous14included and6pending preserved. New4dataset/7method420record controlled experiment executed separately;3661saved-output checks pass. No browser UI, purchase or invented novelty claim. Detailed sources, deviations and actual execution logs are retained.\n''')
with (R/'AI_Assistance_Record.md').open('a') as f:f.write('''\n## Authorized major revision — 9 October 2026\n\nAI authored the protocol amendment, supplemental public API discovery, P023 fulltext extraction/P024 exclusion, controlled published-operator adaptations,420actual experimental records,manual confusion-count audit,stability/cost/diagnostic analysis,three CSV-derived plots,new manuscript sections/tables/equation and updated matrices/reports. Workspace23tests passed. All current prose including additions remainsAI-generated;no human independent authorship or final approval is claimed. The earlier presentation-stage statement that no expansion occurred describes that earlier stage only:subsequent user major-revision steering authorized the separate expansion. Originalresults/figures/ZIP remainfrozen. No browser UI or paidaccess used. New plots are actual reproducible data visualizations;no AI-image model used. Journal novelty/compliance/acceptance and external similarity scores are not asserted.\n''')
write('reports/major_revision_visual_qa.md','''# Major-revision visual QA

9October2026. Latest Final_Research_Paper.docx rendered to tmp/major_revision_ready/:18page PNGs/PDF. Every current page visually verified: pages unchanged from the inspected prior render were checked by identical PNG hashes; changed pages2/12/13/14/15 plus final17/18 inspected directly. Native equations readable, labels/captions intact, tables fit/repeat headers,23references fill the final reference page. Figure4 uses larger native Word crops; original image remains unchanged. Other new figures are genuine saved-CSV plots. No clipped text/missing glyphs observed.

Workbooks retain editable cells, frozen headers, provenance and missing-evidence markers. Updated Summary15/6/3, expanded results/stability, author expanded tabs and original sheet previews inspected. The separate sample-format workbook retains all13exact headings. Artifact-tool recalculation scans logged zero matching formula errors. Structural verification of all rows/IDs/numeric fields is recorded separately; a preview is not independent verification of scientific claims.
''')
write('README.md','''# GA feature-selection critical review: major revision

Editable manuscript and verified evidence/experiment package for author review. Current21relevant primary matrix records=15fulltext+6pending;3excluded and3surveys separate. University final prose must be independently student-authored; see AI_Assistance_Record.md. Novelty/journal-readiness is not established.

Original results/ and figures/ and Complete_Reproducibility_Package.zip are frozen. New work is Results_and_Graphs/major_revision/ with420records,4datasets,7methods; protocol/major_revision_protocol.md predates execution. Guided methods are controlled adaptations, not exact published implementations.

## Verify saved results and reproduce

Python3.14; isolated environment with requirements.txt. From project root:

```bash
python -m pip install -r requirements.txt
python src/analyze_major_revision.py
python -m pytest tests -q
python src/plot_major_revision.py
```

Audit3661checks/0failures; workspace23testspassed. Extracted portable archive validation is recorded in reports/major_revision_portable_validation.log. It omits source-dependent research tests/PDF redistribution, while retaining18executable tests and both saved-result pools.

To refit, preserve the existing new-results directory first (timing cannot be reproduced exactly), then:

```bash
python src/major_experiment.py configs/major_revision_full.yaml
python src/analyze_major_revision.py
python src/plot_major_revision.py
```

The smoke configuration writes a separate directory. Original experiment can be refit using src/experiment.py and configs/experiment_full.yaml, but would overwrite original results/; no such overwrite was performed. Office builders use bundled runtimes/skills recorded in logs/runtime_paths.md. Do not run legacy src/finalize_reports.py after this revision; it represents earlier counts and reports.

## Deliverables

Final_Research_Paper.docx; Complete_Literature_Matrix.xlsx; separate outputs/01a11ce9-c69d-77d1-86a7-82e828ff3742/Literature_Matrix_Sample_Format.xlsx with13exact sample headings; Author_Verification_Worksheet.xlsx with29specific checks; Research_Paper_References.bib; Research_Methodology_and_Search_Log.md; Experimental_Source_Code/; Results_and_Graphs/; Reproducibility_and_Test_Report.md; Source_Verification_Report.md; Final_Quality_and_Submission_Checklist.md; AI_Assistance_Record.md; Complete_Reproducibility_Package_Major_Revision.zip.

The main matrix has14tabs, author worksheet10tabs. Manuscript references1–23 include only cited records; the broader BibTeX catalog also retains pending sources clearly documented in the matrix. Source PDFs remain in the workspace, not redistributed in the portable archive. Human verification and independent authorship are mandatory; optional publication strengthening is separated in the checklist. No submission, paid purchase, similarity score or guaranteed acceptance.
''')
shutil.copy2(R/'references/literature_catalog.bib',R/'Research_Paper_References.bib')
shutil.copy2(R/'Final_Research_Paper.docx',R/'deliverables/GA_Feature_Selection_Review_Paper.docx')
shutil.copy2(R/'Complete_Literature_Matrix.xlsx',R/'deliverables/GA_Feature_Selection_Literature_Matrix.xlsx')
for name in ['major_ga.py','major_experiment.py','analyze_major_revision.py','plot_major_revision.py','ga.py']:
    shutil.copy2(R/'src'/name,R/'Experimental_Source_Code'/name)
for name in ['major_revision_full.yaml','major_revision_smoke.yaml']:
    shutil.copy2(R/'configs'/name,R/'Experimental_Source_Code'/name)
shutil.copy2(R/'Reproducibility_and_Test_Report.md',R/'Experimental_Source_Code/README.md')
print('Reports, exports and original-file preservation updated.')
