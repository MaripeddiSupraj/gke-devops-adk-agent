#!/usr/bin/env python3
"""
GKE DevOps Agent - Deployment Manager

This module provides deployment monitoring and management with:
- Replica status tracking and readiness verification
- Deployment health assessment and status reporting
- Professional formatting for deployment overview

Author: GKE DevOps Team
"""

from .config import k8s_apps_v1
from kubernetes.client.exceptions import ApiException
import datetime

def list_deployments(namespace: str = "default") -> dict:
    """
    List all deployments in the specified namespace with status details.
    
    Provides comprehensive deployment monitoring including:
    - Replica status tracking and readiness verification
    - Deployment health assessment and status reporting
    - Professional formatting for deployment overview
    
    Args:
        namespace (str): Kubernetes namespace to scan (default: "default")
        
    Returns:
        dict: Formatted deployment report with replica counts and status
    """
    try:
        deployments = k8s_apps_v1.list_namespaced_deployment(namespace)
        
        deployment_lines = []
        for dep in deployments.items:
            age = "Unknown"
            if dep.metadata.creation_timestamp:
                delta = datetime.datetime.now(datetime.timezone.utc) - dep.metadata.creation_timestamp
                if delta.days > 0:
                    age = f"{delta.days}d"
                else:
                    age = f"{delta.seconds // 3600}h"

            deployment_lines.append(
                f"{dep.metadata.name:<25} {dep.status.ready_replicas or 0}/{dep.spec.replicas:<5} "
                f"{dep.status.updated_replicas or 0:<12} {dep.status.available_replicas or 0:<11} {age}"
            )

        if not deployments.items:
            deployment_details = "No deployments found in this namespace."
        else:
            deployment_details = chr(10).join(deployment_lines)

        return {
            "status": "success",
            "formatted_response": f"""
🚀 **Deployments Report - {namespace}**

**Total Deployments: {len(deployments.items)}**

```
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
{deployment_details}
```
            """
        }
    except ApiException as e:
        return {"status": "error", "error_message": f"Kubernetes API error: {e.reason}"}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}