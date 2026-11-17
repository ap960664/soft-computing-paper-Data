"""Prospective crossover-policy diagnostic, not integrated into saved runs.

Source: Zhou/Hua2022,Algorithm2,Eq7,physicalp4: choose the cut by
max(J(child1),J(child2)),then return BOTH chromosomes. This module
isolates that step;it is not a reproduction of the complete CGGA.
Caller must separately declare mutation,budget and empty-mask policies.
"""
import numpy as np

def guided_crossover(a,b,points,guidance,policy='both',rng=None):
    a=np.asarray(a);b=np.asarray(b)
    if a.ndim!=1 or a.shape!=b.shape or not len(a) or not np.isin(a,[0,1]).all() or not np.isin(b,[0,1]).all():
        raise ValueError('Parents must be equally sized,nonempty binary vectors')
    a=a.astype(bool);b=b.astype(bool);points=list(points)
    if not points or any(not isinstance(p,(int,np.integer)) or not 1<=p<=len(a) for p in points):
        raise ValueError('Cut points are1..d,inclusive,as specified by the source')
    if policy not in ['both','best_one','random_one']:raise ValueError('Unknown retention policy')
    pairs=[(np.r_[a[:p],b[p:]],np.r_[b[:p],a[p:]]) for p in points]
    scores=[(float(guidance(x)),float(guidance(y))) for x,y in pairs]
    # Stable first-cut tie handling is declared here;source argmax does not
    # specify a tie policy. End-point crossover may return unchanged parents.
    index=max(range(len(pairs)),key=lambda i:max(scores[i]))
    pair=pairs[index];vals=scores[index]
    if policy=='both':children=pair
    elif policy=='best_one':children=(pair[int(vals[1]>vals[0])],)
    else:
        if rng is None:raise ValueError('Explicit RNG required for random retention')
        children=(pair[int(rng.integers(2))],)
    return children,{'cut':int(points[index]),'guidance_scores':vals,'policy':policy}
