from __future__ import annotations
import sys
import importlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

sys.modules["agent_library"]        = importlib.import_module("risk_agents.agent_library")
sys.modules["tools"]                = importlib.import_module("risk_agents.tools")
sys.modules["schemas"]              = importlib.import_module("risk_agents.schemas")
sys.modules["agent_config_loader"]  = importlib.import_module("risk_agents.agent_config_loader")
