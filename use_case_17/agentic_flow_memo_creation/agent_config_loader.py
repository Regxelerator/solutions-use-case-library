from pathlib import Path
import yaml
from typing import Dict

_DEFAULT_YAML = Path(__file__).resolve().parent / "agents_list.yaml"

def load_agent_config(agent_name: str, yaml_path=_DEFAULT_YAML) -> Dict:

    data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    for cfg in data.get("agents", []):
        if cfg.get("name") == agent_name:
            return cfg
    raise ValueError(f"Agent '{agent_name}' not defined in {yaml_path}")
