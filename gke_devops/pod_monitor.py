import datetime
from .config import k8s_v1
from .models import Pod
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
        pods_api = k8s_v1.list_namespaced_pod(namespace)
        pods = []
        for p in pods_api.items:
            ready_containers = 0
            total_containers = len(p.spec.containers)
            restarts = 0
            if p.status.container_statuses:
                ready_containers = sum(1 for c in p.status.container_statuses if c.ready)
                restarts = sum(c.restart_count for c in p.status.container_statuses)

            age = "Unknown"
            if p.metadata.creation_timestamp:
                delta = datetime.datetime.now(datetime.timezone.utc) - p.metadata.creation_timestamp
                if delta.days > 0:
                    age = f"{delta.days}d"
                else:
                    age = f"{delta.seconds // 3600}h"

            pods.append(Pod(
                name=p.metadata.name,
                status=p.status.phase,
                ready=f"{ready_containers}/{total_containers}",
                restarts=restarts,
                age=age,
                node=p.spec.node_name or "N/A",
            ))

        pod_cards = []
        for pod in pods:
            status_emoji = {"Running": "🟢", "Pending": "🟡", "Failed": "🔴", "Succeeded": "✅"}.get(pod.status, "⚪️")
            pod_cards.append(
                f"""│ {status_emoji} {pod.name:<66} │
│    Status:   {pod.status:<56} │
│    Ready:    {pod.ready:<56} │
│    Restarts: {pod.restarts:<56} │
│    Age:      {pod.age:<56} │
│    Node:     {pod.node:<56} │"""
            )

        total_pods = len(pods)
        running_pods = sum(1 for p in pods if p.status == "Running")
        health_percentage = (running_pods / total_pods * 100) if total_pods > 0 else 100

        if health_percentage == 100:
            overall_status = "🟢 All pods are running normally."
        elif running_pods > 0:
            overall_status = f"🟡 {total_pods - running_pods} pod(s) have issues."
        else:
            overall_status = f"🔴 No pods are running in the namespace."

        return {
            "status": "success",
            "formatted_response": f"""
┌─────────────────────────────────────────────────────────────────┐
│ 📦 Pod Status: {namespace:<52} │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
{chr(10).join(pod_cards)}
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Summary                                                         │
│   Total Pods: {total_pods:<51} │
│   Health:     {health_percentage:<51.0f}% │
└─────────────────────────────────────────────────────────────────┘
            """
        }
    except ApiException as e:
        return {"status": "error", "error_message": f"Kubernetes API error: {e.reason}"}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}