from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate(results='results',output='figures'):
    out=Path(output);out.mkdir(exist_ok=True);r=pd.read_csv(Path(results)/'raw_metrics.csv');c=pd.read_csv(Path(results)/'ga_convergence.csv')
    plt.rcParams.update({'font.size':10,'figure.dpi':150})
    order=['all_svm','filter_svm','ga_svm','random_svm'];labels=['All features','ANOVA filter','GA search','Random search']
    fig,axes=plt.subplots(1,3,figsize=(11,3.6))
    for ax,metric,ylabel in zip(axes,['balanced_accuracy','feature_count','total_train_seconds'],['Balanced accuracy (proportion)','Selected features (count)','Selection + final fit (seconds)']):
        groups=[r.loc[r.method==m,metric] for m in order]
        ax.bar(labels,[g.mean() for g in groups],yerr=[g.std(ddof=1) for g in groups],capsize=3,color=['#64748b','#0891b2','#2563eb','#b45309'])
        ax.set_ylabel(ylabel);ax.tick_params(axis='x',rotation=25);ax.spines[['top','right']].set_visible(False)
        if metric=='balanced_accuracy':ax.set_ylim(0,1)
    fig.tight_layout();fig.savefig(out/'method_comparison.png',dpi=300);fig.savefig(out/'method_comparison.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.5,3.5))
    g=c.groupby('generation').best_fitness.agg(['mean','std']);ax.plot(g.index,g['mean']);ax.fill_between(g.index,g['mean']-g['std'],g['mean']+g['std'],alpha=.2)
    ax.set(xlabel='Generation',ylabel='Training-side scalar fitness',title='GA convergence: mean and descriptive SD');fig.tight_layout();fig.savefig(out/'ga_convergence.png',dpi=300);plt.close(fig)
    (out/'provenance.md').write_text('method_comparison: results/raw_metrics.csv; mean and sample SD across repeated outer folds. ga_convergence: results/ga_convergence.csv; training-side scalar fitness, not test accuracy. No inferential confidence intervals.\n')

if __name__=='__main__':generate()
