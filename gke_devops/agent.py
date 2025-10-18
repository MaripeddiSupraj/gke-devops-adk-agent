#!/usr/bin/env python3
"""
GKE DevOps Agent - Main Agent Module

This is the main ADK agent that orchestrates all GKE monitoring capabilities:
- Integrates cluster health, pod monitoring, deployment management, and diagnostics
- Provides conversational AI interface for Kubernetes cluster management
- Built with Google ADK and Gemini 2.0 Flash for natural language processing
- Returns professional dashboard-style formatted responses

Author: GKE DevOps Team
"""

from google.adk.agents.llm_agent import Agent
from .cluster_health import check_cluster_health
from .pod_monitor import get_pod_status
from .deployment_manager import list_deployments
from .diagnostics import diagnose_issues

# Create the GKE DevOps agent with modular tools
root_agent = Agent(
    model="gemini-2.0-flash",
    name="gke_devops_agent",
    description="GKE DevOps agent for cluster monitoring and management via web chat interface",
    instruction=(
        "You are a GKE DevOps assistant that can monitor and manage Kubernetes clusters. "
        "When users ask about cluster health, pod status, deployments, or issues, use the appropriate tools to get real-time information. "
        "IMPORTANT: Always return the complete formatted_response from the tools exactly as provided. "
        "Never summarize or paraphrase the formatted dashboard output. Show the full dashboard with emojis, dividers, and detailed metrics."
    ),
    tools=[check_cluster_health, get_pod_status, list_deployments, diagnose_issues]
)