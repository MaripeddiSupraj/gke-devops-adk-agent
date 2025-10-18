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
from .security_scanner import security_scan
from .cost_optimizer import analyze_costs
from .advanced_security import advanced_security_scan

# === MAIN ADK AGENT CONFIGURATION ===
# Create the GKE DevOps agent with all enterprise-grade tools
root_agent = Agent(
    model="gemini-2.0-flash",  # Google's latest Gemini model for optimal performance
    name="gke_devops_agent",
    description="Enterprise GKE DevOps agent for comprehensive cluster monitoring and management",
    instruction=(
        "You are an expert GKE DevOps assistant that provides comprehensive Kubernetes cluster management. "
        "You have access to 7 enterprise-grade tools for monitoring, security, and cost optimization. "
        "CRITICAL: Always return the complete formatted_response from tools exactly as provided. "
        "Never summarize or modify the professional dashboard outputs. Display full metrics and insights."
    ),
    # === AVAILABLE TOOLS ===
    # Complete toolkit for enterprise Kubernetes management
    tools=[
        check_cluster_health,      # Comprehensive cluster health monitoring
        get_pod_status,           # Detailed pod status and lifecycle tracking
        list_deployments,         # Deployment monitoring and management
        diagnose_issues,          # Intelligent issue detection and troubleshooting
        security_scan,            # Production security scanning (CIS + NSA standards)
        analyze_costs,            # Cost optimization and savings analysis
        advanced_security_scan    # Enterprise security with CVE scanning and compliance
    ]
)