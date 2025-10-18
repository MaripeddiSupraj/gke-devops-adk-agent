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
from kubernetes.client.exceptions import ApiException

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
        pods = k8s_v1.list_namespaced_pod(namespace)
        issues = []

        for pod in pods.items:
            if pod.status.phase not in ["Running", "Succeeded"]:
                reason = pod.status.reason
                message = pod.status.message
                details = f"Pod is {pod.status.phase}."

                if pod.status.container_statuses:
                    for cs in pod.status.container_statuses:
                        if cs.state.waiting:
                            reason = cs.state.waiting.reason
                            message = cs.state.waiting.message
                            details = f"Container {cs.name} is waiting: {reason} - {message}"
                            break
                        if cs.state.terminated:
                            reason = cs.state.terminated.reason
                            message = cs.state.terminated.message
                            details = f"Container {cs.name} terminated: {reason} (Exit code: {cs.state.terminated.exit_code}) - {message}"
                            break
                
                issues.append(
                    f"{pod.metadata.name:<40} {pod.status.phase:<12} {reason:<20} {details}"
                )

        if not issues:
            issue_details = "No issues detected. All pods are healthy! 🎉"
            count = 0
        else:
            issue_details = chr(10).join(issues)
            count = len(issues)

        return {
            "status": "success",
            "formatted_response": f"""
🔍 **Cluster Diagnostics - {namespace}**

**{count} issues found.**

```
NAME                                     STATUS       REASON               DETAILS
{issue_details}
```
            """
        }
    except ApiException as e:
        return {"status": "error", "error_message": f"Kubernetes API error: {e.reason}"}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}