#!/usr/bin/env python3
"""
GKE DevOps Agent - Pod Status Monitor

This module provides detailed pod monitoring capabilities with:
- Container readiness and restart count tracking
- Pod age calculation and node assignment details
- Health percentage scoring and status categorization
- Professional dashboard with detailed pod information

Author: GKE DevOps Team
"""

import datetime
from .config import k8s_v1

def get_pod_status(namespace: str = "default") -> dict:
    """
    Get detailed pod status in specified namespace with comprehensive metrics.
    
    Args:
        namespace (str): Kubernetes namespace to monitor (default: "default")
        
    Returns:
        dict: Formatted pod status dashboard with health summary and detailed pod info
    """
    try:
        pods = k8s_v1.list_namespaced_pod(namespace)
        pod_stats = {}
        pod_details = []
        
        for pod in pods.items:
            phase = pod.status.phase
            pod_stats[phase] = pod_stats.get(phase, 0) + 1
            
            # Get detailed pod info
            ready_containers = 0
            total_containers = len(pod.spec.containers) if pod.spec.containers else 0
            restart_count = 0
            
            if pod.status.container_statuses:
                ready_containers = sum(1 for c in pod.status.container_statuses if c.ready)
                restart_count = sum(c.restart_count for c in pod.status.container_statuses)
            
            # Get pod age
            if pod.metadata.creation_timestamp:
                age = datetime.datetime.now(datetime.timezone.utc) - pod.metadata.creation_timestamp
                age_str = f"{age.days}d" if age.days > 0 else f"{age.seconds//3600}h{(age.seconds%3600)//60}m"
            else:
                age_str = "Unknown"
            
            # Status icon
            status_icon = {
                "Running": "🟢",
                "Pending": "🟡", 
                "Failed": "🔴",
                "Succeeded": "✅",
                "Unknown": "⚪"
            }.get(phase, "❓")
            
            pod_details.append({
                "name": pod.metadata.name,
                "phase": phase,
                "icon": status_icon,
                "ready": f"{ready_containers}/{total_containers}",
                "restarts": restart_count,
                "age": age_str,
                "node": pod.spec.node_name or "Not Assigned"
            })
        
        # Enhanced pod list
        pod_list = "\n".join([
            f"   {pod['icon']} **{pod['name']}**\n      └─ Status: {pod['phase']} | Ready: {pod['ready']} | Restarts: {pod['restarts']} | Age: {pod['age']} | Node: {pod['node']}"
            for pod in pod_details[:10]
        ])
        
        if len(pod_details) > 10:
            pod_list += f"\n   📋 ... and {len(pod_details) - 10} more pods"
        
        # Calculate health percentage
        running_pods = pod_stats.get('Running', 0)
        health_percentage = (running_pods / len(pod_details) * 100) if len(pod_details) > 0 else 100
        
        # Overall status
        if health_percentage == 100:
            overall_status = "🟢 **EXCELLENT** - All pods healthy"
        elif health_percentage >= 80:
            overall_status = "🟡 **GOOD** - Most pods healthy"
        else:
            overall_status = "🔴 **ATTENTION** - Multiple pod issues"
        
        # Status summary
        status_summary = []
        for phase, count in pod_stats.items():
            icon = {"Running": "🟢", "Pending": "🟡", "Failed": "🔴", "Succeeded": "✅"}.get(phase, "❓")
            status_summary.append(f"   {icon} **{phase}**: {count} pods")
        
        return {
            "status": "success",
            "formatted_response": f"""
📦 **Pod Status Dashboard - {namespace} namespace**

{overall_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Pod Health Summary**:
   📈 **Health Score**: {health_percentage:.0f}%
   🔢 **Total Pods**: {len(pod_details)}
{chr(10).join(status_summary)}

🚀 **Detailed Pod Status** (showing first 10):
{pod_list}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **Quick Insights**:
   • Pod Density: {len(pod_details)} workloads in {namespace}
   • Restart Activity: {sum(pod['restarts'] for pod in pod_details)} total restarts
   • Health Status: {health_percentage:.0f}% operational

🎯 **Recommendation**: {"🎉 All pods are running smoothly!" if health_percentage == 100 else "⚠️ Monitor non-running pods for issues"}
            """
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}