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
from .models import Deployment
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
        deployments_api = k8s_apps_v1.list_namespaced_deployment(namespace)
        deployments = []
        for d in deployments_api.items:
            age = "Unknown"
            if d.metadata.creation_timestamp:
                delta = datetime.datetime.now(datetime.timezone.utc) - d.metadata.creation_timestamp
                if delta.days > 0:
                    age = f"{delta.days}d"
                else:
                    age = f"{delta.seconds // 3600}h"

            deployments.append(Deployment(
                name=d.metadata.name,
                ready=f"{d.status.ready_replicas or 0}/{d.spec.replicas}",
                up_to_date=f"{d.status.updated_replicas or 0}",
                available=f"{d.status.available_replicas or 0}",
                age=age,
            ))

        deployment_lines = []
        for dep in deployments:
            deployment_lines.append(
                f"{dep.name:<25} {dep.ready:<5} {dep.up_to_date:<12} {dep.available:<11} {dep.age}"
            )

        if not deployments:
            deployment_details = "No deployments found in this namespace."
        else:
            deployment_details = chr(10).join(deployment_lines)

        return {
            "status": "success",
            "formatted_response": f"""
🚀 **Deployments Report - {namespace}**

**Total Deployments: {len(deployments)}**

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