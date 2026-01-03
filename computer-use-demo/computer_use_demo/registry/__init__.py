"""
Proto Computer Registry Module.

Tracks all computers in the network and their capabilities.

Usage:
    from computer_use_demo.registry import (
        get_computer_registry,
        Computer,
        ComputerCapability,
    )

    # Get the registry
    registry = get_computer_registry()

    # Register a computer
    computer = Computer(
        id="computer-1",
        name="Dev Machine",
        capabilities=[ComputerCapability.CODE_EXECUTION, ComputerCapability.BROWSER],
    )
    await registry.register(computer)

    # Find computers by capability
    browsers = await registry.find_by_capability(ComputerCapability.BROWSER)
"""

from .types import (
    Computer,
    ComputerCapability,
    ComputerStatus,
    ComputerHealth,
    ComputerMetrics,
)

from .registry import (
    ComputerRegistry,
    get_computer_registry,
    shutdown_registry,
)

from .discovery import (
    ComputerDiscovery,
    DiscoveryMethod,
)

__all__ = [
    # Types
    "Computer",
    "ComputerCapability",
    "ComputerStatus",
    "ComputerHealth",
    "ComputerMetrics",
    # Registry
    "ComputerRegistry",
    "get_computer_registry",
    "shutdown_registry",
    # Discovery
    "ComputerDiscovery",
    "DiscoveryMethod",
]
