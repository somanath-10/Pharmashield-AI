# Evaluation

Backend tests cover:

- Intent classification for multi-agent and authenticity/compliance cases
- Shortage agent inventory and workflow logic
- Coverage agent missing-evidence detection and appeal drafting
- Authenticity agent suspicious-claim escalation
- Coordinator end-to-end response synthesis
- Citation deduplication

Suggested manual checks:

1. Run `make up`.
2. Run `make seed`.
3. Analyze the demo Ozempic/Wegovy/online semaglutide case.
4. Confirm the response includes shortage, coverage, authenticity, action plan, draft messages, citations, and review requirement.
5. Submit feedback and confirm the correction appears under `/api/memory`.
