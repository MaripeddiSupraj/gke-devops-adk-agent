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
    
    Args:
        namespace (str): Kubernetes namespace to diagnose (default: "default")
        
    Returns:
        dict: Formatted diagnostics report with issue details and recommendations
    """
    try:
        pods = k8s_v1.list_namespaced_pod(namespace)
        issues = []
        
        for pod in pods.items:
            if pod.status.phase in ["Failed", "Pending"]:
                issues.append({
                    "pod_name": pod.metadata.name,
                    "phase": pod.status.phase,
                    "reason": pod.status.reason or "Unknown"
                })
        
        if issues:
            issue_details = "\n".join([f"   • {issue['pod_name']}: {issue['phase']} - {issue['reason']}" for issue in issues])
            status_icon = "🔴"
            recommendation = "🔍 **Recommendation**: Check pod logs and events for detailed troubleshooting"
        else:
            issue_details = "   • No issues detected - all pods are healthy! 🎉"
            status_icon = "✅"
            recommendation = "🎉 **Great news**: Your cluster is running smoothly!"
            
        return {
            "status": "success",
            "formatted_response": f"""
🔍 **Cluster Diagnostics Report - {namespace} namespace**

{status_icon} **Issues Found**: {len(issues)}

📊 **Issue Details**:
{issue_details}

{recommendation}
            """
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}