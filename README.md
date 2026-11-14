# Ferris Earth Intelligence

Ferris is an Astro scientific workspace for exploring NASA POWER climate records and NASA GIBS imagery.

## Run locally
Install Python dependencies with python -m pip install -r science/requirements.txt.
Inside apps/web, run npm ci and npm run dev.
Run npm run build for the production site.

## Scientific features
- Six NASA POWER temperature/rainfall investigations, 2001-2025.
- Trend estimates, HAC uncertainty, seasonal anomalies and evidence export.
- Interactive 3D Earth and dated satellite browse imagery.
- Guided discovery, browser-local notebooks and a rule-based evidence assistant.
- Regional Contradiction Atlas with adjusted significance tests.
- Green Mirage: paired vegetation/fluorescence import and an explicitly synthetic teaching example.
- Digital Twin Lite: conditional regional scenarios with validation baselines.
- Machine Learning Lab: six trained ridge models, held-out testing and custom-input predictions.
- Editable research drafts, methods, catalog, FAQ and educational examples.

## Reproduce
Original NASA responses are in data/raw.
Run python science/fetch_power.py to retrieve records, then python science/prepare_missions.py.
Run python science/advanced.py to regenerate Atlas and Twin artifacts.
Run python science/train_ml.py to regenerate ml-models.json.
Run python -m unittest discover -s tests and node tests/mirage.mjs for scientific checks.

ML hyperparameter selection uses 2002-2016 training and 2017-2020 validation.
The final model uses 228 monthly samples from 2002-2020 with training-only scaling.
Each model is evaluated on 60 held-out one-step predictions from 2021-2025.
The browser supports historical-month testing, editable inputs, extrapolation warnings and model export.
Training runs in Python; inference runs in the browser. Predictions are not causal forecasts.
Baseline comparisons and limitations remain visible even where the trained model performs worse.

## Hosting
wrangler deploy publishes the built apps/web/dist directory to the configured Cloudflare custom domain.
Build from the GitHub revision intended for release before deployment.
