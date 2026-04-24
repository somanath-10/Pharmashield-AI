# Data Sources

Supported connectors and seeded sources:

- openFDA shortages: `https://api.fda.gov/drug/shortages.json`
- openFDA enforcement recalls: `https://api.fda.gov/drug/enforcement.json`
- DailyMed services v2: `https://dailymed.nlm.nih.gov/dailymed/services/v2/`
- Synthetic payer policies for `Demo Health Plan`
- Synthetic compliance notes and suspicious supplier examples
- Uploaded pharmacy SOPs, denial letters, CSVs, and text files

The MVP seeds GLP-1 examples for:

- semaglutide
- tirzepatide
- Ozempic
- Wegovy
- Rybelsus
- Mounjaro
- Zepbound

All live public ingest steps are best-effort. If external APIs are unavailable, the seeded synthetic dataset still supports the end-to-end demo workflow.
