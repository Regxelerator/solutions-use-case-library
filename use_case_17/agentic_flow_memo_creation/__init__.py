"""
Expose the agent packages that live under `agentic_flow_memo_creation/`
under their original import names so that existing code such as

    from agent_library import Runner
    from tools.content_loader import content_loader

continues to work without modification.
"""
import sys
from importlib import import_module
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Ensure the folder itself is on sys.path
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# ------------------------------------------------------------------
# Aliases – point the old import names at the new sub‑modules
# ------------------------------------------------------------------
sys.modules['agent_library']        = import_module('agentic_flow_memo_creation.agent_library')
sys.modules['tools']               = import_module('agentic_flow_memo_creation.tools')
sys.modules['schemas']             = import_module('agentic_flow_memo_creation.schemas')
sys.modules['agent_config_loader'] = import_module('agentic_flow_memo_creation.agent_config_loader')