import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score

def repair(mask):
    mask=np.asarray(mask)
    if mask.ndim!=1 or not np.isin(mask,[0,1]).all() or len(mask)==0:
        raise ValueError('Mask must be a nonempty binary vector')
    mask=mask.astype(bool).copy()
    if not mask.any():mask[0]=True
    return mask

def model():return make_pipeline(StandardScaler(),SVC(C=1,kernel='rbf',gamma='scale'))

class Fitness:
    def __init__(self,X,y,splits,alpha):
        self.X,self.y,self.splits,self.alpha=X,y,splits,alpha
        self.cache={}
    def __call__(self,mask):
        mask=repair(mask)
        if len(mask)!=self.X.shape[1]:raise ValueError('Wrong mask length')
        key=mask.tobytes()
        if key not in self.cache:
            b=float(cross_val_score(model(),self.X[:,mask],self.y,cv=self.splits,scoring='balanced_accuracy',n_jobs=1,error_score='raise').mean())
            self.cache[key]=(self.alpha*b+(1-self.alpha)*(1-mask.mean()),b)
        return self.cache[key][0]

def offspring(a,b,rng,crossover_probability):
    child=a.copy()
    if rng.random()<crossover_probability:
        swaps=rng.random(len(a))<.5;child[swaps]=b[swaps]
    child^=rng.random(len(a))<1/len(a)
    return repair(child)

def search(fitness,seed,population,generations,crossover_probability):
    rng=np.random.default_rng(seed);d=fitness.X.shape[1]
    pop=[repair(rng.random(d)<rng.uniform(.1,.8)) for _ in range(population)]
    history=[]
    for generation in range(generations+1):
        scores=np.array([fitness(m) for m in pop]);best=int(scores.argmax())
        history.append(dict(generation=generation,best_fitness=float(scores[best]),mean_fitness=float(scores.mean()),unique_evaluations=len(fitness.cache)))
        if generation==generations:return pop[best],history
        def parent():
            ids=rng.integers(population,size=3);return pop[ids[np.argmax(scores[ids])]]
        new=[pop[best].copy()]
        while len(new)<population:new.append(offspring(parent(),parent(),rng,crossover_probability))
        pop=new

def random_search(fitness,seed,budget):
    rng=np.random.default_rng(seed);d=fitness.X.shape[1];best=None;score=-np.inf
    while len(fitness.cache)<budget:
        # Uniform subset cardinality avoids favouring dense masks.
        k=int(rng.integers(1,d+1));m=np.zeros(d,dtype=bool);m[rng.choice(d,k,replace=False)]=True
        s=fitness(m)
        if s>score:best,score=m,s
    return best
