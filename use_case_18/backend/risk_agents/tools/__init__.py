from .incident_tools import update_fields as update_fields_tool
from .incident_tools import get_form_status as get_form_status_tool

TOOL_REGISTRY = {
    "update_fields_tool": update_fields_tool,
    "get_form_status_tool": get_form_status_tool,
}
