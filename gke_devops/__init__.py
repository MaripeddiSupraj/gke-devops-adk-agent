"""
GKE DevOps Agent Package

A professional Google ADK agent for Kubernetes cluster management through conversational AI.
Provides real-time monitoring, pod management, deployment oversight, and intelligent diagnostics.

Modules:
- config: Kubernetes client configuration
- cluster_health: Comprehensive cluster health monitoring  
- pod_monitor: Detailed pod status and lifecycle tracking
- deployment_manager: Deployment monitoring and management
- diagnostics: Intelligent issue detection and troubleshooting
- agent: Main ADK agent orchestrating all capabilities

Author: GKE DevOps Team
"""

from .agent import root_agent

__all__ = ['root_agent']