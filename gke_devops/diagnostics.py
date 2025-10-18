#!/usr/bin/env python3
"""
GKE DevOps Agent - Cluster Diagnostics

This module provides intelligent cluster issue detection with:
- Failed and pending pod identification
- Root cause analysis and troubleshooting recommendations
- Professional diagnostic reporting with actionable insights

Author: GKE DevOps Team
"""

from .config import k8s_v1

def diagnose_issues(namespace: str = "default") -> dict:
    """
    Diagnose common cluster issues and failed pods with recommendations.
    
    Provides intelligent cluster issue detection including:
    - Failed and pending pod identification
    - Root cause analysis and troubleshooting recommendations
    - Professional diagnostic reporting with actionable insights
    
    Args:
        namespace (str): Kubernetes namespace to diagnose (default: "default")
        
    Returns:
        dict: Formatted diagnostics report with issue details and recommendations
    """
    try:
        # === ISSUE DETECTION ===
        # Scan all pods for failed or problematic states
        pods = k8s_v1.list_namespaced_pod(namespace)
        issues = []  # List to store identified issues
        
        # === POD ISSUE ANALYSIS ===
        # Identify pods in problematic states and extract failure reasons
        for pod in pods.items:
            if pod.status.phase in ["Failed", "Pending"]:
                issues.append({
                    "pod": pod.metadata.name,
                    "status": pod.status.phase,
                    "reason": pod.status.reason or "Unknown",
                    "command": f"kubectl describe pod {pod.metadata.name} -n {namespace}"
                })
        
        issue_details = ""
        if issues:
            status_icon = "🔴"
            issue_list = []
            for issue in issues:
                issue_list.append(f"Pod    : {issue['pod']} ({issue['status']})")
                issue_list.append(f"Reason : {issue['reason']}")
                issue_list.append(f"Action : {issue['command']}\n")
            issue_details = "```\n" + "\n".join(issue_list) + "```"
        else:
            status_icon = "✅"
            issue_details = "No issues detected. All pods are healthy! 🎉\n"
            
        return {
            "status": "success",
            "formatted_response": f"""
🔍 **Cluster Diagnostics Report - {namespace} namespace**
{status_icon} **Issues Found**: {len(issues)}
{issue_details}
            """
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}