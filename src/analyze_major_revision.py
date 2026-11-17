from pathlib import Path
import json,itertools,hashlib
import numpy as np
import pandas as pd

R=Path(__file__).resolve().parents[1];O=R/'Results_and_Graphs/major_revision'

def jaccard(a,b):
    a=np.asarray(a,dtype=bool);b=np.asarray(b,dtype=bool)
    return float((a&b).sum()/(a|b).sum()) if (a|b).any() else 1.0

def analyze():
    raw=pd.read_csv(O/'raw_metrics.csv');pred=pd.read_csv(O/'predictions.csv');masks=json.loads((O/'masks.json').read_text());ds={x['dataset']:x for x in json.loads((O/'datasets.json').read_text())}
    checks=[]
    def ck(name,ok):checks.append({'check':name,'passed':bool(ok)})
    ck('420 unique complete records',len(raw)==420 and not raw.duplicated(['dataset','method','seed','fold']).any() and raw.groupby(['dataset','method']).size().eq(15).all())
    recalculated=[]
    for row in raw.itertuples():
        p=pred[(pred.dataset==row.dataset)&(pred.method==row.method)&(pred.seed==row.seed)&(pred.fold==row.fold)]
        y=p.truth.to_numpy();z=p.prediction.to_numpy();recalls=[];f1s=[]
        for label in np.unique(y):
            tp=((y==label)&(z==label)).sum();fn=((y==label)&(z!=label)).sum();fp=((y!=label)&(z==label)).sum()
            recalls.append(tp/(tp+fn));f1s.append(2*tp/(2*tp+fn+fp) if 2*tp+fn+fp else 0.)
        vals={'accuracy':float((y==z).mean()),'balanced_accuracy':float(np.mean(recalls)),'macro_f1':float(np.mean(f1s))}
        for metric,value in vals.items():ck(f'{row.dataset}/{row.method}/{row.seed}/{row.fold}/{metric}',np.isclose(getattr(row,metric),value,atol=1e-12))
        mask=next(x['mask'] for x in masks if (x['dataset'],x['method'],x['seed'],x['fold'])==(row.dataset,row.method,row.seed,row.fold))
        ck('mask count',sum(mask)==row.feature_count and len(mask)==ds[row.dataset]['d'])
        ck('reduction',np.isclose(row.feature_reduction_pct,100*(1-sum(mask)/len(mask))))
        ck('pipeline timing identity',np.isclose(row.pipeline_seconds,row.search_seconds+row.fit_seconds+row.predict_seconds))
        ck('search component identity',np.isclose(row.search_seconds,row.guidance_preprocess_seconds+row.objective_seconds+row.proposal_overhead_seconds,atol=1e-8))
        ck('fit budget',row.inner_classifier_fits==3*row.unique_evaluations)
        recalculated.append({'dataset':row.dataset,'method':row.method,'seed':row.seed,'fold':row.fold,**vals})
    search=raw[raw.method.isin(['random','basic_ga','cgco_ga','cgmo_ga','cgga_adapted'])]
    for key,g in search.groupby(['dataset','seed','fold']):ck(str(key)+'budget matched',g.unique_evaluations.nunique()==1 and g.unique_evaluations.iloc[0]==min(64,2**ds[key[0]]['d']-1))
    for s in json.loads((O/'splits.json').read_text()):
        tr=set(s['train']);te=set(s['test']);ck('outer split',not tr&te and len(tr|te)==ds[s['dataset']]['n'])
        for i in s['inner']:ck('inner split',set(i['train'])|set(i['valid'])==tr and not set(i['train'])&set(i['valid']) and not (set(i['train'])|set(i['valid']))&te)
    metrics=['accuracy','balanced_accuracy','macro_f1','feature_count','feature_reduction_pct','guidance_preprocess_seconds','objective_seconds','proposal_overhead_seconds','search_seconds','fit_seconds','predict_seconds','pipeline_seconds','unique_evaluations','inner_classifier_fits','cheap_guidance_calls','diversity_injections']
    summary=[]
    for (dataset,method),g in raw.groupby(['dataset','method']):
        for metric in metrics:summary.append({'dataset':dataset,'method':method,'metric':metric,'mean':g[metric].mean(),'sd':g[metric].std(ddof=1),'n':len(g),'interpretation':'Descriptive over dependent repeated folds;not independent-trial CI'})
    stability=[]
    for dataset,method in raw.groupby(['dataset','method']).groups:
        ms=[x['mask'] for x in masks if x['dataset']==dataset and x['method']==method];vals=[jaccard(a,b) for a,b in itertools.combinations(ms,2)]
        stability.append({'dataset':dataset,'method':method,'pairwise_jaccard_mean':np.mean(vals),'sd':np.std(vals,ddof=1),'pairs':len(vals),'note':'Overlapping training samples;Jaccard sensitive to subset size'})
    seedmeans=raw.groupby(['dataset','method','seed'])[metrics].mean().reset_index()
    paired=[];means=raw.groupby(['dataset','method']).balanced_accuracy.mean().unstack()
    for method in ['cgco_ga','cgmo_ga','cgga_adapted','random']:
        delta=means[method]-means.basic_ga;observed=abs(delta.mean());distribution=[abs(np.mean(delta.to_numpy()*signs)) for signs in itertools.product([-1,1],repeat=4)]
        paired.append({'method':method,'comparator':'basic_ga','mean_dataset_difference':delta.mean(),'exact_sign_flip_p':np.mean(np.array(distribution)>=observed-1e-14),'datasets':4,'patterns':16,'scope':'Diagnostic under dataset-exchangeability assumption;Iris sanity included;no0.05 significance possible'})
    for name,frame in [('summary_tidy',pd.DataFrame(summary)),('stability',pd.DataFrame(stability)),('seed_means',seedmeans),('paired_dataset_diagnostics',pd.DataFrame(paired)),('recomputed_metrics',pd.DataFrame(recalculated)),('audit_checks',pd.DataFrame(checks))]:frame.to_csv(O/(name+'.csv'),index=False)
    audit={'checks':len(checks),'failures':sum(not c['passed'] for c in checks),'status':'VERIFIED' if all(c['passed'] for c in checks) else 'FAILED','raw_sha256':hashlib.sha256((O/'raw_metrics.csv').read_bytes()).hexdigest(),'prediction_sha256':hashlib.sha256((O/'predictions.csv').read_bytes()).hexdigest()};(O/'audit.json').write_text(json.dumps(audit,indent=2));print(audit)
    if audit['failures']:raise SystemExit(1)

if __name__=='__main__':analyze()
