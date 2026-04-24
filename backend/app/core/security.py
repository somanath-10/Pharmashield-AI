from __future__ import annotations

import hashlib
import json
from typing import Any


def hash_patient_context(payload: dict[str, Any] | None) -> str:
    serialized = json.dumps(payload or {}, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
