from pathlib import Path
import sys,json,time,platform,hashlib,traceback,importlib.metadata
import numpy as np
import pandas as pd
import yaml
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import StratifiedKFold,cross_val_score
from sklearn.feature_selection import SelectKBest,f_classif
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score,balanced_accuracy_score,f1_score,precision_score,recall_score
from ga import Fitness,search,random_search,model

def run(config_path):
    cfg=yaml.safe_load(Path(config_path).read_text());out=Path(cfg['output']);out.mkdir(parents=True,exist_ok=True)
    start=time.time();data=load_breast_cancer();X=data.data;y=data.target
    (out/'dataset_description.txt').write_text(data.DESCR)
    versions={m:importlib.metadata.version(m) for m in ['numpy','pandas','scikit-learn','scipy','matplotlib','PyYAML','pytest']}
    manifest=dict(status='RUNNING',start_epoch=start,config=cfg,config_path=str(config_path),shape=list(X.shape),class_counts={str(k):int((y==k).sum()) for k in np.unique(y)},missing_values=int(np.isnan(X).sum()),target_names=list(data.target_names),positive_class='benign (1); F1/precision/recall refer to benign',versions=versions,platform=platform.platform(),processor=platform.processor(),data_hash=hashlib.sha256(X.tobytes()+y.tobytes()).hexdigest(),code_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('src').glob('*.py')})
    (out/'experiment_manifest.json').write_text(json.dumps(manifest,indent=2));(out/'environment.txt').write_text(json.dumps(versions,indent=2)+'\n'+platform.platform())
    rows=[];features=[];convergence=[];predictions=[];splits=[]
    for seed in cfg['seeds']:
        outer=StratifiedKFold(cfg['outer_folds'],shuffle=True,random_state=seed)
        for fold,(tr,te) in enumerate(outer.split(X,y),1):
            print(f'Seed {seed}, outer fold {fold}',flush=True)
            inner=list(StratifiedKFold(cfg['inner_folds'],shuffle=True,random_state=seed+fold).split(X[tr],y[tr]))
            splits.append(dict(seed=seed,fold=fold,train=tr.tolist(),test=te.tolist(),inner=[{'train_global':tr[a].tolist(),'valid_global':tr[b].tolist()} for a,b in inner]))
            fs=Fitness(X[tr],y[tr],inner,cfg['alpha']);t=time.perf_counter()
            ga,hist=search(fs,seed+1000*fold,cfg['population'],cfg['generations'],cfg['crossover_probability']);ga_time=time.perf_counter()-t
            for h in hist:convergence.append(dict(seed=seed,fold=fold,**h))
            for method in ['all_svm','filter_svm','ga_svm','random_svm']:
                t=time.perf_counter();evals=0
                try:
                    if method=='all_svm':mask=np.ones(X.shape[1],dtype=bool);search_time=0.;clf=model()
                    elif method=='ga_svm':mask=ga;search_time=ga_time;evals=len(fs.cache);clf=model()
                    elif method=='random_svm':
                        rf=Fitness(X[tr],y[tr],inner,cfg['alpha']);mask=random_search(rf,seed+2000*fold,len(fs.cache));search_time=time.perf_counter()-t;evals=len(rf.cache);clf=model()
                    else:
                        vals=[]
                        for k in cfg['filter_k']:
                            p=make_pipeline(SelectKBest(f_classif,k=k),StandardScaler(),SVC(C=1,kernel='rbf',gamma='scale'))
                            s=float(cross_val_score(p,X[tr],y[tr],cv=inner,scoring='balanced_accuracy',error_score='raise').mean())
                            vals.append(cfg['alpha']*s+(1-cfg['alpha'])*(1-k/X.shape[1]))
                        k=cfg['filter_k'][int(np.argmax(vals))]
                        selector=SelectKBest(f_classif,k=k).fit(X[tr],y[tr]);mask=selector.get_support();search_time=time.perf_counter()-t;evals=len(vals);clf=model()
                    fit_start=time.perf_counter();clf.fit(X[tr][:,mask],y[tr]);fit_time=time.perf_counter()-fit_start
                    predict_start=time.perf_counter();yp=clf.predict(X[te][:,mask]);predict_time=time.perf_counter()-predict_start
                    row=dict(method=method,seed=seed,fold=fold,accuracy=accuracy_score(y[te],yp),balanced_accuracy=balanced_accuracy_score(y[te],yp),f1=f1_score(y[te],yp),precision=precision_score(y[te],yp),recall=recall_score(y[te],yp),feature_count=int(mask.sum()),feature_reduction_pct=100*(1-mask.mean()),search_seconds=search_time,fit_seconds=fit_time,predict_seconds=predict_time,total_train_seconds=search_time+fit_time,unique_objective_evaluations=evals,inner_classifier_fits=evals*cfg['inner_folds'],error='')
                    for j in np.flatnonzero(mask):features.append(dict(method=method,seed=seed,fold=fold,feature_index=int(j),feature_name=data.feature_names[j]))
                    for index,truth,pred in zip(te,y[te],yp):predictions.append(dict(method=method,seed=seed,fold=fold,index=int(index),truth=int(truth),prediction=int(pred)))
                except Exception as exc:
                    traceback.print_exc();row=dict(method=method,seed=seed,fold=fold,error=str(exc))
                rows.append(row);pd.DataFrame(rows).to_csv(out/'raw_metrics.csv',index=False)
                print(method,{k:round(row[k],4) for k in ['balanced_accuracy','feature_count','total_train_seconds'] if k in row},flush=True)
    pd.DataFrame(features).to_csv(out/'selected_features.csv',index=False);pd.DataFrame(convergence).to_csv(out/'ga_convergence.csv',index=False);pd.DataFrame(predictions).to_csv(out/'test_predictions.csv',index=False)
    (out/'split_indices.json').write_text(json.dumps(splits));frame=pd.DataFrame(rows)
    numeric=['accuracy','balanced_accuracy','f1','feature_count','feature_reduction_pct','search_seconds','fit_seconds','predict_seconds','total_train_seconds','unique_objective_evaluations']
    summary=[]
    for method,g in frame.groupby('method'):
        for metric in numeric:summary.append(dict(method=method,metric=metric,mean=g[metric].mean(),sd=g[metric].std(ddof=1),n=int(g[metric].count()),units=('seconds' if 'seconds' in metric else 'percent' if metric.endswith('pct') else 'count' if metric in ['feature_count','unique_objective_evaluations'] else 'proportion'),interpretation='descriptive SD across overlapping repeated CV folds; not independent trials'))
    pd.DataFrame(summary).to_csv(out/'summary_metrics.csv',index=False)
    manifest.update(status='COMPLETE' if frame.error.fillna('').eq('').all() else 'COMPLETE_WITH_FAILURES',end_epoch=time.time(),elapsed_seconds=time.time()-start,rows=len(frame));(out/'experiment_manifest.json').write_text(json.dumps(manifest,indent=2));print(manifest['status'],manifest['elapsed_seconds'],flush=True)

if __name__=='__main__':run(sys.argv[1])
