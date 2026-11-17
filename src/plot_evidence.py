from pathlib import Path
import json,pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

R=Path(__file__).resolve().parents[1];out=R/'figures'
q=pd.read_csv(R/'evidence/evidence_quality.csv');criteria=list(json.loads((R/'evidence/quality_definitions.json').read_text()))
lookup={'Yes':2,'No':0,'Unclear':1,'Not reported':3};a=np.array([[lookup[q.loc[i,c]] for c in criteria] for i in q.index])
fig,ax=plt.subplots(figsize=(10,5.5));ax.imshow(a,aspect='auto',cmap=ListedColormap(['#ef4444','#fbbf24','#14b8a6','#cbd5e1']),vmin=-.5,vmax=3.5)
ax.set_yticks(range(len(q)),q.Study_ID);ax.set_xticks(range(len(criteria)),['Dataset\nsource','Test\nseparation','Train-only\npreprocess','Baselines','GA\nsettings','Repeats/\nvariation','Timing\nboundary','Hardware','Code/\ndata'],fontsize=9)
for i in range(len(q)):
    for j,c in enumerate(criteria):ax.text(j,i,{'Yes':'Y','No':'N','Unclear':'?','Not reported':'NR'}[q.loc[i,c]],ha='center',va='center',fontsize=9)
ax.set_title(f'Reporting audit of {len(q)} included full-text primary studies\nY explicit; N contrary design; ? unclear; NR not reported',fontsize=11);fig.tight_layout();fig.savefig(out/'evidence_quality.png',dpi=300);plt.close(fig)
counts=json.loads((R/'logs/selection_counts.json').read_text())
fig,ax=plt.subplots(figsize=(7,3));ax.axis('off');labels=[f"Registered records: {counts['registry_records']}",f"Secondary reviews: {counts['secondary_reviews']} (separate)",f"Primary candidates: {counts['primary_candidates']}",f"Included: {counts['included_primary']} | Pending: {counts['pending_primary']} | Excluded: {counts['excluded_primary']}"]
for i,t in enumerate(labels):ax.text(.5,.9-i*.24,t,ha='center',bbox=dict(boxstyle='round,pad=.5',facecolor='#edf2f7',edgecolor='#64748b'),fontsize=12)
ax.set_title('Logged study selection, not a PRISMA flow');fig.tight_layout();fig.savefig(out/'selection_flow.png',dpi=300);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,3));ax.axis('off')
boxes=[('Outer training data',.10),('Inner-fold pipelines\nEvaluate masks',.36),('GA operators\nSelect final mask',.62),('Outer test data\nEvaluate once',.88)]
for t,x in boxes:ax.text(x,.5,t,ha='center',va='center',bbox=dict(boxstyle='round,pad=.7',facecolor='#e2e8f0'),fontsize=10)
for x in [.22,.48,.74]:ax.annotate('',xy=(x+.07,.5),xytext=(x-.04,.5),arrowprops=dict(arrowstyle='->'))
ax.text(.5,.15,'All scaling and filter selection are fitted within the relevant training fold',ha='center',fontsize=10);fig.tight_layout();fig.savefig(out/'ga_pipeline.png',dpi=300);plt.close(fig)
(out/'evidence_plot_provenance.md').write_text('evidence_quality.png: evidence/evidence_quality.csv, definitions in quality_definitions.json. selection_flow.png: logs/selection_counts.json. ga_pipeline.png: original conceptual diagram reflecting executed code, not experimental evidence.\n')
