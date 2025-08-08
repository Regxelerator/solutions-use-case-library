from __future__ import annotations
from typing import Any
import logging

log = logging.getLogger(__name__)

DRAFT: dict[str, Any] = {}


def apply_patch(patch: list[dict]) -> None:
    for op in patch:
        if not isinstance(op, dict):
            log.warning("Skipping non-dict patch entry: %r", op)
            continue
        if "op" not in op or "path" not in op or "value" not in op:
            log.warning("Skipping malformed patch entry: %r", op)
            continue
        if op["op"] not in {"add", "replace"}:
            log.debug("Ignoring unsupported op %s", op["op"])
            continue

        keys = op["path"].lstrip("/").split("/")
        ref = DRAFT
        for k in keys[:-1]:
            ref = ref.setdefault(k, {})
        ref[keys[-1]] = op["value"]