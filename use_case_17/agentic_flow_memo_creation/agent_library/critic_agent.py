from agents import Agent, function_tool
from schemas import Evaluation_Report
from agent_config_loader import load_agent_config


def create_critic_agent() -> Agent:
    cfg = load_agent_config("Critic Agent")

    return Agent(
        name=cfg["name"],
        model=cfg["model"],
        instructions=cfg["instructions"],
        output_type=Evaluation_Report,
    )

def get_critic_tool():
    
    critic_agent = create_critic_agent()

    return critic_agent.as_tool(
        tool_name="run_qc",
        tool_description=("""
            Performs a quality and factuality review of the briefing memo outline and/or section drafts.
            Returns an evaluation report with a rating and comments.
            """
        ),
    )