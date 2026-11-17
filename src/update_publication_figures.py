"""Final-corpus evidence figures. Experimental arrays and plots are immutable."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
R=Path(__file__).resolve().parents[1];O=R/'Results_and_Graphs/publication_revision';O.mkdir(exist_ok=True)
counts=json.loads((R/'logs/selection_counts.json').read_text())
assert counts['registry_records']==27 and counts['primary_candidates']==24
assert counts['included_primary']==15 and counts['pending_primary']==6 and counts['excluded_primary']==3
fig,ax=plt.subplots(figsize=(8.5,3.5));ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
boxes=[(.5,.85,'Registered records\n27'),(.24,.56,'Secondary surveys\n3 — separate background'),(.73,.56,'Primary candidates\n24'),(.42,.17,'Included full texts\n15'),(.70,.17,'Pending full texts\n6'),(.94,.17,'Excluded\n3')]
for x,y,label in boxes:
    ax.text(x,y,label,ha='center',va='center',fontsize=11,bbox={'boxstyle':'round,pad=.5','facecolor':'#edf2f7','edgecolor':'#64748b'})
for a,b in [((.5,.77),(.24,.66)),((.5,.77),(.73,.66)),((.73,.46),(.42,.28)),((.73,.46),(.70,.28)),((.73,.46),(.94,.28))]:
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'#475569'})
ax.set_title('Final logged study selection: 27 = 3 + (15 + 6 + 3)',fontsize=12,pad=10)
fig.tight_layout()
for ext in ['png','svg']:fig.savefig(O/f'selection_flow_final.{ext}',dpi=300,bbox_inches='tight')
plt.close(fig)
q=pd.read_csv(R/'evidence/evidence_quality.csv');criteria=list(json.loads((R/'evidence/quality_definitions.json').read_text()))
assert len(q)==15 and q.Study_ID.is_unique and 'P023' in q.Study_ID.values
lookup={'Yes':2,'No':0,'Unclear':1,'Not reported':3}
a=np.array([[lookup[row[c]] for c in criteria] for _,row in q.iterrows()])
colors=['#ef4444','#fbbf24','#14b8a6','#cbd5e1']
fig,ax=plt.subplots(figsize=(8.5,5.5))
ax.imshow(a,aspect='auto',cmap=ListedColormap(colors),vmin=-.5,vmax=3.5)
ax.set_yticks(range(len(q)),q.Study_ID,fontsize=11)
ax.set_xticks(range(len(criteria)),['Dataset\nsource','Test\nseparation','Train-only\npreprocess','Baselines','GA\nsettings','Repeats/\nvariation','Timing\nboundary','Hardware','Code/\ndata'],fontsize=10)
marks={'Yes':'Y','No':'N','Unclear':'?','Not reported':'NR'}
for i,(_,row) in enumerate(q.iterrows()):
    for j,c in enumerate(criteria):ax.text(j,i,marks[row[c]],ha='center',va='center',fontsize=10)
ax.set_title('Reporting audit of all 15 included full-text primary studies',fontsize=12,pad=12)
fig.legend(handles=[Patch(facecolor=colors[i],label=x) for i,x in enumerate(['N: contrary design','?: unclear','Y: explicit','NR: not reported'])],loc='lower center',ncol=4,fontsize=9,frameon=False)
fig.tight_layout(rect=[0,.06,1,1])
for ext in ['png','svg']:fig.savefig(O/f'evidence_quality_final.{ext}',dpi=300,bbox_inches='tight')
plt.close(fig)
inputs=['logs/selection_counts.json','evidence/evidence_quality.csv','evidence/quality_definitions.json']
(O/'provenance.json').write_text(json.dumps({'date':'2026-10-09','selection_counts':counts,'quality_rows':q.Study_ID.tolist(),'source_sha256':{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in inputs},'note':'Derived corpus figures, not experimental metrics. Original evidence/experiment figures retained separately. Codes are reporting evidence, not algorithm quality; source ambiguities require author verification.'},indent=2))
print('Final 27-record flow and 15-study reporting heatmap generated.')
