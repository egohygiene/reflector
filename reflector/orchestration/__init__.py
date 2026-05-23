"""Reflector orchestration package.

Implements the milestone orchestration layer described in milestone_execution.tex.
Manages milestone lifecycle, governance checkpoint evaluation, and progression
approval workflows.
"""

from reflector.orchestration.milestone import MilestoneOrchestrator

__all__ = ["MilestoneOrchestrator"]
