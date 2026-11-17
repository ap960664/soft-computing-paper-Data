"""Independent saved-output audit: no experiment is rerun or overwritten."""
from pathlib import Path
import json,hashlib,datetime
import pandas as pd
import numpy as np
R=Path(__file__).resolve().parents[1];out=R/'reports';raw=pd.read_csv(R/'results/raw_metrics.csv');pred=pd.read_csv(R/'results/test_predictions.csv');sel=pd.read_csv(R/'results/selected_features.csv');summary=pd.read_csv(R/'results/summary_metrics.csv');splits=json.loads((R/'results/split_indices.json').read_text());checks=[]
def check(label,ok,detail):
 checks.append({'check':label,'status':'VERIFIED' if bool(ok) else 'FAILED','detail':detail})
check('60 unique method-seed-fold records',len(raw)==60 and not raw.duplicated(['method','seed','fold']).any() and raw.groupby('method').size().eq(15).all(),'4 methods x 3 seeds x 5 folds;15 records per method')
check('No recorded method failures',raw.error.fillna('').eq('').all(),'Saved raw error column')
recomputed=[]
for _,r in raw.iterrows():
 p=pred[(pred.method==r.method)&(pred.seed==r.seed)&(pred.fold==r.fold)];y=p.truth.to_numpy();z=p.prediction.to_numpy();tp=((y==1)&(z==1)).sum();tn=((y==0)&(z==0)).sum();fp=((y==0)&(z==1)).sum();fn=((y==1)&(z==0)).sum()
 v={'accuracy':(tp+tn)/len(y),'balanced_accuracy':.5*(tp/(tp+fn)+tn/(tn+fp)),'precision':tp/(tp+fp),'recall':tp/(tp+fn),'f1':2*tp/(2*tp+fp+fn)}
 for name,value in v.items():check(f'{r.method}/{r.seed}/{r.fold} {name}',abs(value-r[name])<1e-12,'Manually recomputed confusion counts;benign=1')
 sf=sel[(sel.method==r.method)&(sel.seed==r.seed)&(sel.fold==r.fold)];check(f'{r.method}/{r.seed}/{r.fold} features',len(sf)==r.feature_count and sf.feature_index.nunique()==len(sf),'Saved selected-feature indices')
 check(f'{r.method}/{r.seed}/{r.fold} reduction',abs(100*(1-len(sf)/30)-r.feature_reduction_pct)<1e-10,'Recomputed denominator30')
 check(f'{r.method}/{r.seed}/{r.fold} timing sum',abs(r.search_seconds+r.fit_seconds-r.total_train_seconds)<1e-10,'Arithmetic audit of saved timings;original wall clock not independently remeasured')
 split=next(s for s in splits if s['seed']==r.seed and s['fold']==r.fold);check(f'{r.method}/{r.seed}/{r.fold} prediction coverage',set(p['index'])==set(split['test']) and len(p)==len(split['test']),'Exact recorded outer test indices')
 recomputed.append({'method':r.method,'seed':r.seed,'fold':r.fold,**v,'feature_count':len(sf),'feature_reduction_pct':100*(1-len(sf)/30)})
for _,r in summary.iterrows():
 vals=raw.loc[raw.method==r.method,r.metric].to_numpy();mean=np.sum(vals)/len(vals);sd=np.sqrt(np.sum((vals-mean)**2)/(len(vals)-1));check(f'{r.method} summary {r.metric}',abs(mean-r['mean'])<1e-10 and abs(sd-r.sd)<1e-10 and len(vals)==r.n,'Mean and sample SD ddof1 recomputed from raw CSV')
for s in splits:
 tr=set(s['train']);te=set(s['test']);check(f"Split {s['seed']}/{s['fold']}",not tr&te and len(tr|te)==569 and all(set(i['train_global'])|set(i['valid_global'])==tr and not set(i['train_global'])&set(i['valid_global']) for i in s['inner']),'Inner training/validation confined to outer training')
for key,g in raw[raw.method.isin(['ga_svm','random_svm'])].groupby(['seed','fold']):check(f'GA/random budget {key}',g.unique_objective_evaluations.nunique()==1 and g.inner_classifier_fits.nunique()==1,'Unique evaluation budget and inner fits matched')
pd.DataFrame(recomputed).to_csv(out/'recomputed_prediction_metrics.csv',index=False);pd.DataFrame(checks).to_csv(out/'result_audit_checks.csv',index=False)
record={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'VERIFIED' if all(c['status']=='VERIFIED' for c in checks) else 'FAILED','checks':len(checks),'failures':sum(c['status']=='FAILED' for c in checks),'scope':'Separate recomputation script, same AI reviewer;not independent human validation','inputs_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'results').glob('*') if p.is_file()}};(out/'result_audit.json').write_text(json.dumps(record,indent=2));print(record['status'],len(checks),'checks',record['failures'],'failures')
if record['failures']:raise SystemExit(1)
