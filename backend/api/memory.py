"""
Memory API Endpoints

Handles Temporal Memory and Hybrid Intelligence operations,
including facts, preferences, conversation search, and agent context.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from memory import get_memory_manager

router = APIRouter(prefix="/memory", tags=["memory"])

# Initialize Memory Manager
memory_manager = get_memory_manager()


# ========================================================================
# Request Models
# ========================================================================

class SearchConversationsRequest(BaseModel):
    """Request to search conversations"""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum results")


class AddFactRequest(BaseModel):
    """Request to add a fact"""
    content: str = Field(..., description="Fact content")
    tier: int = Field(3, ge=1, le=3, description="Fact tier (1=highest, 3=lowest)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AddPreferenceRequest(BaseModel):
    """Request to add a preference"""
    content: str = Field(..., description="Preference content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AddContextRequest(BaseModel):
    """Request to add context item"""
    content: str = Field(..., description="Context content")
    agent_id: Optional[str] = Field(None, description="Agent this context applies to")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# ========================================================================
# Temporal Memory Endpoints
# ========================================================================

@router.get("/facts")
async def get_facts(
    tier: Optional[int] = Query(None, ge=1, le=3, description="Filter by tier"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results")
):
    """
    Get curated facts from Temporal Memory.

    Args:
        tier: Filter by tier (1=most important, 3=least important)
        limit: Maximum number of facts

    Returns:
        List of facts with tier information
    """
    try:
        facts = memory_manager.get_facts(tier=tier, limit=limit)

        return {
            "success": True,
            "facts": [
                {
                    "id": f.id,
                    "tier": f.tier,
                    "content": f.content,
                    "metadata": f.metadata,
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in facts
            ],
            "count": len(facts)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get facts: {str(e)}"
        )


@router.get("/preferences")
async def get_preferences(
    limit: int = Query(100, ge=1, le=500, description="Maximum results")
):
    """
    Get user preferences from Temporal Memory.

    Args:
        limit: Maximum number of preferences

    Returns:
        List of preferences
    """
    try:
        preferences = memory_manager.get_preferences(limit=limit)

        return {
            "success": True,
            "preferences": [
                {
                    "id": p.id,
                    "content": p.content,
                    "metadata": p.metadata,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in preferences
            ],
            "count": len(preferences)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences: {str(e)}"
        )


@router.get("/context/{agent_id}")
async def get_agent_context(agent_id: str):
    """
    Get complete context for an agent.

    This combines facts, preferences, context items, and relevant
    conversation history into a complete context package.

    Args:
        agent_id: Agent identifier

    Returns:
        Complete agent context
    """
    try:
        context = memory_manager.get_agent_context(agent_id)

        return {
            "success": True,
            "agent_id": agent_id,
            "context": {
                "facts": [
                    {
                        "id": f.id,
                        "tier": f.tier,
                        "content": f.content
                    }
                    for f in context.facts
                ],
                "preferences": [
                    {
                        "id": p.id,
                        "content": p.content
                    }
                    for p in context.preferences
                ],
                "context_items": [
                    {
                        "id": c.id,
                        "content": c.content
                    }
                    for c in context.context_items
                ],
                "relevant_conversations": [
                    {
                        "id": conv.id,
                        "summary": conv.summary,
                        "relevance_score": conv.relevance_score
                    }
                    for conv in context.relevant_conversations
                ],
                "last_updated": context.last_updated.isoformat()
            },
            "formatted": memory_manager.format_context_for_agent(agent_id)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent context: {str(e)}"
        )


@router.post("/facts", status_code=status.HTTP_201_CREATED)
async def add_fact(request: AddFactRequest):
    """
    Add a new fact to Temporal Memory.

    Args:
        request: Fact details

    Returns:
        Created fact
    """
    try:
        response = memory_manager.temporal.add_fact(
            content=request.content,
            tier=request.tier,
            metadata=request.metadata
        )

        if response.success:
            fact = response.data
            return {
                "success": True,
                "fact": {
                    "id": fact.id,
                    "tier": fact.tier,
                    "content": fact.content,
                    "metadata": fact.metadata
                },
                "message": "Fact added successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add fact: {str(e)}"
        )


@router.post("/preferences", status_code=status.HTTP_201_CREATED)
async def add_preference(request: AddPreferenceRequest):
    """
    Add a new preference to Temporal Memory.

    Args:
        request: Preference details

    Returns:
        Created preference
    """
    try:
        response = memory_manager.temporal.add_preference(
            content=request.content,
            metadata=request.metadata
        )

        if response.success:
            pref = response.data
            return {
                "success": True,
                "preference": {
                    "id": pref.id,
                    "content": pref.content,
                    "metadata": pref.metadata
                },
                "message": "Preference added successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.error
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add preference: {str(e)}"
        )


# ========================================================================
# Hybrid Intelligence Endpoints
# ========================================================================

@router.post("/search")
async def search_conversations(request: SearchConversationsRequest):
    """
    Search conversations using Hybrid Intelligence.

    Full-text search across 29K+ indexed conversations.

    Args:
        request: Search configuration

    Returns:
        Search results with matching conversations
    """
    try:
        conversations = memory_manager.search_conversations(
            query=request.query,
            limit=request.limit
        )

        return {
            "success": True,
            "query": request.query,
            "results": [
                {
                    "id": c.id,
                    "summary": c.summary,
                    "content": c.content[:200] + "..." if len(c.content) > 200 else c.content,
                    "relevance_score": c.relevance_score,
                    "timestamp": c.timestamp.isoformat(),
                    "metadata": c.metadata
                }
                for c in conversations
            ],
            "count": len(conversations)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/conversations/recent")
async def get_recent_conversations(
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """
    Get recent conversations from Hybrid Intelligence.

    Args:
        limit: Maximum number of conversations

    Returns:
        List of recent conversations
    """
    try:
        conversations = memory_manager.get_recent_conversations(limit=limit)

        return {
            "success": True,
            "conversations": [
                {
                    "id": c.id,
                    "summary": c.summary,
                    "timestamp": c.timestamp.isoformat(),
                    "metadata": c.metadata
                }
                for c in conversations
            ],
            "count": len(conversations)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent conversations: {str(e)}"
        )


# ========================================================================
# Synchronization Endpoints
# ========================================================================

@router.post("/sync")
async def sync_memory():
    """
    Synchronize with all memory systems.

    Refreshes data from:
    - Temporal Memory MCP (facts, preferences, context)
    - Hybrid Intelligence MCP (conversation index)

    Returns:
        Sync status and any errors
    """
    try:
        sync_status = memory_manager.sync_all()

        return {
            "success": sync_status.success,
            "temporal_synced": sync_status.temporal_synced,
            "hybrid_synced": sync_status.hybrid_synced,
            "errors": sync_status.errors,
            "timestamp": sync_status.timestamp.isoformat(),
            "message": "Sync completed" if sync_status.success else "Sync failed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


@router.post("/sync/temporal")
async def sync_temporal_only():
    """
    Sync only Temporal Memory.

    Returns:
        Sync status
    """
    try:
        success = memory_manager.sync_temporal_only()

        return {
            "success": success,
            "message": "Temporal Memory synced" if success else "Sync failed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Temporal sync failed: {str(e)}"
        )


# ========================================================================
# Statistics & Status Endpoints
# ========================================================================

@router.get("/stats")
async def get_memory_stats():
    """
    Get statistics from all memory systems.

    Returns:
        Memory statistics including counts and index sizes
    """
    try:
        stats = memory_manager.get_memory_stats()

        return {
            "success": True,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/status")
async def get_memory_status():
    """
    Get health status of all memory systems.

    Returns:
        Health status for each system
    """
    try:
        status_info = memory_manager.get_health_status()

        return {
            "success": True,
            "status": status_info
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )
