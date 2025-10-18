import datetime
from .config import k8s_v1
from kubernetes.client.exceptions import ApiException

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
        pods = k8s_v1.list_namespaced_pod(namespace)
        pod_details = []
        pod_stats = {"Running": 0, "Pending": 0, "Failed": 0, "Succeeded": 0, "Unknown": 0}

        for pod in pods.items:
            pod_stats[pod.status.phase] = pod_stats.get(pod.status.phase, 0) + 1

            ready_containers = 0
            total_containers = len(pod.spec.containers)
            restarts = 0
            if pod.status.container_statuses:
                ready_containers = sum(1 for c in pod.status.container_statuses if c.ready)
                restarts = sum(c.restart_count for c in pod.status.container_statuses)

            age = "Unknown"
            if pod.metadata.creation_timestamp:
                delta = datetime.datetime.now(datetime.timezone.utc) - pod.metadata.creation_timestamp
                if delta.days > 0:
                    age = f"{delta.days}d"
                else:
                    age = f"{delta.seconds // 3600}h"

            pod_details.append(
                f"{pod.status.phase:<10} {pod.metadata.name:<40} {ready_containers}/{total_containers} {restarts:<3} {age:<5} {pod.spec.node_name}"
            )

        total_pods = len(pods.items)
        running_pods = pod_stats.get("Running", 0)
        health_percentage = (running_pods / total_pods * 100) if total_pods > 0 else 100

        if health_percentage == 100:
            overall_status = "🟢 EXCELLENT: All pods are running normally."
        elif running_pods > 0:
            overall_status = f"🟡 ATTENTION: {total_pods - running_pods} pod(s) have issues."
        else:
            overall_status = f"🔴 CRITICAL: No pods are running in the namespace."

        pod_table = ["STATUS     NAME                                     READY RESTARTS AGE   NODE"]
        pod_table.extend(pod_details[:10])
        pod_summary = f"... and {len(pod_details) - 10} more pods" if len(pod_details) > 10 else ""

        return {
            "status": "success",
            "formatted_response": f"""
📦 **Pod Status Report - {namespace}**

**{overall_status}**

**Summary:**
- **Health:** {health_percentage:.0f}%
- **Total:** {total_pods}
- **Running:** {running_pods}
- **Pending:** {pod_stats.get('Pending', 0)}
- **Failed:** {pod_stats.get('Failed', 0)}

**Pod Details:**
```
{chr(10).join(pod_table)}
```
{pod_summary}
            """
        }
    except ApiException as e:
        return {"status": "error", "error_message": f"Kubernetes API error: {e.reason}"}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}