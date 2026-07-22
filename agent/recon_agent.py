"""
NEXUS-OSINT: Autonomous AI Recon Agent (LangGraph)
Orchestrates autonomous OSINT investigations using tool-calling LLM.
"""
import asyncio
import json
import os
from typing import Any

import structlog
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from state import ReconState
from tools import ALL_TOOLS
from prompts import SYSTEM_PROMPT, INVESTIGATION_PROMPT
from correlation import CorrelationEngine

logger = structlog.get_logger(__name__)


class ReconAgent:
    """
    Autonomous OSINT investigation agent built on LangGraph.
    Accepts a target, autonomously decides which transforms to run,
    and produces a structured intelligence report.
    """

    def __init__(self):
        self._llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "qwen2.5:72b"),
            openai_api_key=os.getenv("LLM_API_KEY", "not-needed"),
            openai_api_base=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
            temperature=0.1,
            max_tokens=4096,
        ).bind_tools(ALL_TOOLS)

        self._correlation_engine = CorrelationEngine(
            qdrant_host=os.getenv("QDRANT_HOST", "qdrant"),
            qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        )

        self._graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Construct the LangGraph workflow."""
        workflow = StateGraph(ReconState)

        # Add nodes
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("execute_tools", self._execute_tools_node)
        workflow.add_node("correlate", self._correlate_node)
        workflow.add_node("report", self._report_node)

        # Set entry point
        workflow.set_entry_point("plan")

        # Define edges
        workflow.add_conditional_edges(
            "plan",
            self._should_continue,
            {
                "execute": "execute_tools",
                "correlate": "correlate",
                "report": "report",
            },
        )
        workflow.add_edge("execute_tools", "plan")
        workflow.add_edge("correlate", "plan")
        workflow.add_edge("report", END)

        return workflow.compile()

    async def _plan_node(self, state: ReconState) -> dict:
        """LLM decides next action based on current state."""
        system_msg = SystemMessage(
            content=SYSTEM_PROMPT.format(max_iterations=state.get("max_iterations", 10))
        )

        investigation_msg = HumanMessage(
            content=INVESTIGATION_PROMPT.format(
                target=state["target"],
                goal=state["investigation_goal"],
                graph_summary=state.get("current_graph_summary", "No data yet."),
                transforms_executed=json.dumps(state.get("transforms_executed", []), indent=2),
                discovered_entities=json.dumps(state.get("discovered_entities", [])[:20], indent=2),
            )
        )

        messages = [system_msg] + state.get("messages", []) + [investigation_msg]

        response = await self._llm.ainvoke(messages)

        return {
            "messages": [response],
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    async def _execute_tools_node(self, state: ReconState) -> dict:
        """Execute tool calls from the LLM response."""
        last_message = state["messages"][-1]

        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return {"should_continue": False}

        new_entities = list(state.get("discovered_entities", []))
        new_edges = list(state.get("discovered_edges", []))
        transforms_executed = list(state.get("transforms_executed", []))

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            logger.info("agent.tool_call", tool=tool_name, args=tool_args)
            transforms_executed.append(f"{tool_name}({json.dumps(tool_args)})")

            # Find and execute the tool
            for t in ALL_TOOLS:
                if t.name == tool_name:
                    try:
                        result = await t.ainvoke(tool_args)
                        # Parse result for new entities
                        if isinstance(result, str) and "new_nodes" in result:
                            try:
                                data = json.loads(result.split(": ", 1)[1])
                                new_entities.extend(data.get("new_nodes", []))
                                new_edges.extend(data.get("new_edges", []))
                            except (json.JSONDecodeError, IndexError):
                                pass
                    except Exception as e:
                        logger.error("agent.tool_error", tool=tool_name, error=str(e))
                    break

        return {
            "discovered_entities": new_entities,
            "discovered_edges": new_edges,
            "transforms_executed": transforms_executed,
        }

    async def _correlate_node(self, state: ReconState) -> dict:
        """Run semantic correlation on discovered entities."""
        entities = state.get("discovered_entities", [])
        correlations = list(state.get("correlations_found", []))

        # Index all entities
        await self._correlation_engine.batch_index(entities)

        # Find cross-type correlations
        for entity in entities[:10]:  # Limit to prevent overload
            try:
                found = await self._correlation_engine.find_correlations(entity)
                correlations.extend(found)
            except Exception as e:
                logger.warning("agent.correlation_error", error=str(e))

        return {"correlations_found": correlations}

    async def _report_node(self, state: ReconState) -> dict:
        """Generate final investigation report."""
        summary_prompt = f"""
        Generate a comprehensive OSINT investigation report based on the following findings:

        Target: {state['target']}
        Goal: {state['investigation_goal']}

        Discovered Entities ({len(state.get('discovered_entities', []))} total):
        {json.dumps(state.get('discovered_entities', [])[:30], indent=2)}

        Relationships ({len(state.get('discovered_edges', []))} total):
        {json.dumps(state.get('discovered_edges', [])[:20], indent=2)}

        Correlations Found ({len(state.get('correlations_found', []))} total):
        {json.dumps(state.get('correlations_found', [])[:15], indent=2)}

        Transforms Executed:
        {json.dumps(state.get('transforms_executed', []), indent=2)}

        Format as a structured intelligence report with:
        1. Executive Summary
        2. Entity Inventory (by type)
        3. Key Relationships
        4. Hidden Correlations
        5. Threat Assessment
        6. Recommendations
        """

        response = await self._llm.ainvoke([HumanMessage(content=summary_prompt)])

        return {
            "investigation_report": response.content,
            "status": "completed",
        }

    def _should_continue(self, state: ReconState) -> str:
        """Routing logic: continue investigating or generate report."""
        iteration = state.get("iteration_count", 0)
        max_iter = state.get("max_iterations", 10)

        if iteration >= max_iter:
            return "report"

        last_message = state.get("messages", [])[-1] if state.get("messages") else None

        if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            # Check if correlation tools were called
            tool_names = [tc["name"] for tc in last_message.tool_calls]
            if "find_semantic_correlations" in tool_names:
                return "correlate"
            return "execute"

        # If no tool calls and we have enough data, correlate then report
        if len(state.get("discovered_entities", [])) > 5:
            return "correlate"

        return "report"

    async def investigate(
        self,
        target: str,
        goal: str = "Conduct comprehensive OSINT investigation",
        max_iterations: int = 10,
    ) -> ReconState:
        """
        Run a full autonomous investigation.

        Args:
            target: The investigation target (domain, IP, email, etc.)
            goal: What to investigate / what questions to answer
            max_iterations: Maximum number of investigation loops

        Returns:
            Final state with investigation report
        """
        initial_state: ReconState = {
            "target": target,
            "investigation_goal": goal,
            "messages": [],
            "discovered_entities": [],
            "discovered_edges": [],
            "current_graph_summary": "",
            "transforms_executed": [],
            "iteration_count": 0,
            "max_iterations": max_iterations,
            "should_continue": True,
            "correlations_found": [],
            "investigation_report": "",
            "status": "running",
        }

        logger.info("agent.investigation_started", target=target, goal=goal)

        final_state = await self._graph.ainvoke(initial_state)

        logger.info(
            "agent.investigation_completed",
            target=target,
            entities_found=len(final_state.get("discovered_entities", [])),
            correlations=len(final_state.get("correlations_found", [])),
        )

        return final_state


# ─── FastAPI wrapper for the agent service ───
async def main():
    """Run the agent as a standalone FastAPI service."""
    from fastapi import FastAPI
    from pydantic import BaseModel
    import uvicorn

    app = FastAPI(title="NEXUS-OSINT Agent Service")
    agent = ReconAgent()

    class InvestigateRequest(BaseModel):
        target: str
        goal: str = "Conduct comprehensive OSINT investigation"
        max_iterations: int = 10

    class InvestigateResponse(BaseModel):
        status: str
        report: str
        entities_found: int
        correlations_found: int
        transforms_executed: list[str]

    @app.post("/investigate", response_model=InvestigateResponse)
    async def investigate(req: InvestigateRequest):
        state = await agent.investigate(
            target=req.target,
            goal=req.goal,
            max_iterations=req.max_iterations,
        )
        return InvestigateResponse(
            status=state.get("status", "completed"),
            report=state.get("investigation_report", ""),
            entities_found=len(state.get("discovered_entities", [])),
            correlations_found=len(state.get("correlations_found", [])),
            transforms_executed=state.get("transforms_executed", []),
        )

    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "nexus-agent"}

    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    asyncio.run(main())
