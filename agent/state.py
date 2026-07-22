"""
NEXUS-OSINT: Agent State Definition (LangGraph)
"""
from typing import Any, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class ReconState(TypedDict):
    """State schema for the autonomous recon agent."""
    # Input
    target: str
    investigation_goal: str

    # Messages (LLM conversation history)
    messages: Annotated[list, add_messages]

    # Graph context
    discovered_entities: list[dict[str, Any]]
    discovered_edges: list[dict[str, Any]]
    current_graph_summary: str

    # Agent control
    transforms_executed: list[str]
    iteration_count: int
    max_iterations: int
    should_continue: bool

    # Correlation results
    correlations_found: list[dict[str, Any]]

    # Final output
    investigation_report: str
    status: str  # "running", "completed", "error"
