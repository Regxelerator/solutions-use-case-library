from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class IncidentRunContext:
    last_patch: List[Dict[str, Any]] = field(default_factory=list)
    active_agent_name: Optional[str] = None
