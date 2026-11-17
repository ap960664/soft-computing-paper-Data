from pathlib import Path
import ast,shutil,json,hashlib,zipfile
import numpy as np,pandas as pd
from sklearn.datasets import load_breast_cancer
R=Path(__file__).resolve().parents[1];S=R/'tmp/repro_package';S.mkdir(exist_ok=True)
for d in ['src','configs','results','figures','reports','tests','data']: (S/d).mkdir(exist_ok=True)
for name in ['ga.py','experiment.py','plot_results.py','plot_evidence.py','audit_results.py']:shutil.copy2(R/'src'/name,S/'src'/name)
for p in (R/'configs').glob('*.yaml'):shutil.copy2(p,S/'configs'/p.name)
shutil.copy2(R/'requirements.txt',S/'requirements.txt')
for p in (R/'results').iterdir():
 if p.is_file():shutil.copy2(p,S/'results'/p.name)
for p in (R/'figures').iterdir():
 if p.is_file():shutil.copy2(p,S/'figures'/p.name)
for name in ['result_audit.json','result_audit_checks.csv','recomputed_prediction_metrics.csv','source_version_audit.md','originality_and_similarity_review.md']:
 if (R/'reports'/name).exists():shutil.copy2(R/'reports'/name,S/'reports'/name)
source=(R/'tests/test_project.py').read_text();tree=ast.parse(source);keep=[]
for n in tree.body:
 if not isinstance(n,ast.FunctionDef) or n.lineno<86 or n.name=='test_scalar_fitness_matches_manually_recomputed_inner_predictions':keep.append(ast.get_source_segment(source,n))
(S/'tests/test_experiments.py').write_text('\n\n'.join(keep)+'\n');(S/'reports/workspace_integration_tests_source.txt').write_text(source)
data=load_breast_cancer();np.savez_compressed(S/'data/wdbc_snapshot.npz',X=data.data,y=data.target,feature_names=data.feature_names,target_names=data.target_names)
actual=hashlib.sha256(data.data.tobytes()+data.target.tobytes()).hexdigest();assert actual==json.loads((R/'results/experiment_manifest.json').read_text())['data_hash']
(S/'data/PROVENANCE.md').write_text('WDBC snapshot exactly matches original experiment data_hash. UCI DOI10.24432/C5DW2B, CC BY4.0 verified9October2026. Retrieved via installed scikit-learn load_breast_cancer,569x30,malignant0/benign1,no missing values. Original description results/dataset_description.txt. Original authors William Wolberg,Olvi Mangasarian,Nick Street,W.Street;official citation and license:https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic .\n')
selected=pd.read_csv(R/'results/selected_features.csv');masks=[]
for (method,seed,fold),g in selected.groupby(['method','seed','fold']):
 mask=[0]*30
 for j in g.feature_index:mask[int(j)]=1
 masks.append({'method':method,'seed':int(seed),'fold':int(fold),'mask':mask})
(S/'results/selected_masks.json').write_text(json.dumps(masks,indent=2));shutil.copy2(S/'results/selected_masks.json',R/'results/selected_masks.json')
(S/'README.md').write_text('''# Complete reproducibility package —9 October2026

Run from the extracted package root. Original metrics/predictions are preserved in results/. Python3.14 and exact dependencies are recorded. The executed algorithm is a custom scalarized binary GA, not a reimplementation of the14 reviewed methods. Four methods ×3 seeds ×5 outer folds =60 records. F1/precision/recall positive class is benign(1). Folds overlap; SD is descriptive.

```
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/audit_results.py
.venv/bin/python -m pytest tests -q
.venv/bin/python src/plot_results.py
```

To rerun the actual experiment while retaining original measurements:

```
.venv/bin/python -c "import shutil;shutil.copytree('results','original_results')"
.venv/bin/python src/experiment.py configs/experiment_fast.yaml
.venv/bin/python src/experiment.py configs/experiment_full.yaml
.venv/bin/python src/plot_results.py
.venv/bin/python src/audit_results.py
```

Full execution overwrites results/ metrics. Keep original_results/ for the comparison. Smoke config writes results/smoke/. Wall time varies; score/mask reproduction depends on pinned environment. experiment.py uses sklearn's bundled WDBC; data/wdbc_snapshot.npz preserves the exact original inputs and hash.

Contents: actual source,requirements,configs,seeds,dataset snapshot/provenance,raw scores,predictions,selected feature masks/indices,split indices,convergence,timing logs,figure scripts,plots,audit computations and actual test logs. Twelve portable experiment tests are included and executed in this extracted layout. The16-test full-workspace suite also checks source PDFs and DOCX;its complete source/log is retained as documentation,not falsely claimed runnable without the original research workspace. plot_evidence.py requires the research evidence CSVs;those are provided below during final packaging.

Publisher PDFs,author code and the thesis are not redistributed. They are accessed in the research workspace with version/rights evidence. Author worksheet and audit report support human source verification. University prohibits AI-authored final prose;independent student authorship and approval remain necessary.\n''')
for d in ['evidence','logs']:
 (S/d).mkdir(exist_ok=True)
 for p in (R/d).glob('*.csv'):shutil.copy2(p,S/d/p.name)
for f in ['logs/selection_counts.json','evidence/quality_definitions.json']:shutil.copy2(R/f,S/f)
print('Prepared portable package',S)
