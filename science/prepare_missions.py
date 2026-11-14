import json,calendar
from pathlib import Path
import numpy as np
from scipy import stats
from analyze import analyze

missions=[]
for file in Path("data/raw").glob("*.json"):
    raw=json.loads(file.read_text())
    params=raw["properties"]["parameter"]
    for key in ["T2M","PRECTOTCORR"]:
        points=[(k,v) for k,v in sorted(params[key].items()) if int(k[-2:])<=12 and v!=-999]
        years=sorted(set(int(k[:4]) for k,v in points))
        annual=[]
        valid_years=[]
        for year in years:
            months=[(int(k[-2:]),v) for k,v in points if int(k[:4])==year]
            if len(months)!=12: continue
            days=[calendar.monthrange(year,m)[1] for m,v in months]
            values=[v for m,v in months]
            annual.append(float(np.dot(values,days) if key=="PRECTOTCORR" else np.average(values,weights=days)))
            valid_years.append(year)
        result=analyze(valid_years,annual)
        x=np.array(valid_years,dtype=float)
        y=np.array(annual)
        robust=stats.theilslopes(y,x)
        result["theil_sen"]=float(robust.slope)
        residual=np.array(result["residuals"])
        result["lag1"]=float(np.corrcoef(residual[:-1],residual[1:])[0,1])
        # HAC sandwich covariance with Bartlett weights and finite sample correction.
        design=np.column_stack([np.ones(len(x)),x-x.mean()])
        bread=np.linalg.inv(design.T@design)
        scores=design*residual[:,None]
        meat=scores.T@scores
        lag=min(3,len(x)-2)
        for offset in range(1,lag+1):
            cross=scores[offset:].T@scores[:-offset]
            meat+=(1-offset/(lag+1))*(cross+cross.T)
        covariance=bread@meat@bread*len(x)/(len(x)-2)
        se=float(np.sqrt(covariance[1,1]))
        critical=stats.t.ppf(.975,len(x)-2)
        result["hac_interval"]=[result["slope"]-critical*se,result["slope"]+critical*se]
        result["hac_p"]=float(2*stats.t.sf(abs(result["slope"]/se),len(x)-2))
        result["hac_lags"]=lag
        climatology={m:float(np.mean([v for k,v in points if int(k[-2:])==m])) for m in range(1,13)}
        result.update(id=file.stem+"-"+key,location=file.stem,variable=key,
            unit="mm/year" if key=="PRECTOTCORR" else "°C",
            label="Annual precipitation" if key=="PRECTOTCORR" else "Annual mean temperature",
            coordinates=raw["geometry"]["coordinates"][:2],
            monthly_dates=[k for k,v in points],monthly=[v for k,v in points],
            anomalies=[v-climatology[int(k[-2:])] for k,v in points],
            monthly_unit=raw["parameters"][key]["units"],climatology=list(climatology.values()),
            source="NASA POWER / MERRA-2",header=raw["header"],
            source_url="https://power.larc.nasa.gov/docs/services/api/temporal/monthly/",
            caveat="Gridded meteorological estimates at the requested point. Spatial context imagery is a separate product. HAC inference is approximate with 25 annual observations.")
        missions.append(result)
Path("apps/web/public/missions.json").write_text(json.dumps(missions,indent=2))
print("Generated",len(missions),"NASA missions")
