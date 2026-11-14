import requests,json
from pathlib import Path
for name,lat,lon in [("Borneo",-2.2,113.9),("Sumatra",-2.9,104.7),("Singapore",1.35,103.82)]:
    response=requests.get("https://power.larc.nasa.gov/api/temporal/monthly/point",params=dict(parameters="T2M,PRECTOTCORR",community="AG",latitude=lat,longitude=lon,start=2001,end=2025,format="JSON"),timeout=90)
    response.raise_for_status()
    payload=response.json()
    Path("data/raw/"+name+".json").write_text(json.dumps(payload,indent=2))
    print(name, response.status_code,flush=True)
