#!/usr/bin/env python3
"""
GKE DevOps Agent - Cluster Health Monitor

This module provides comprehensive cluster health monitoring with:
- Node status and readiness checks
- Pod health metrics and efficiency calculations  
- Professional dashboard formatting with emojis and dividers
- Real-time infrastructure and workload status reporting

Author: GKE DevOps Team
"""

from .config import k8s_v1

def check_cluster_health() -> dict:
    """
    Check overall GKE cluster health status with detailed metrics.
    
    Provides comprehensive cluster health assessment including:
    - Node readiness and version information
    - Pod health metrics and distribution
    - System reliability calculations
    - Infrastructure utilization analysis
    
    Returns:
        dict: Formatted cluster health dashboard with infrastructure and workload status
    """
    try:
        # === NODE HEALTH ASSESSMENT ===
        # Fetch all cluster nodes and evaluate their readiness status
        nodes = k8s_v1.list_node()
        ready_nodes = sum(1 for node in nodes.items 
                         if any(c.type == "Ready" and c.status == "True" 
                               for c in node.status.conditions))
        
        # === POD HEALTH METRICS ===
        # Analyze pod status across all namespaces for cluster-wide health
        pods = k8s_v1.list_pod_for_all_namespaces()
        running_pods = sum(1 for pod in pods.items if pod.status.phase == "Running")
        failed_pods = sum(1 for pod in pods.items if pod.status.phase == "Failed")
        pending_pods = sum(1 for pod in pods.items if pod.status.phase == "Pending")
        pod_efficiency = (running_pods / len(pods.items) * 100) if len(pods.items) > 0 else 100
        
        # === NODE DETAILED INFORMATION ===
        # Extract detailed node information including readiness and Kubernetes version
        node_details = []
        for node in nodes.items:
            node_ready = any(c.type == "Ready" and c.status == "True" for c in node.status.conditions)
            node_details.append({
                "name": node.metadata.name,
                "ready": "✅" if node_ready else "❌",
                "version": node.status.node_info.kubelet_version
            })
        
        # === CLUSTER STATUS DETERMINATION ===
        # Determine overall cluster health status based on pod conditions
        if failed_pods == 0 and pending_pods == 0:
            detailed_status = "🟢 **EXCELLENT** - All systems operational"
        elif failed_pods == 0 and pending_pods > 0:
            detailed_status = f"🟡 **GOOD** - {pending_pods} pods pending startup"
        else:
            detailed_status = f"🔴 **ATTENTION** - {failed_pods} failed, {pending_pods} pending"
        
        return {
            "status": "success",
            "formatted_response": f"""
🏥 **GKE Cluster Health Dashboard**
{detailed_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
┌──────────────────────────────┬──────────────────────────────┐
│ 🖥️ INFRASTRUCTURE            │ 🚀 WORKLOADS                 │
├──────────────────────────────┼──────────────────────────────┤
│ Nodes     : {ready_nodes} / {len(nodes.items)} Ready      │ Pods      : {running_pods} / {len(pods.items)} Running   │
│ Uptime    : {pod_efficiency:.0f}%                  │ Running   : {running_pods}                   │
│ Density   : {(len(pods.items)/len(nodes.items)):.1f} pods/node     │ Pending   : {pending_pods}                   │
│                               │ Failed    : {failed_pods}                   │
└──────────────────────────────┴──────────────────────────────┘
```
Node Details:
```
{"\n".join([f"  • {node['name']} ({node['version']}) - {node['ready']}" for node in node_details])}
```
            """
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}