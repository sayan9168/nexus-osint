"""
NEXUS-OSINT: WebSocket Endpoint for Real-Time Graph Updates
Broadcasts new nodes/edges as the AI Agent discovers them.
"""
import asyncio
import json
from typing import Any
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time graph updates."""

    def __init__(self):
        self._connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.append(websocket)
        logger.info("ws.client_connected", total=len(self._connections))

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self._connections:
                self._connections.remove(websocket)
        logger.info("ws.client_disconnected", total=len(self._connections))

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcast a message to all connected clients."""
        payload = json.dumps({
            **message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        disconnected = []
        async with self._lock:
            for ws in self._connections:
                try:
                    await ws.send_text(payload)
                except Exception:
                    disconnected.append(ws)
            for ws in disconnected:
                self._connections.remove(ws)

    async def send_node_added(self, node: dict[str, Any]) -> None:
        await self.broadcast({"type": "node_added", "data": node})

    async def send_edge_added(self, edge: dict[str, Any]) -> None:
        await self.broadcast({"type": "edge_added", "data": edge})

    async def send_transform_started(self, transform_name: str, entity: str) -> None:
        await self.broadcast({
            "type": "transform_started",
            "data": {"transform": transform_name, "entity": entity},
        })

    async def send_transform_completed(self, result: dict[str, Any]) -> None:
        await self.broadcast({"type": "transform_completed", "data": result})

    async def send_agent_update(self, message: str, iteration: int) -> None:
        await self.broadcast({
            "type": "agent_update",
            "data": {"message": message, "iteration": iteration},
        })

    @property
    def active_connections(self) -> int:
        return len(self._connections)


# Global connection manager
ws_manager = ConnectionManager()


@router.websocket("/ws/graph")
async def websocket_graph_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time graph updates.
    Clients connect here to receive live updates as the AI Agent discovers entities.

    Message types:
    - node_added: New entity discovered
    - edge_added: New relationship discovered
    - transform_started: A transform began execution
    - transform_completed: A transform finished
    - agent_update: AI Agent status message
    - graph_snapshot: Full graph state (on request)
    """
    await ws_manager.connect(websocket)

    try:
        # Send initial graph snapshot
        from db.memgraph import get_memgraph
        memgraph = await get_memgraph()
        graph_data = await memgraph.get_full_graph(limit=5000)
        await websocket.send_text(json.dumps({
            "type": "graph_snapshot",
            "data": graph_data,
            "timestamp": datetime.utcnow().isoformat(),
        }))

        # Listen for client messages (commands)
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type", "")

                if msg_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

                elif msg_type == "request_snapshot":
                    graph_data = await memgraph.get_full_graph(limit=10000)
                    await websocket.send_text(json.dumps({
                        "type": "graph_snapshot",
                        "data": graph_data,
                    }))

                elif msg_type == "subscribe_filter":
                    # Client can filter by entity type
                    pass

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "Invalid JSON"},
                }))

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error("ws.error", error=str(e))
        await ws_manager.disconnect(websocket)
