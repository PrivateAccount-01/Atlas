# AtlasCore Repository Guardrails

Purpose
-------

This document records the guardrails for implementing the AtlasCore foundation
layer. The foundation enforces strict anti-hallucination rules, typed errors,
provenance, contracts, validators, and tests. Any change that violates these
rules must be rejected.

Hard rules (short)
------------------

1. Never create fake predictions or fabricate scores or confidences.
2. Never use random values for intelligence outputs.
3. Never create mock production data outside `tests/fixtures/`.
4. Never create a signal, prediction, or graph edge without evidence and provenance.
5. Never silently ignore errors; use typed errors and fail loudly.
6. Never overwrite raw data; write transformed artifacts separately.
7. Do not introduce RL, LLM extraction, GraphRAG, Neo4j, Qdrant, or prediction models in foundation.

Build order
-----------

1. Repository guardrail docs (this file)
2. Pydantic contracts (`src/atlascore/contracts`)
3. Typed errors (`src/atlascore/errors.py`)
4. Validators (`src/atlascore/validators.py`)
5. Domain-pack loader (`src/atlascore/domain_pack/loader.py`)
6. Provenance helpers (`src/atlascore/provenance.py`)
7. Sample `supply_chain` domain pack (architecture validation only)
8. Unit and contract tests (`tests/`)

Tech stack
----------

- Python 3.11+
- Pydantic v2
- PyYAML
- pytest
- ruff

Testing and fixtures
--------------------

- All synthetic fixtures MUST live in `tests/fixtures/` and be clearly named.
- Tests must assert evidence/provenance requirements and that raw data is immutable.

Change process
--------------

1. Before making code changes, list the files to change, contracts involved,
   validation rules added, and tests to be added. Get confirmation.
2. Implement Pydantic contracts and tests first. Validators and provenance
   helpers follow.
3. Reject or revert any change that fabricates results or uses unvalidated inputs.

If you want me to implement the next step, specify which build-order item to run.
