export type PairedRow = {date:string;ndvi:number;sif:number;count:number;quality_pass:boolean};
export type PairedInput = {
  kind:"observations"|"synthetic";
  region:string;
  ndvi_source:string;
  sif_source:string;
  sif_independent:boolean;
  sif_units:string;
  matching_method:string;
  quality_method:string;
  rows:PairedRow[];
};

function slope(values:number[]):number {
  const center=(values.length-1)/2;
  return values.reduce((sum,value,index)=>sum+(index-center)*value,0)/
    values.reduce((sum,_,index)=>sum+(index-center)**2,0)*12;
}
function quantile(values:number[],p:number):number {
  const ordered=[...values].sort((a,b)=>a-b);
  const index=(ordered.length-1)*p;
  return ordered[Math.floor(index)]+(ordered[Math.ceil(index)]-ordered[Math.floor(index)])*(index%1);
}

export function greenMirage(input:PairedInput) {
  if(!input||!["synthetic","observations"].includes(input.kind)||!Array.isArray(input.rows))throw new Error("Provide an observations or synthetic record with rows.");
  for(const key of ["region","ndvi_source","sif_source","sif_units","matching_method","quality_method"] as const)
    if(typeof input[key]!=="string"||!input[key].trim())throw new Error("Missing metadata: "+key);
  if(input.sif_independent!==true)throw new Error("Independent SIF observations are required for this analysis. Reflectance-derived SIF risks circular comparison.");
  if(input.rows.length>1200)throw new Error("Maximum 1,200 monthly pairs.");
  const rows=[...input.rows].sort((a,b)=>a.date.localeCompare(b.date));
  if(rows.length<72)throw new Error("At least 72 consecutive monthly pairs are required, including 36 baseline months.");
  let previous=-1;
  for(const row of rows){
    if(!/^\d{4}-(0[1-9]|1[0-2])$/.test(row.date))throw new Error("Dates must use YYYY-MM.");
    const month=Number(row.date.slice(0,4))*12+Number(row.date.slice(5))-1;
    if(previous>=0&&month!==previous+1)throw new Error("Monthly pairs must be consecutive and unique. Resolve gaps upstream without fabricating observations.");
    previous=month;
    if(!Number.isFinite(row.ndvi)||row.ndvi< -1||row.ndvi>1||!Number.isFinite(row.sif))throw new Error("Invalid NDVI or SIF observation.");
    if(row.quality_pass!==true||!Number.isInteger(row.count)||row.count<3)throw new Error("Every month must pass upstream quality checks and contain at least three matched observations.");
  }
  const baseline=rows.slice(0,36);
  function standardize(field:"ndvi"|"sif"){
    const climatology=Array.from({length:12},(_,month)=>{
      const values=baseline.filter(r=>Number(r.date.slice(5))===month+1).map(r=>r[field]);
      return values.reduce((a,b)=>a+b,0)/values.length;
    });
    const baselineResiduals=baseline.map(row=>row[field]-climatology[Number(row.date.slice(5))-1]);
    const sd=Math.sqrt(baselineResiduals.reduce((sum,v)=>sum+v*v,0)/(baseline.length-12));
    if(sd<1e-9)throw new Error("Baseline residual variance is too small for standardization.");
    return rows.slice(36).map(row=>(row[field]-climatology[Number(row.date.slice(5))-1])/sd);
  }
  const ndvi=standardize("ndvi"),sif=standardize("sif");
  const divergence=sif.map((v,i)=>v-ndvi[i]);
  const estimate=slope(divergence),mean=divergence.reduce((a,b)=>a+b,0)/divergence.length;
  const residual=divergence.map((v,i)=>v-mean-estimate*(i-(divergence.length-1)/2)/12);
  let seed=7319;
  function random(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296}
  const nullSlopes:number[]=[];
  for(let replicate=0;replicate<1000;replicate++){
    const resampled:number[]=[];
    while(resampled.length<residual.length){
      const start=Math.floor(random()*residual.length);
      for(let offset=0;offset<6&&resampled.length<residual.length;offset++)resampled.push(residual[(start+offset)%residual.length]);
    }
    nullSlopes.push(slope(resampled));
  }
  const interval=[estimate-quantile(nullSlopes,.975),estimate-quantile(nullSlopes,.025)];
  const p=(1+nullSlopes.filter(v=>Math.abs(v)>=Math.abs(estimate)).length)/1001;
  return {dates:rows.slice(36).map(r=>r.date),ndvi,sif,divergence,slope:estimate,interval,p,
    ndvi_slope:slope(ndvi),sif_slope:slope(sif),
    candidate:estimate<0&&interval[1]<0&&slope(ndvi)>=0&&slope(sif)<0,
    baseline:[rows[0].date,rows[35].date],
    method:"Calendar-month baseline means over first 36 months; residual baseline SD; subsequent paired standardized anomalies. Circular residual block bootstrap, six-month blocks, 1,000 replicates, fixed seed 7319. Approximate inference conditional on baseline and upstream matching; baseline and measurement uncertainty are omitted."};
}

export function teachingExample():PairedInput {
  let seed=419;
  const noise=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296-.5};
  return {kind:"synthetic",region:"Illustrative ecosystem",ndvi_source:"Synthetic educational generator",sif_source:"Synthetic educational generator",sif_independent:true,sif_units:"illustrative SIF units",matching_method:"Synthetic co-located monthly pairs",quality_method:"Synthetic values; no satellite quality flags",rows:Array.from({length:120},(_,i)=>({date:String(2015+Math.floor(i/12))+"-"+String(i%12+1).padStart(2,"0"),ndvi:.5+.06*Math.sin(i*Math.PI/6)+.0003*i+.025*noise(),sif:1.5+.2*Math.sin(i*Math.PI/6)-.002*i+.15*noise(),count:20,quality_pass:true}))};
}
