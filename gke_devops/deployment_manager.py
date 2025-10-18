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
        # === DEPLOYMENT DATA COLLECTION ===
        # Fetch all deployments in the specified namespace
        deployments = k8s_apps_v1.list_namespaced_deployment(namespace)
        deployment_list = []  # List to store deployment information
        
        # === DEPLOYMENT ANALYSIS ===
        # Process each deployment to extract replica status and health information
        for dep in deployments.items:
            deployment_list.append({
                "name": dep.metadata.name,
                "ready": f"{dep.status.ready_replicas or 0}/{dep.spec.replicas}",
                "status": "✅ Ready" if dep.status.ready_replicas == dep.spec.replicas else "🔄 Updating"
            })
            
        # Create a formatted table
        headers = ["STATUS", "DEPLOYMENT", "REPLICAS"]
        deploy_table = [headers]
        for d in deployment_list:
            deploy_table.append([d['status'], d['name'], d['ready']])

        # Simple column alignment
        deploy_details = "\n".join(["  ".join(f"{item:<{max(len(str(row[i])) for row in deploy_table) + 2}}" for i, item in enumerate(row))) for row in deploy_table])

        if not deployment_list:
            deploy_details = "No deployments found in this namespace."
            
        return {
            "status": "success",
            "formatted_response": f"""
🚀 **Deployments Report - {namespace} namespace**
Total Deployments: {len(deployment_list)}
```
{deploy_details}
```
            """
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}