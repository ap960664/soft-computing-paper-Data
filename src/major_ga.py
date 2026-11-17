"""Controlled CGGA-operator adaptations; source and deviations in protocol."""
import time
import numpy as np
from sklearn.metrics import mutual_info_score
from ga import Fitness, repair

def entropy(x):
    _,n=np.unique(x,return_counts=True);p=n/n.sum()
    return float(-(p*np.log(p)).sum())

def symmetric_uncertainty(a,b):
    den=entropy(a)+entropy(b)
    return 0.0 if den==0 else float(np.clip(2*mutual_info_score(a,b)/den,0,1))

class Guidance:
    def __init__(self,X,y,splits,bins=5):
        self.calls=0;self.matrices=[];d=X.shape[1]
        for tr,_ in splits:
            Xt=X[tr];codes=np.zeros_like(Xt,dtype=int)
            for j in range(d):
                cuts=np.unique(np.quantile(Xt[:,j],np.arange(1,bins)/bins))
                codes[:,j]=np.searchsorted(cuts,Xt[:,j],side='right')
            fc=np.array([symmetric_uncertainty(codes[:,j],y[tr]) for j in range(d)])
            ff=np.zeros((d,d))
            for j in range(d):
                for k in range(j):ff[j,k]=ff[k,j]=symmetric_uncertainty(codes[:,j],codes[:,k])
            self.matrices.append((fc,ff))
    def __call__(self,mask):
        self.calls+=1;ids=np.flatnonzero(mask);k=len(ids)
        if k==0:return 0.0
        return float(np.mean([fc[ids].sum()/np.sqrt(k+ff[np.ix_(ids,ids)].sum()) for fc,ff in self.matrices]))

class TimedFitness(Fitness):
    def __init__(self,*args):super().__init__(*args);self.seconds=0.0
    def __call__(self,mask):
        fresh=repair(mask).tobytes() not in self.cache
        t=time.perf_counter();v=super().__call__(mask)
        if fresh:self.seconds+=time.perf_counter()-t
        return v

def mutation(a,rng):
    d=len(a);k=1 if d==1 or rng.random()<.9 else int(rng.integers(2,d+1))
    m=a.copy();m[rng.choice(d,k,replace=False)]^=True
    return repair(m)

def propose(a,b,rng,guidance,cross_checks,mutation_checks):
    d=len(a)
    points=rng.choice(np.arange(1,d),size=min(cross_checks,d-1),replace=False) if d>1 else [0]
    pairs=[]
    for p in points:pairs.append((repair(np.r_[a[:p],b[p:]]),repair(np.r_[b[:p],a[p:]])))
    if cross_checks>1:
        pair=max(pairs,key=lambda pair:max(guidance(pair[0]),guidance(pair[1])))
    else:pair=pairs[0]
    child=pair[int(rng.integers(2))]
    variants=[mutation(child,rng) for _ in range(mutation_checks)]
    return max(variants,key=guidance) if mutation_checks>1 else variants[0]

def budget_search(fitness,seed,population,budget,guidance=None,cross_checks=1,mutation_checks=1,random_only=False):
    rng=np.random.default_rng(seed);d=fitness.X.shape[1];budget=min(budget,2**d-1)
    pop=[];history=[];duplicates=0;injections=0;proposals=0;start=time.perf_counter()
    def random_mask():
        k=int(rng.integers(1,d+1));m=np.zeros(d,dtype=bool);m[rng.choice(d,k,replace=False)]=True;return m
    def best():
        key=max(fitness.cache,key=lambda b:(fitness.cache[b][0],tuple(np.frombuffer(b,dtype=bool))))
        return np.frombuffer(key,dtype=bool).copy()
    if d<=4:
        # Declared exhaustive sanity case; identical objective coverage for searches.
        for n in range(1,budget+1):fitness(np.array([(n>>j)&1 for j in range(d)],dtype=bool))
        return best(),[{'proposal':0,'unique_evaluations':len(fitness.cache),'best_fitness':fitness(best())}],0,0
    while len(fitness.cache)<budget:
        proposals+=1
        if random_only or len(pop)<population or duplicates>=20:
            mask=random_mask()
            if duplicates>=20:injections+=1;duplicates=0
        else:
            def parent():
                ids=rng.integers(len(pop),size=3)
                return max((pop[i] for i in ids),key=fitness)
            mask=propose(parent(),parent(),rng,guidance,cross_checks,mutation_checks)
        n=len(fitness.cache);value=fitness(mask)
        if len(fitness.cache)==n:duplicates+=1
        else:
            duplicates=0;pop.append(mask)
            pop=sorted(pop,key=fitness,reverse=True)[:population]
            history.append({'proposal':proposals,'unique_evaluations':len(fitness.cache),'best_fitness':fitness(best())})
        if proposals>budget*10000:raise RuntimeError('Search stalled instead of inventing completed budget')
    return best(),history,injections,proposals
