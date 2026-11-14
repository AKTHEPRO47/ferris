"""Reproducible regional contrasts and observation-driven scenario models."""
import json
import itertools
from pathlib import Path
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]

def hac_trend(years, values, lags=3):
    x = np.asarray(years, dtype=float)
    y = np.asarray(values, dtype=float)
    design = np.column_stack([np.ones(len(x)), x-x.mean()])
    coefficients = np.linalg.lstsq(design, y, rcond=None)[0]
    residual = y-design@coefficients
    bread = np.linalg.inv(design.T@design)
    scores = design*residual[:,None]
    meat = scores.T@scores
    for offset in range(1, min(lags,len(x)-2)+1):
        cross = scores[offset:].T@scores[:-offset]
        meat += (1-offset/(lags+1))*(cross+cross.T)
    covariance = bread@meat@bread*len(x)/(len(x)-2)
    se = np.sqrt(max(0, covariance[1,1]))
    slope = float(coefficients[1])
    p = float(2*stats.t.sf(abs(slope/se),len(x)-2)) if se>0 else float(slope==0)
    critical = stats.t.ppf(.975,len(x)-2)
    return {"slope":slope,"p":p,"interval":[float(slope-critical*se),float(slope+critical*se)]}

def bh_adjust(pvalues):
    p = np.asarray(pvalues)
    order = np.argsort(p)
    adjusted = np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1]
    result = np.empty(len(p))
    result[order] = np.minimum(1,adjusted)
    return result.tolist()

def kalman_step(state, covariance, observation, transition, process, noise):
    predicted = transition@state
    predicted_covariance = transition@covariance@transition.T+process
    gain = np.linalg.solve((predicted_covariance+noise).T,predicted_covariance.T).T
    updated = predicted+gain@(observation-predicted)
    identity = np.eye(len(state))
    updated_covariance = (identity-gain)@predicted_covariance@(identity-gain).T+gain@noise@gain.T
    return updated,updated_covariance,predicted,predicted_covariance+noise

def fit_twin(temperature, rain):
    raw = np.column_stack([temperature["monthly"],rain["monthly"]])
    dates = temperature["monthly_dates"]
    if dates!=rain["monthly_dates"] or len(raw)!=300:
        raise ValueError("Twin requires matched 300-month records")
    training_count = 240
    months = np.array([int(date[-2:])-1 for date in dates])
    climatology = np.array([raw[:training_count][months[:training_count]==month].mean(axis=0) for month in range(12)])
    anomalies = raw-climatology[months]
    scale = anomalies[:training_count].std(axis=0,ddof=1)
    standardized = anomalies/scale
    train = standardized[:training_count]
    transition = np.linalg.solve(train[:-1].T@train[:-1]+.1*np.eye(2),train[:-1].T@train[1:]).T
    radius = max(abs(np.linalg.eigvals(transition)))
    if radius>.98:
        transition *= .98/radius
    innovations = train[1:]-train[:-1]@transition.T
    process = np.cov(innovations.T)+1e-6*np.eye(2)
    noise = .1*np.eye(2)
    state = np.zeros(2)
    covariance = np.eye(2)
    predictions, actual, coverage, persistence = [],[],[],[]
    for index,observation in enumerate(standardized):
        state,covariance,predicted,predictive_covariance = kalman_step(state,covariance,observation,transition,process,noise)
        if index>=training_count:
            predictions.append(predicted)
            actual.append(observation)
            coverage.append(np.abs(observation-predicted)<=1.96*np.sqrt(np.diag(predictive_covariance)))
            persistence.append(standardized[index-1])
    actual = np.array(actual)
    prediction = np.array(predictions)
    def rmse(values):
        return (np.sqrt(np.mean((actual-np.array(values))**2,axis=0))*scale).tolist()
    return {
        "location":temperature["location"],"coordinates":temperature["coordinates"],
        "dates":dates,"observed":raw.tolist(),"transition":transition.tolist(),
        "process":process.tolist(),"noise":noise.tolist(),"state":state.tolist(),
        "covariance":covariance.tolist(),"scale":scale.tolist(),"climatology":climatology.tolist(),
        "training_min":train.min(axis=0).tolist(),"training_max":train.max(axis=0).tolist(),
        "validation":{"period":"2021–2025","rmse":rmse(prediction),"persistence_rmse":rmse(persistence),
                      "climatology_rmse":rmse(np.zeros_like(actual)),"coverage":np.mean(coverage,axis=0).tolist(),
                      "predicted":(prediction*scale+climatology[months[training_count:]]).tolist()},
        "training_period":"2001–2020","source":"NASA POWER / MERRA-2",
        "units":["°C","mm/day"],
        "assumptions":"Two standardized meteorological anomaly states, H=I. Ridge VAR(1) transition fitted before holdout, then used in a Kalman filter. R=0.1 I is an assumed observation-noise covariance. Q is empirical transition residual covariance. Scenario inputs directly shift standardized state each month. Intervals omit parameter uncertainty. Rainfall values are not clipped; negative values expose Gaussian model limitations."
    }

def main():
    missions = json.loads((ROOT/"apps/web/public/missions.json").read_text())
    # Reserve 2001–2005 for baseline similarity, analyze 2006–2025.
    locations = sorted({m["location"] for m in missions})
    features = []
    for location in locations:
        features.append([np.mean(next(m for m in missions if m["location"]==location and m["variable"]==v)["values"][:5]) for v in ["T2M","PRECTOTCORR"]])
    features = np.array(features)
    features = (features-features.mean(axis=0))/features.std(axis=0,ddof=1)
    trends = {}
    for m in missions:
        trends[m["id"]] = hac_trend(m["years"][5:],m["values"][5:])
    adjusted = bh_adjust([trends[m["id"]]["p"] for m in missions])
    for m,q in zip(missions,adjusted):
        trends[m["id"]]["q"] = q
    pairs = []
    for variable in ["T2M","PRECTOTCORR"]:
        records = [m for m in missions if m["variable"]==variable]
        for a,b in itertools.combinations(records,2):
            first,second = trends[a["id"]],trends[b["id"]]
            difference = np.array(a["values"][5:])-np.array(b["values"][5:])
            contrast = hac_trend(a["years"][5:],difference)
            distance = float(np.linalg.norm(features[locations.index(a["location"])]-features[locations.index(b["location"])]))
            pairs.append({"id":a["id"]+"--"+b["id"],"variable":variable,"unit":a["unit"],
                          "a":a["location"],"b":b["location"],"coordinates":[a["coordinates"],b["coordinates"]],
                          "years":a["years"][5:],"values":[a["values"][5:],b["values"][5:]],
                          "trends":[first,second],"contrast":contrast,"similarity":float(np.exp(-distance)),
                          "opposite":first["slope"]*second["slope"]<0})
    for pair,q in zip(pairs,bh_adjust([p["contrast"]["p"] for p in pairs])):
        pair["contrast"]["q"] = q
        pair["qualified"] = bool(pair["opposite"] and max(t["q"] for t in pair["trends"])<.05 and q<.05)
        combined_scale = float(np.std(np.concatenate(pair["values"]),ddof=1))
        separation = abs(pair["contrast"]["slope"])*20/combined_scale
        pair["score"] = float(100*(1-np.exp(-separation))*(1-max(q,*[t["q"] for t in pair["trends"]]))*pair["similarity"])
    atlas = {"baseline":"2001–2005","period":"2006–2025","pairs":pairs,
             "families":"BH correction across six regional-variable slopes and separately across six paired contrasts. Exploratory screening with approximate HAC p-values.",
             "score":"100 × (1 − exp(− |slope difference| × 20 / pooled SD)) × (1 − largest adjusted q) × exp(− baseline distance). Ranking heuristic; no inferential interpretation.",
             "matching":"Euclidean distance between standardized baseline temperature and rainfall features. Only three locations; similarity calibration is limited."}
    twins = [fit_twin(next(m for m in missions if m["location"]==location and m["variable"]=="T2M"),next(m for m in missions if m["location"]==location and m["variable"]=="PRECTOTCORR")) for location in locations]
    (ROOT/"apps/web/public/atlas.json").write_text(json.dumps(atlas,indent=2))
    (ROOT/"apps/web/public/twins.json").write_text(json.dumps(twins,indent=2))
    print("Prepared",len(pairs),"paired contrasts and",len(twins),"validated scenario models")
    print("Qualified opposite pairs:",sum(p["qualified"] for p in pairs))

if __name__=="__main__":
    main()
