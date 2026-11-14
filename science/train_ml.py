"""Train and export ridge regression models with chronological validation."""
import json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["Previous month temperature (C)", "Previous month rainfall (mm/day)", "Same month last year temperature (C)", "Same month last year rainfall (mm/day)", "Target month sine", "Target month cosine"]

def fit(x, y, alpha):
    mean, scale = x.mean(axis=0), x.std(axis=0)
    scale = np.where(scale > 1e-10, scale, 1)
    z = (x-mean)/scale
    center = float(y.mean())
    weights = np.linalg.solve(z.T@z+alpha*np.eye(x.shape[1]), z.T@(y-center))
    return {"mean":mean.tolist(),"scale":scale.tolist(),"weights":weights.tolist(),"intercept":center,"alpha":alpha}

def predict(model, x):
    return ((x-np.array(model["mean"]))/np.array(model["scale"]))@np.array(model["weights"])+model["intercept"]

def train(temperature, rainfall, location, dates):
    raw = np.column_stack([temperature, rainfall])
    if raw.shape != (300,2) or not np.isfinite(raw).all():
        raise ValueError("Expected 300 finite matched monthly observations")
    x, indices = [], np.arange(12,300)
    for t in indices:
        month = int(dates[t][-2:])
        x.append([*raw[t-1], *raw[t-12], np.sin(2*np.pi*month/12), np.cos(2*np.pi*month/12)])
    x = np.array(x)
    initial, validation, development, test = indices<192, (indices>=192)&(indices<240), indices<240, indices>=240
    models=[]
    for dimension, name, unit in [(0,"Temperature","C"),(1,"Rainfall","mm/day")]:
        y=raw[indices,dimension]
        candidates=[]
        for alpha in [.01,.1,1.,10.,100.]:
            m=fit(x[initial],y[initial],alpha)
            candidates.append({"alpha":alpha,"rmse":float(np.sqrt(np.mean((predict(m,x[validation])-y[validation])**2)))})
        best=min(candidates,key=lambda row:row["rmse"])["alpha"]
        m=fit(x[development],y[development],best)
        predictions=predict(m,x[test])
        truth=y[test]
        seasonal=raw[indices[test]-12,dimension]
        persistence=raw[indices[test]-1,dimension]
        def metrics(p):
            return {"rmse":float(np.sqrt(np.mean((p-truth)**2))),"mae":float(np.mean(abs(p-truth)))}
        models.append({**m,"id":location+"-"+name,"location":location,"target":name,"unit":unit,
            "features":FEATURES,"training_period":"2002-2020","selection_training":"2002-2016","validation_period":"2017-2020","test_period":"2021-2025",
            "training_count":int(development.sum()),"test_count":int(test.sum()),
            "candidates":candidates,"metrics":metrics(predictions),"seasonal":metrics(seasonal),"persistence":metrics(persistence),
            "minimum":x[development].min(axis=0).tolist(),"maximum":x[development].max(axis=0).tolist(),
            "test":[{"date":dates[t],"inputs":row.tolist(),"actual":float(actual),"predicted":float(pred),"seasonal":float(base)} for t,row,actual,pred,base in zip(indices[test],x[test],truth,predictions,seasonal)]})
    return models

def main():
    missions=json.loads((ROOT/"apps/web/public/missions.json").read_text())
    models=[]
    for location in sorted({m["location"] for m in missions}):
        temp=next(m for m in missions if m["location"]==location and m["variable"]=="T2M")
        rain=next(m for m in missions if m["location"]==location and m["variable"]=="PRECTOTCORR")
        if temp["monthly_dates"]!=rain["monthly_dates"]: raise ValueError("Unmatched dates")
        models.extend(train(temp["monthly"],rain["monthly"],location,temp["monthly_dates"]))
    (ROOT/"apps/web/public/ml-models.json").write_text(json.dumps(models,indent=2,allow_nan=False))
    for m in models: print(m["id"],"test RMSE",round(m["metrics"]["rmse"],3),"seasonal",round(m["seasonal"]["rmse"],3))
if __name__=="__main__": main()
