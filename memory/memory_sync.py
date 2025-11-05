"""
Memory Synchronization

Coordinates synchronization between Temporal Memory and Hybrid Intelligence MCPs.
Provides unified interface for memory management and context loading.
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from .temporal_connector import (
    TemporalMemoryConnector,
    create_temporal_connector,
    MemoryItem
)
from .hybrid_connector import (
    HybridIntelligenceConnector,
    create_hybrid_connector,
    Conversation
)

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """
    Complete context for an agent, combining temporal memory and
    hybrid intelligence data.
    """
    agent_id: str
    facts: List[MemoryItem]
    preferences: List[MemoryItem]
    context_items: List[MemoryItem]
    relevant_conversations: List[Conversation]
    last_updated: datetime


@dataclass
class SyncStatus:
    """Status of a synchronization operation"""
    success: bool
    temporal_synced: bool
    hybrid_synced: bool
    errors: List[str]
    timestamp: datetime


class MemoryManager:
    """
    Unified memory management system.

    Coordinates between Temporal Memory and Hybrid Intelligence MCPs,
    providing a single interface for all memory operations.
    """

    def __init__(
        self,
        temporal_config: Optional[Dict[str, Any]] = None,
        hybrid_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Memory Manager.

        Args:
            temporal_config: Configuration for Temporal Memory MCP
            hybrid_config: Configuration for Hybrid Intelligence MCP
        """
        self.temporal = create_temporal_connector(temporal_config)
        self.hybrid = create_hybrid_connector(hybrid_config)

        self._agent_contexts: Dict[str, AgentContext] = {}

        logger.info("Memory Manager initialized")

    # ========================================================================
    # Temporal Memory Operations
    # ========================================================================

    def get_facts(
        self,
        tier: Optional[int] = None,
        limit: int = 100
    ) -> List[MemoryItem]:
        """
        Get facts from Temporal Memory.

        Args:
            tier: Filter by tier (1, 2, or 3)
            limit: Maximum number of facts

        Returns:
            List of facts
        """
        response = self.temporal.get_facts(tier=tier, limit=limit)
        if response.success:
            return response.data
        else:
            logger.error(f"Failed to get facts: {response.error}")
            return []

    def get_preferences(self, limit: int = 100) -> List[MemoryItem]:
        """
        Get preferences from Temporal Memory.

        Args:
            limit: Maximum number of preferences

        Returns:
            List of preferences
        """
        response = self.temporal.get_preferences(limit=limit)
        if response.success:
            return response.data
        else:
            logger.error(f"Failed to get preferences: {response.error}")
            return []

    def get_context_items(
        self,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[MemoryItem]:
        """
        Get context items from Temporal Memory.

        Args:
            agent_id: Filter by agent ID
            limit: Maximum number of items

        Returns:
            List of context items
        """
        response = self.temporal.get_context(agent_id=agent_id, limit=limit)
        if response.success:
            return response.data
        else:
            logger.error(f"Failed to get context: {response.error}")
            return []

    # ========================================================================
    # Hybrid Intelligence Operations
    # ========================================================================

    def search_conversations(
        self,
        query: str,
        limit: int = 10
    ) -> List[Conversation]:
        """
        Search conversations using Hybrid Intelligence.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching conversations
        """
        response = self.hybrid.search_conversations(query=query, limit=limit)
        if response.success:
            return response.data.conversations
        else:
            logger.error(f"Search failed: {response.error}")
            return []

    def get_recent_conversations(self, limit: int = 10) -> List[Conversation]:
        """
        Get recent conversations.

        Args:
            limit: Maximum number of conversations

        Returns:
            List of recent conversations
        """
        response = self.hybrid.get_recent_conversations(limit=limit)
        if response.success:
            return response.data
        else:
            logger.error(f"Failed to get recent conversations: {response.error}")
            return []

    # ========================================================================
    # Agent Context
    # ========================================================================

    def get_agent_context(
        self,
        agent_id: str,
        include_conversations: bool = True,
        conversation_query: Optional[str] = None
    ) -> AgentContext:
        """
        Get complete context for an agent.

        Combines:
        - Relevant facts (tier 1 and 2)
        - User preferences
        - Agent-specific context items
        - Relevant conversation history (optional)

        Args:
            agent_id: Agent identifier
            include_conversations: Include relevant conversations
            conversation_query: Optional query for conversation search

        Returns:
            AgentContext with all relevant information
        """
        # Check cache first
        if agent_id in self._agent_contexts:
            cached = self._agent_contexts[agent_id]
            # Return cached if recent (< 5 minutes old)
            if (datetime.now() - cached.last_updated).seconds < 300:
                logger.info(f"Returning cached context for {agent_id}")
                return cached

        # Get facts (tier 1 and 2 are most important)
        tier1_facts = self.get_facts(tier=1)
        tier2_facts = self.get_facts(tier=2)
        all_facts = tier1_facts + tier2_facts

        # Get preferences
        preferences = self.get_preferences()

        # Get agent-specific context
        context_items = self.get_context_items(agent_id=agent_id)

        # Get relevant conversations if requested
        conversations = []
        if include_conversations:
            query = conversation_query or agent_id
            conversations = self.search_conversations(query=query, limit=5)

        # Build context
        context = AgentContext(
            agent_id=agent_id,
            facts=all_facts,
            preferences=preferences,
            context_items=context_items,
            relevant_conversations=conversations,
            last_updated=datetime.now()
        )

        # Cache for future use
        self._agent_contexts[agent_id] = context

        return context

    def format_context_for_agent(self, agent_id: str) -> str:
        """
        Format agent context as a string for injection into agent prompts.

        Args:
            agent_id: Agent identifier

        Returns:
            Formatted context string
        """
        context = self.get_agent_context(agent_id)

        sections = []

        # Add facts
        if context.facts:
            sections.append("FACTS:")
            for fact in context.facts[:10]:  # Top 10 most important
                sections.append(f"- {fact.content}")

        # Add preferences
        if context.preferences:
            sections.append("\nPREFERENCES:")
            for pref in context.preferences[:5]:  # Top 5 preferences
                sections.append(f"- {pref.content}")

        # Add context items
        if context.context_items:
            sections.append("\nCONTEXT:")
            for item in context.context_items:
                sections.append(f"- {item.content}")

        return "\n".join(sections)

    # ========================================================================
    # Synchronization
    # ========================================================================

    def sync_all(self) -> SyncStatus:
        """
        Sync with all memory systems.

        Returns:
            SyncStatus with results
        """
        errors = []
        temporal_synced = False
        hybrid_synced = False

        # Sync Temporal Memory
        try:
            temporal_response = self.temporal.sync()
            if temporal_response.success:
                temporal_synced = True
                logger.info("Temporal Memory synced successfully")
            else:
                errors.append(f"Temporal: {temporal_response.error}")
        except Exception as e:
            errors.append(f"Temporal sync error: {str(e)}")

        # Sync Hybrid Intelligence (if applicable)
        try:
            hybrid_response = self.hybrid.health_check()
            if hybrid_response.success:
                hybrid_synced = True
                logger.info("Hybrid Intelligence health check passed")
            else:
                errors.append(f"Hybrid: {hybrid_response.error}")
        except Exception as e:
            errors.append(f"Hybrid check error: {str(e)}")

        # Clear cached contexts after sync
        self._agent_contexts.clear()

        return SyncStatus(
            success=temporal_synced and hybrid_synced,
            temporal_synced=temporal_synced,
            hybrid_synced=hybrid_synced,
            errors=errors,
            timestamp=datetime.now()
        )

    def sync_temporal_only(self) -> bool:
        """
        Sync only Temporal Memory.

        Returns:
            True if successful
        """
        response = self.temporal.sync()
        if response.success:
            self._agent_contexts.clear()
            return True
        return False

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get combined statistics from all memory systems.

        Returns:
            Dictionary with memory statistics
        """
        stats = {}

        # Temporal Memory stats
        temporal_response = self.temporal.get_stats()
        if temporal_response.success:
            stats["temporal"] = temporal_response.data

        # Hybrid Intelligence stats
        hybrid_response = self.hybrid.get_stats()
        if hybrid_response.success:
            stats["hybrid"] = hybrid_response.data

        # Cached contexts
        stats["cached_contexts"] = len(self._agent_contexts)

        return stats

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of all memory systems.

        Returns:
            Dictionary with health status
        """
        status = {
            "temporal": {
                "connected": self.temporal.connected,
                "status": "healthy" if self.temporal.connected else "disconnected"
            },
            "hybrid": {
                "connected": self.hybrid.connected,
                "status": "healthy" if self.hybrid.connected else "disconnected"
            },
            "overall": "healthy" if (self.temporal.connected and self.hybrid.connected) else "degraded"
        }

        return status


# ========================================================================
# Singleton Instance
# ========================================================================

_memory_manager_instance: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """
    Get global MemoryManager instance (singleton pattern).

    Returns:
        MemoryManager instance
    """
    global _memory_manager_instance

    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()

    return _memory_manager_instance


# ========================================================================
# Module-level test
# ========================================================================

if __name__ == "__main__":
    print("Testing Memory Manager...")

    manager = get_memory_manager()

    print("\nGetting facts...")
    facts = manager.get_facts(tier=1)
    print(f"Found {len(facts)} tier 1 facts")

    print("\nGetting preferences...")
    preferences = manager.get_preferences()
    print(f"Found {len(preferences)} preferences")

    print("\nSearching conversations...")
    conversations = manager.search_conversations("agent optimization")
    print(f"Found {len(conversations)} conversations")

    print("\nGetting agent context...")
    context = manager.get_agent_context("remus")
    print(f"Context for REMUS:")
    print(f"  - Facts: {len(context.facts)}")
    print(f"  - Preferences: {len(context.preferences)}")
    print(f"  - Conversations: {len(context.relevant_conversations)}")

    print("\nFormatting context...")
    formatted = manager.format_context_for_agent("remus")
    print(f"Formatted context ({len(formatted)} chars):")
    print(formatted[:200] + "...")

    print("\nSyncing all systems...")
    sync_status = manager.sync_all()
    print(f"Sync success: {sync_status.success}")
    print(f"  - Temporal: {sync_status.temporal_synced}")
    print(f"  - Hybrid: {sync_status.hybrid_synced}")

    print("\nGetting stats...")
    stats = manager.get_memory_stats()
    print(f"Memory stats: {stats}")

    print("\nSUCCESS: Memory Manager working!")
