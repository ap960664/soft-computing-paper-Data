from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parents[1];O=R/'Results_and_Graphs/major_revision';F=O/'figures';F.mkdir(exist_ok=True)
raw=pd.read_csv(O/'raw_metrics.csv');st=pd.read_csv(O/'stability.csv')
datasets=['iris','wine','breast_cancer','digits'];names=['Iris: exhaustive sanity','Wine','WDBC','Digits']
methods=['all_svm','anova','random','basic_ga','cgco_ga','cgmo_ga','cgga_adapted'];labels=['All','ANOVA','Random','Basic','CGCO','CGMO','Both']
plt.rcParams.update({'font.size':12,'axes.titlesize':13})
fig,axes=plt.subplots(2,2,figsize=(9,6.8))
for ax,dataset,title in zip(axes.flat,datasets,names):
    g=raw[raw.dataset==dataset].groupby('method').balanced_accuracy
    means=g.mean().reindex(methods);sd=g.std(ddof=1).reindex(methods)
    ax.errorbar(range(7),means,yerr=sd,fmt='o',capsize=3,color='#1d4ed8')
    ax.set_xticks(range(7),labels,rotation=30);ax.set_ylim(.85,1.02);ax.set_title(title);ax.set_ylabel('Balanced accuracy');ax.grid(axis='y',alpha=.2)
fig.tight_layout();fig.savefig(F/'performance.png',dpi=300);fig.savefig(F/'performance.svg');plt.close(fig)
fig,axes=plt.subplots(2,2,figsize=(9,7))
components=[('objective_seconds','Inner evaluator','#2563eb'),('guidance_preprocess_seconds','Guidance setup','#f59e0b'),('proposal_overhead_seconds','Proposal overhead','#7c3aed')]
for ax,dataset,title in zip(axes.flat,datasets,names):
    g=raw[raw.dataset==dataset].groupby('method').mean(numeric_only=True).reindex(methods);bottom=np.zeros(7)
    for metric,label,color in components:
        ax.bar(range(7),g[metric],bottom=bottom,label=label,color=color);bottom+=g[metric].to_numpy()
    last=g.fit_seconds+g.predict_seconds;ax.bar(range(7),last,bottom=bottom,label='Final fit + predict',color='#64748b')
    ax.set_xticks(range(7),labels,rotation=30);ax.set_ylabel('Pipeline seconds');ax.set_title(title)
handles,legend=axes[0,0].get_legend_handles_labels();fig.legend(handles,legend,ncol=2,loc='lower center',fontsize=11)
fig.tight_layout(rect=(0,.09,1,1));fig.savefig(F/'cost_components.png',dpi=300);fig.savefig(F/'cost_components.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.3));a=st.pivot(index='dataset',columns='method',values='pairwise_jaccard_mean').reindex(index=datasets,columns=methods).to_numpy()
im=ax.imshow(a,vmin=0,vmax=1,cmap='Blues',aspect='auto')
for i in range(4):
    for j in range(7):ax.text(j,i,f'{a[i,j]:.3f}',ha='center',va='center',color='white' if a[i,j]>.65 else '#111827')
ax.set_xticks(range(7),labels);ax.set_yticks(range(4),['Iris','Wine','WDBC','Digits']);ax.set_title('Mean pairwise feature-mask Jaccard overlap');fig.colorbar(im,ax=ax,fraction=.035,pad=.025)
fig.tight_layout();fig.savefig(F/'stability.png',dpi=300);fig.savefig(F/'stability.svg');plt.close(fig)
(F/'provenance.md').write_text('performance/cost:major_revision/raw_metrics.csv;stability:major_revision/stability.csv. Performance points show mean andsampleSD over15dependentfolds;axis focuses0.85–1.02. Costs aremean savedobservationaltimings andinclude setup/evaluation/proposal/finalfit/prediction. Jaccard describes105dependentmaskpairs,is cardinality-sensitive,andall-feature1is trivial. Original figures/ files were not changed.\n')
print('Saved three expanded CSV-driven figures')
