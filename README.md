# PharmaShield AI

PharmaShield AI is a memory-aware multi-agent RAG platform for pharmacy operations. It helps pharmacy teams handle drug shortages, prior authorization, and GLP-1 authenticity/compliance risk.

This MVP supports pharmacist-reviewable workflows only. It does not make final medical, dispensing, substitution, or legal determinations.

## Features
- Multi-agent orchestration
- Shortage and substitution agent
- Prior authorization and coverage agent
- GLP-1 authenticity and compliance agent
- RAG retrieval
- Citation-backed outputs
- Pharmacist feedback memory
- Demo data
- FastAPI backend
- Next.js frontend

## Quickstart
```bash
cp .env.example .env
make up
```

In a second terminal:

```bash
make seed
```

Then open:

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

## Demo case

Use the built-in analyzer defaults or submit this payload to `POST /api/cases/analyze`:

```json
{
  "query": "Ozempic is out of stock, Wegovy was denied by insurance, and patient found a cheaper semaglutide supplier online claiming generic Ozempic with no prescription needed. What should pharmacy staff do?",
  "drug_name": "Ozempic",
  "payer_name": "Demo Health Plan",
  "patient_context": {
    "age": 52,
    "diagnoses": ["type 2 diabetes"],
    "labs": {"a1c": "8.7"},
    "previous_therapies": ["metformin"],
    "allergies": []
  },
  "inventory_context": {
    "location_id": "PHARMACY_001",
    "quantity_on_hand": 0,
    "reorder_threshold": 2
  },
  "product_context": {
    "supplier_name": "Online Semaglutide Discount Pharmacy",
    "claim_text": "Generic Ozempic, same active ingredient, no prescription needed",
    "ndc": null,
    "lot_number": null,
    "manufacturer": null
  }
}
```

## API examples

- `GET /health`
- `POST /api/cases/analyze`
- `GET /api/cases/{case_id}`
- `POST /api/ingest/demo`
- `POST /api/ingest/public`
- `POST /api/documents/upload`
- `POST /api/feedback`

## Make targets

- `make up` starts the stack
- `make down` stops the stack
- `make seed` loads demo data
- `make public-ingest` attempts live public source ingest
- `make test` runs backend tests in Docker

## Screenshots

- `docs/screenshots/home.png` placeholder
- `docs/screenshots/case-detail.png` placeholder
- `docs/screenshots/dashboard.png` placeholder

## Safety note

Every final answer must be treated as pharmacist-reviewable support content:

`Pharmacist review required before clinical, dispensing, substitution, or patient-specific action.`
