# Advanced scientific features

## Climate Contradiction Atlas
Three locations, six variable-region slopes and six pairwise contrasts. Baseline temperature and rainfall from 2001–2005 define standardized Euclidean similarity. Trends use 2006–2025. Paired differences receive their own HAC fit. BH adjustment uses separate families for regional slopes and contrasts. No pair passes all opposing-trend criteria in the current prepared data.

The discovery score is a heuristic combining standardized slope separation, the largest adjusted q-value, and baseline similarity. Its exact formula is included in atlas.json. Spatial dependence, only three analogues, short records and data-driven selection limit interpretation.

## Digital Twin Lite
A two-state standardized temperature/precipitation model uses a ridge VAR(1) transition and Kalman filtering with H=I. The transition, scaling and monthly climatology use 2001–2020. Stability is capped at spectral radius 0.98. Q is empirical transition residual covariance. R=0.1 I is an assumed noise setting. This calibration is approximate and may double-count measurement variability.

2021–2025 validation compares sequential one-step predictions with persistence and seasonal climatology, using observed updates only after each prediction. Parameter uncertainty is omitted. This validation differs from the 24-month open-loop scenarios. Controls inject a temperature anomaly and a fraction of climatological monthly rain into state updates. These are assumed inputs rather than identified causal sensitivities. Negative precipitation exposes Gaussian model limitations.

## Green Mirage
The browser accepts matched monthly NDVI and independent SIF in JSON. No real paired fluorescence/vegetation record is bundled. Users must document upstream geographic/temporal matching, source versions, SIF units, and quality screening. Flags and sources are user declarations and are not independently validated.

First 36 months establish monthly climatology and residual SD. At least 36 subsequent months are analyzed. D = Z(SIF) - Z(NDVI). Fixed-seed circular residual block bootstrap uses six-month blocks and 1,000 samples. The basic bootstrap interval and null test are approximate and condition on the selected baseline. Retrieval uncertainty and baseline uncertainty require further propagation. Three matched observations per month is an application threshold requiring study-specific review.

The bundled generator is explicitly synthetic. Candidate criteria require a nonnegative NDVI slope, negative SIF slope and negative divergence with interval entirely below zero. The criterion does not establish ecosystem decline.

## 3D Earth
Three.js renders a NASA GIBS Blue Marble Next Generation texture. Geographic research markers link to prepared observations and reports. Sun position is illustrative. This is an interactive geographic globe, not a physical Earth-system simulator.

## Reproduction
Run python science/advanced.py to regenerate atlas.json and twins.json from missions.json.
Run python -m unittest discover -s tests and node --experimental-strip-types tests/mirage.mjs.
Build with npm run build in apps/web.

## Sources
- NASA POWER monthly service: https://power.larc.nasa.gov/docs/services/api/temporal/monthly/
- NASA GIBS access: https://nasa-gibs.github.io/gibs-api-docs/access-basics/
- OCO data: https://oco.caltech.edu/science/data-access
- SIF product paper: https://essd.copernicus.org/articles/14/1513/2022/
- Reflectance-derived SIF caveat: https://daac.ornl.gov/VEGETATION/guides/Global_High_Res_SIF_OCO2.html
