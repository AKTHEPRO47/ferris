# Ferris evidence card
Run python -m pip install -r science/requirements.txt then python science/analyze.py from the root.
Run npm install and npm run dev inside apps/web. Run npm run build for a production build.
Run python -m unittest discover -s tests for scientific checks.

Implemented: Astro card, interactive chart, Python regression, pointwise confidence bounds for the mean fit, computed explanations, evidence export, missing imagery disclosure and rule-based suggestions.
The included mission is synthetic. NASA ingestion, real imagery, LLM agents, live API and deployment remain planned.
OLS inference assumes independent errors and constant variance. Real missions need quality controls, seasonal treatment and dependence-aware inference.

## NASA investigations
The primary workspace includes six NASA POWER investigations for Borneo, Sumatra and Singapore, 2001–2025. Original NASA responses are retained in data/raw. Run python science/fetch_power.py to retrieve data and python science/prepare_missions.py to regenerate missions.json. Network access is required for retrieval and GIBS imagery.

Added annual calendar-weighted aggregation, seasonal anomalies, residual inspection, Theil–Sen estimates, HAC intervals and approximate p-values. Live image panels request dated MODIS Terra true-color browse scenes. Imagery provides context and has no quantitative change-detection model. Advanced inference and image rendering require further validation. LLM agents and deployment remain pending.
