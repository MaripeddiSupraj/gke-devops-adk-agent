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
    
    Provides detailed pod monitoring including:
    - Container readiness and restart count tracking
    - Pod age calculation and node assignment details
    - Health percentage scoring and status categorization
    - Professional dashboard with detailed pod information
    
    Args:
        namespace (str): Kubernetes namespace to monitor (default: "default")
        
    Returns:
        dict: Formatted pod status dashboard with health summary and detailed pod info
    """
    try:
        # === POD DATA COLLECTION ===
        # Fetch all pods in the specified namespace
        pods = k8s_v1.list_namespaced_pod(namespace)
        pod_stats = {}      # Pod status statistics by phase
        pod_details = []    # Detailed information for each pod
        
        # === POD ANALYSIS LOOP ===
        # Process each pod to extract detailed metrics and status information
        for pod in pods.items:
            phase = pod.status.phase
            pod_stats[phase] = pod_stats.get(phase, 0) + 1
            
            # === CONTAINER METRICS EXTRACTION ===
            # Calculate container readiness and restart statistics
            ready_containers = 0
            total_containers = len(pod.spec.containers) if pod.spec.containers else 0
            restart_count = 0
            
            if pod.status.container_statuses:
                ready_containers = sum(1 for c in pod.status.container_statuses if c.ready)
                restart_count = sum(c.restart_count for c in pod.status.container_statuses)
            
            # === POD AGE CALCULATION ===
            # Calculate how long the pod has been running
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
        # Create a formatted table for pod details
        headers = ["STATUS", "NAME", "READY", "RESTARTS", "AGE", "NODE"]
        pod_table = [headers]
        for p in pod_details[:10]:
            pod_table.append([p['icon'], p['name'], p['ready'], str(p['restarts']), p['age'], p['node']])
        
        # Simple column alignment
        pod_list = "\n".join(["  ".join(f"{item:<{max(len(str(row[i])) for row in pod_table) + 2}}" for i, item in enumerate(row))) for row in pod_table])

        # === HEALTH SCORING CALCULATION ===
        # Calculate overall pod health percentage based on running pods
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

`Health: {health_percentage:.0f}%` | `Total: {len(pod_details)}` | `Running: {pod_stats.get('Running', 0)}` | `Pending: {pod_stats.get('Pending', 0)}` | `Failed: {pod_stats.get('Failed', 0)}`

```
{pod_list}
```
{"... and " + str(len(pod_details) - 10) + " more pods" if len(pod_details) > 10 else ""}
            """
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}