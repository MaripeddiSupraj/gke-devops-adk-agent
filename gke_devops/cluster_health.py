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
    
    Returns:
        dict: Formatted cluster health dashboard with infrastructure and workload status
    """
    try:
        nodes = k8s_v1.list_node()
        ready_nodes = sum(1 for node in nodes.items 
                         if any(c.type == "Ready" and c.status == "True" 
                               for c in node.status.conditions))
        
        pods = k8s_v1.list_pod_for_all_namespaces()
        running_pods = sum(1 for pod in pods.items if pod.status.phase == "Running")
        failed_pods = sum(1 for pod in pods.items if pod.status.phase == "Failed")
        pending_pods = sum(1 for pod in pods.items if pod.status.phase == "Pending")
        pod_efficiency = (running_pods / len(pods.items) * 100) if len(pods.items) > 0 else 100
        
        # Get node details
        node_details = []
        for node in nodes.items:
            node_ready = any(c.type == "Ready" and c.status == "True" for c in node.status.conditions)
            node_details.append({
                "name": node.metadata.name,
                "ready": "✅" if node_ready else "❌",
                "version": node.status.node_info.kubelet_version
            })
        
        # Enhanced status
        if failed_pods == 0 and pending_pods == 0:
            detailed_status = "🟢 **EXCELLENT** - All systems operational"
        elif failed_pods == 0 and pending_pods > 0:
            detailed_status = f"🟡 **GOOD** - {pending_pods} pods pending startup"
        else:
            detailed_status = f"🔴 **ATTENTION** - {failed_pods} failed, {pending_pods} pending"
        
        node_list = "\n".join([f"      • {node['name']}: {node['ready']} {node['version']}" for node in node_details])
        
        return {
            "status": "success",
            "formatted_response": f"""
🏥 **GKE Cluster Health Dashboard**

{detailed_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖥️ **Infrastructure Status**
   📍 **Nodes**: {ready_nodes}/{len(nodes.items)} ready ({(ready_nodes/len(nodes.items)*100):.0f}%)
   🔧 **Node Details**:
{node_list}

🚀 **Workload Status**
   📊 **Pod Health**: {pod_efficiency:.0f}% operational
   ✅ **Running**: {running_pods} pods
   ⏳ **Pending**: {pending_pods} pods
   ❌ **Failed**: {failed_pods} pods
   📈 **Total Workloads**: {len(pods.items)} pods

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **Quick Insights**:
   • Cluster Utilization: {len(pods.items)} pods across {len(nodes.items)} node(s)
   • Average Pod Density: {(len(pods.items)/len(nodes.items)):.1f} pods per node
   • System Reliability: {pod_efficiency:.0f}% uptime
   • Infrastructure: {'Single-node setup' if len(nodes.items) == 1 else f'{len(nodes.items)}-node cluster'}

🎯 **Status**: {"🎉 Your cluster is performing optimally!" if failed_pods == 0 and pending_pods == 0 else "⚠️ Monitor pending/failed pods for optimal performance"}
            """
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}