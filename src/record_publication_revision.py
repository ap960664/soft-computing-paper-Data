"""Document publication assessment, figure QA and immutable result checks."""
from pathlib import Path
import json,hashlib,shutil,datetime
from openpyxl import load_workbook
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
A=R/'reports/pre_publication_revision';A.mkdir(exist_ok=True)
for name in ['Complete_Reproducibility_Package_Major_Revision.zip','Author_Verification_Worksheet.xlsx']:
    if not (A/name).exists():shutil.copy2(R/name,A/name)
old=R/'deliverables/GA_Feature_Selection_Review_Paper.docx'
if not (A/'Final_Research_Paper.docx').exists():shutil.copy2(old,A/'Final_Research_Paper.docx')
before=json.loads((R/'reports/author_review_baseline_hashes.json').read_text())
preservation={p:sha(R/p)==h for p,h in before.items() if p.startswith(('results/','figures/')) or p=='Complete_Reproducibility_Package.zip'}
assert all(preservation.values())
with __import__('zipfile').ZipFile(A/'Complete_Reproducibility_Package_Major_Revision.zip') as z:
    prefix='Major_Revision_Reproducibility_Package/'
    experimental={str(p.relative_to(R)):sha(p)==hashlib.sha256(z.read(prefix+str(p.relative_to(R)))).hexdigest() for p in (R/'Results_and_Graphs/major_revision').rglob('*') if p.is_file()}
assert all(experimental.values())
author=load_workbook(R/'Author_Verification_Worksheet.xlsx',read_only=True,data_only=True)
manual=list(author['Manual_Source_Checks'].values)[1:]
assert len(manual)==29 and all(x[6]=='PENDING' for x in manual)
q=(R/'Results_and_Graphs/publication_revision/provenance.json')
figures=json.loads(q.read_text());assert len(figures['quality_rows'])==15
render=R/'tmp/publication_docx_qa';previous=R/'tmp/major_revision_ready'
pages=sorted(render.glob('page-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
changed=[p.name for p in pages if sha(p)!=sha(previous/p.name)]
assert changed==[f'page-{i}.png' for i in range(4,11)] and len(pages)==18
record={'date':'2026-10-09','docx_pages':18,'changed_pages_visually_inspected':changed,'other_pages_identical_to_previously_inspected_render':True,'all_current_pages_visually_verified':True,'new_figures':'27 registry records; 15 included quality rows; both PNG/SVG generated from logged evidence','experimental_files_unchanged':experimental,'legacy_files_unchanged':preservation,'manual_checks_outstanding':29,'author_worksheet_sha256_unchanged':sha(R/'Author_Verification_Worksheet.xlsx')==sha(A/'Author_Verification_Worksheet.xlsx'),'docx_sha256':sha(R/'Final_Research_Paper.docx'),'recommended_title_is_proposal_only':True,'external_similarity':'NOT TESTED','local_exact_12_token_flags':0,'publication_novelty':'NOT ESTABLISHED'}
(R/'reports/publication_revision_qa.json').write_text(json.dumps(record,indent=2))
(R/'reports/publication_revision_visual_qa.md').write_text('''# Publication figure/document QA

9 October 2026. Updated selection/reporting-quality figures visually inspected as standalone PNGs and in the latest18-page DOCX render, tmp/publication_docx_qa/. Seven changed pages4–10 inspected directly;11 other pages byte-identical to the previously inspected render. Figure2 shows27=3+(15+6+3); Figure3 includes all15studyIDs and a readable categorical legend. No clipped labels, broken captions or table continuation problems observed. Experimental figures/results unchanged. The final reference page remains unchanged. Current exact receipts are in publication_revision_qa.json; earlier visual reports describe earlier artifact versions.
''')
shutil.copy2(R/'Final_Research_Paper.docx',old)
shutil.copy2(R/'src/update_publication_figures.py',R/'Experimental_Source_Code/update_publication_figures.py')
with (R/'AI_Assistance_Record.md').open('a') as f:f.write('''\n## Publication-focused assessment and corpus-figure update — 9 October 2026\n\nAI prepared Publication_Positioning_and_Improvement_Plan.md, including a recommended title and source-page comparisons against S01/P002. It generated the final27-record selection figure and15-study reporting heatmap from logged evidence, updated their manuscript captions/paths and rendered/visually checked the DOCX. Valid experimental records and plots were preserved. No additional benchmark, parameter tuning, inference claim, browser UI, purchase or submission was performed. The29 author checks remain outstanding; reviewed artifacts do not establish independent student authorship or final source approval. All plan/manuscript prose remains AI-generated. Similarity services remain NOT TESTED; limited local12-token screen0flags is not an originality percentage.\n''')
with (R/'notes/03_survey_overlap_audit.md').open('a') as f:f.write('''\n## Publication-focused amendment — 9 October 2026\n\nThe earlier14-study/no-expansion paragraph describes a prior stage. Current15included+6pending follow the legitimate P023 addition; separate420records now exist. Publication_Positioning_and_Improvement_Plan.md gives the focused S01/P002 comparison. CGGA already has check-count sensitivity Table2p6, convergence curves Fig3p7, high-dimensional artificial/real benchmarks and complexity including SU setup. It cannot be presented as lacking those contributions. The current nested SVM/scalar-objective/operator adaptation and cost decomposition are differences, not established novelty. Table6 real-dataset dimensions are on physicalp9. No new experiment or browser task for this assessment.\n''')
with (R/'Reproducibility_and_Test_Report.md').open('a') as f:f.write('''\n## Latest publication-focused export\n\n9 October2026. New corpus figures show27registered/15included counts and are saved under Results_and_Graphs/publication_revision/. The latest DOCX and publication assessment are included in the refreshed major-revision archive, together with all420raw rows,predictions,masks,configuration/code,timing fields and3661check outcomes. Experimental files remain byte-identical. Current archive CRC/hash/extraction validation is reports/major_revision_package_verification.json and major_revision_portable_validation.log. No full experimental refit was performed. The29 author checks remain visible and pending.\n''')
with (R/'AGENT_PROGRESS.md').open('a') as f:f.write('''\n## Publication-focused revision — 9 October 2026\n\nFinal27-record selection flow and15-study reporting audit generated and integrated;18-pageDOCX visuallychecked (changed4–10;othersidentical). Focused publication plan and proposedtitle saved; currentposition structuredcriticalreview withcontrolledbenchmarking. CGGA already covershigh-dimensionaldata,checksensitivity andSUsetupcomplexity. High-dimensionalregimes/sensitivity/dataset-levelinference areconditionalrequirements forstronger empiricalclaims,not executedadditions. Originalandexpandedexperimentalfiles unchanged;29manualcheckspending;AIrecordupdated;externalsimilarityNOTTESTED. NewlatestZIPincludescomplete420recordevidence and3661checks;validationreceipt recordsactualextractedrun. Submissionreadiness/noveltynotclaimed.\n''')
print('Publication QA, preservation and authorship records saved.')
