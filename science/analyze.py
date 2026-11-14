import json
from pathlib import Path
import numpy as np
from scipy import stats
def analyze(years, values):
    if len(years)!=len(values): raise ValueError("Lengths differ")
    pairs=[(float(x),float(y)) for x,y in zip(years,values) if y is not None and np.isfinite(y) and np.isfinite(x)]
    if len(pairs)<4: raise ValueError("Four observations required")
    x,y=np.array(sorted(pairs)).T
    if len(set(x))!=len(x): raise ValueError("Duplicate years")
    if np.ptp(y)==0:
        slope,intercept,p,se,r2=0.,float(y[0]),1.,0.,0.
    else:
        f=stats.linregress(x,y)
        slope,intercept,p,se,r2=f.slope,f.intercept,f.pvalue,f.stderr,f.rvalue**2
    fitted=intercept+slope*x
    residual=y-fitted
    t=stats.t.ppf(.975,len(x)-2)
    error=np.sqrt(np.sum(residual**2)/(len(x)-2))
    band=t*error*np.sqrt(1/len(x)+(x-x.mean())**2/np.sum((x-x.mean())**2))
    return dict(years=x.tolist(),values=y.tolist(),fitted=fitted.tolist(),lower=(fitted-band).tolist(),upper=(fitted+band).tolist(),slope=float(slope),p=float(p),r2=float(r2),interval=[float(slope-t*se),float(slope+t*se)],n=len(x),missing=len(values)-len(x),residuals=residual.tolist(),method="Ordinary least squares, Student t inference")
if __name__=="__main__":
    r=analyze(list(range(2017,2026)),[.462,.493,.471,.518,.500,.553,.524,.576,.557])
    r.update(origin="Synthetic educational fixture",unit="NDVI units per year",season="Annual illustrative values; no seasonal adjustment applied.",region="Illustrative region; no geographic coordinates",imagery=[])
    Path("apps/web/public/evidence.json").write_text(json.dumps(r,indent=2))
