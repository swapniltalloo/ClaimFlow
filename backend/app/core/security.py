import hashlib
import json
from typing import Any, Dict


def compute_input_hash(payload: Any) -> str:
    """Computes a SHA-256 hash of any input payload for immutable audit trail verification."""
    if isinstance(payload, dict):
        serialized = json.dumps(payload, sort_keys=True, default=str)
    elif isinstance(payload, str):
        serialized = payload
    elif hasattr(payload, "model_dump"):
        serialized = json.dumps(payload.model_dump(), sort_keys=True, default=str)
    else:
        serialized = str(payload)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def mask_phi(text: str) -> str:
    """Masks synthetic identification numbers and sensitive text for safe logging."""
    # Synthetic UHID masking, e.g. UHID-12345678 -> UHID-****5678
    import re
    return re.sub(r'(UHID|POL|PAT)-(\d{4})(\d{4})', r'\1-****\3', text)
