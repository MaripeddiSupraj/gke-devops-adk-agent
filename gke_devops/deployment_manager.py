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
                "replicas": dep.spec.replicas,
                "ready_replicas": dep.status.ready_replicas or 0,
                "status": "Ready" if dep.status.ready_replicas == dep.spec.replicas else "Not Ready"
            })
            
        if deployment_list:
            deploy_details = "\n".join([f"   • {dep['name']}: {dep['ready_replicas']}/{dep['replicas']} ready ({dep['status']})" for dep in deployment_list])
        else:
            deploy_details = "   • No deployments found"
            
        return {
            "status": "success",
            "formatted_response": f"""
🚀 **Deployments Report - {namespace} namespace**

📊 **Total Deployments**: {len(deployment_list)}

📋 **Deployment Status**:
{deploy_details}

✅ **Summary**: Found {len(deployment_list)} deployments in {namespace} namespace
            """
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}