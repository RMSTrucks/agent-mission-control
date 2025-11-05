"""
Memory System Integration

Connectors for Temporal Memory and Hybrid Intelligence MCPs,
plus unified memory management and synchronization.
"""

from .temporal_connector import (
    TemporalMemoryConnector,
    create_temporal_connector,
    MemoryItem,
    MemoryResponse
)

from .hybrid_connector import (
    HybridIntelligenceConnector,
    create_hybrid_connector,
    Conversation,
    SearchResult,
    HybridResponse
)

from .memory_sync import (
    MemoryManager,
    get_memory_manager,
    AgentContext,
    SyncStatus
)

__all__ = [
    # Temporal Memory
    'TemporalMemoryConnector',
    'create_temporal_connector',
    'MemoryItem',
    'MemoryResponse',
    # Hybrid Intelligence
    'HybridIntelligenceConnector',
    'create_hybrid_connector',
    'Conversation',
    'SearchResult',
    'HybridResponse',
    # Memory Manager
    'MemoryManager',
    'get_memory_manager',
    'AgentContext',
    'SyncStatus',
]
