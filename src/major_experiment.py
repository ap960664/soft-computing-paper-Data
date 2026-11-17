from pathlib import Path
import json,time,sys,platform,hashlib,importlib.metadata
import numpy as np
import pandas as pd
import yaml
from sklearn.datasets import load_iris,load_wine,load_breast_cancer,load_digits
from sklearn.model_selection import StratifiedKFold,cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest,f_classif
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score,balanced_accuracy_score,f1_score
from ga import model
from major_ga import Guidance,TimedFitness,budget_search

LOADERS={'iris':load_iris,'wine':load_wine,'breast_cancer':load_breast_cancer,'digits':load_digits}
METHODS=['all_svm','anova','random','basic_ga','cgco_ga','cgmo_ga','cgga_adapted']

def run(path):
    cfg=yaml.safe_load(Path(path).read_text());out=Path(cfg['output']);out.mkdir(parents=True,exist_ok=True)
    (out/'data').mkdir(exist_ok=True);start=time.time();rows=[];pred=[];masks=[];splitlog=[];convergence=[];datasets=[]
    for name in cfg['datasets']:
        data=LOADERS[name]();X,y=data.data,data.target;d=X.shape[1]
        np.savez_compressed(out/'data'/f'{name}.npz',X=X,y=y,feature_names=data.feature_names)
        (out/'data'/f'{name}_description.txt').write_text(data.DESCR)
        datasets.append({'dataset':name,'n':len(y),'d':d,'classes':len(np.unique(y)),'class_counts':{str(k):int(sum(y==k)) for k in np.unique(y)},'sha256':hashlib.sha256(X.tobytes()+y.tobytes()).hexdigest(),'loader':LOADERS[name].__name__})
        for seed in cfg['seeds']:
            for fold,(tr,te) in enumerate(StratifiedKFold(cfg['outer_folds'],shuffle=True,random_state=seed).split(X,y),1):
                inner=list(StratifiedKFold(cfg['inner_folds'],shuffle=True,random_state=seed+fold).split(X[tr],y[tr]))
                splitlog.append({'dataset':name,'seed':seed,'fold':fold,'train':tr.tolist(),'test':te.tolist(),'inner':[{'train':tr[a].tolist(),'valid':tr[b].tolist()} for a,b in inner]})
                print(name,seed,fold,flush=True)
                # Deterministic rotating order reduces fixed warm-up/order confounding.
                shift=(seed+fold)%len(METHODS);order=METHODS[shift:]+METHODS[:shift]
                for method in order:
                    t=time.perf_counter();prep=0.;guidance=None;injections=proposals=0;fits=evals=0;objective_seconds=0.;cheap=0
                    if method=='all_svm':mask=np.ones(d,dtype=bool);searchtime=0.
                    elif method=='anova':
                        ks=sorted(set(max(1,int(np.ceil(d*r))) for r in [.1,.2,.33,.5,.75,1]))
                        vals=[]
                        for k in ks:
                            estimator=make_pipeline(SelectKBest(f_classif,k=k),StandardScaler(),SVC(C=1,gamma='scale'))
                            score=cross_val_score(estimator,X[tr],y[tr],cv=inner,scoring='balanced_accuracy',error_score='raise').mean()
                            vals.append(cfg['alpha']*score+(1-cfg['alpha'])*(1-k/d))
                        chosen=ks[int(np.argmax(vals))];mask=SelectKBest(f_classif,k=chosen).fit(X[tr],y[tr]).get_support()
                        evals=len(ks);fits=evals*len(inner);searchtime=time.perf_counter()-t;objective_seconds=searchtime
                    else:
                        if d>4 and method in ['cgco_ga','cgmo_ga','cgga_adapted']:
                            gt=time.perf_counter();guidance=Guidance(X[tr],y[tr],inner);prep=time.perf_counter()-gt
                        fitness=TimedFitness(X[tr],y[tr],inner,cfg['alpha'])
                        nc=cfg['guidance_checks'] if method in ['cgco_ga','cgga_adapted'] else 1
                        nm=cfg['guidance_checks'] if method in ['cgmo_ga','cgga_adapted'] else 1
                        mask,h,injections,proposals=budget_search(fitness,seed+1000*fold,cfg['population'],cfg['budget'],guidance,nc,nm,method=='random')
                        searchtime=time.perf_counter()-t;evals=len(fitness.cache);fits=evals*len(inner);objective_seconds=fitness.seconds;cheap=guidance.calls if guidance else 0
                        for item in h:convergence.append({'dataset':name,'method':method,'seed':seed,'fold':fold,**item})
                    tfit=time.perf_counter();clf=model().fit(X[tr][:,mask],y[tr]);fittime=time.perf_counter()-tfit
                    tp=time.perf_counter();yp=clf.predict(X[te][:,mask]);predtime=time.perf_counter()-tp
                    rows.append({'dataset':name,'method':method,'seed':seed,'fold':fold,'accuracy':accuracy_score(y[te],yp),'balanced_accuracy':balanced_accuracy_score(y[te],yp),'macro_f1':f1_score(y[te],yp,average='macro'),'feature_count':int(mask.sum()),'feature_reduction_pct':100*(1-mask.mean()),'guidance_preprocess_seconds':prep,'objective_seconds':objective_seconds,'proposal_overhead_seconds':max(0.,searchtime-prep-objective_seconds),'search_seconds':searchtime,'fit_seconds':fittime,'predict_seconds':predtime,'pipeline_seconds':searchtime+fittime+predtime,'unique_evaluations':evals,'inner_classifier_fits':fits,'cheap_guidance_calls':cheap,'diversity_injections':injections,'proposals':proposals})
                    masks.append({'dataset':name,'method':method,'seed':seed,'fold':fold,'mask':mask.astype(int).tolist()})
                    for i,truth,prediction in zip(te,y[te],yp):pred.append({'dataset':name,'method':method,'seed':seed,'fold':fold,'index':int(i),'truth':int(truth),'prediction':int(prediction)})
                    pd.DataFrame(rows).to_csv(out/'raw_metrics.csv',index=False)
                    print(method,round(rows[-1]['balanced_accuracy'],4),int(mask.sum()),round(searchtime,3),flush=True)
    pd.DataFrame(pred).to_csv(out/'predictions.csv',index=False);pd.DataFrame(convergence).to_csv(out/'convergence.csv',index=False)
    (out/'masks.json').write_text(json.dumps(masks));(out/'splits.json').write_text(json.dumps(splitlog));(out/'datasets.json').write_text(json.dumps(datasets,indent=2))
    pd.DataFrame(rows).groupby(['dataset','method']).agg({c:['mean','std','count'] for c in ['accuracy','balanced_accuracy','macro_f1','feature_count','feature_reduction_pct','pipeline_seconds','guidance_preprocess_seconds','search_seconds','unique_evaluations']}).to_csv(out/'summary.csv')
    manifest={'status':'COMPLETE','config':cfg,'start_epoch':start,'end_epoch':time.time(),'elapsed_seconds':time.time()-start,'rows':len(rows),'versions':{x:importlib.metadata.version(x) for x in ['numpy','pandas','scikit-learn','scipy','matplotlib','pytest']},'platform':platform.platform(),'execution':'Serial,rotating method order;timing observational','code_sha256':{f:hashlib.sha256(Path('src',f).read_bytes()).hexdigest() for f in ['major_ga.py','major_experiment.py','ga.py']}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('COMPLETE',len(rows),manifest['elapsed_seconds'],flush=True)

if __name__=='__main__':run(sys.argv[1])
