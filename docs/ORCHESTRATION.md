# Orchestration

The coordinator is intentionally inspectable and deterministic.

## Flow

1. Create a `PharmacyCase` record and hash patient context.
2. Classify the request with the `IntentRouter`.
3. Select agents based on detected intents:
   - `shortage_agent`
   - `coverage_agent`
   - `authenticity_agent`
4. Persist an `AgentRun` for each execution.
5. Retrieve relevant memory notes by payer, drug, supplier, and location scope.
6. Merge outputs with the `SynthesisAgent`.
7. Validate safety and compliance language through the guardrail layer.
8. Store the final response payload for later retrieval.

## Agent responsibilities

- Shortage Agent: inventory pressure, shortage events, recall overlap, substitution workflow guidance.
- Coverage Agent: payer policy matching, missing evidence detection, denial interpretation, appeal drafting.
- Authenticity Agent: suspicious claims, missing NDC or lot data, supplier-risk red flags, counseling language.
