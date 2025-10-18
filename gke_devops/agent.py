#!/usr/bin/env python3
"""GKE DevOps agent for ADK web interface."""

from google.adk.agents.llm_agent import Agent
from kubernetes import client, config

# Load Kubernetes config
try:
    config.load_incluster_config()
except:
    config.load_kube_config()

k8s_v1 = client.CoreV1Api()
k8s_apps_v1 = client.AppsV1Api()

def check_cluster_health() -> dict:
    """Check overall GKE cluster health status."""
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

def get_pod_status(namespace: str = "default") -> dict:
    """Get detailed pod status in specified namespace."""
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
            import datetime
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

def list_deployments(namespace: str = "default") -> dict:
    """List all deployments in the specified namespace."""
    try:
        deployments = k8s_apps_v1.list_namespaced_deployment(namespace)
        deployment_list = []
        
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

def diagnose_issues(namespace: str = "default") -> dict:
    """Diagnose common cluster issues and failed pods."""
    try:
        pods = k8s_v1.list_namespaced_pod(namespace)
        issues = []
        
        for pod in pods.items:
            if pod.status.phase in ["Failed", "Pending"]:
                issues.append({
                    "pod_name": pod.metadata.name,
                    "phase": pod.status.phase,
                    "reason": pod.status.reason or "Unknown"
                })
        
        if issues:
            issue_details = "\n".join([f"   • {issue['pod_name']}: {issue['phase']} - {issue['reason']}" for issue in issues])
            status_icon = "🔴"
            recommendation = "🔍 **Recommendation**: Check pod logs and events for detailed troubleshooting"
        else:
            issue_details = "   • No issues detected - all pods are healthy! 🎉"
            status_icon = "✅"
            recommendation = "🎉 **Great news**: Your cluster is running smoothly!"
            
        return {
            "status": "success",
            "formatted_response": f"""
🔍 **Cluster Diagnostics Report - {namespace} namespace**

{status_icon} **Issues Found**: {len(issues)}

📊 **Issue Details**:
{issue_details}

{recommendation}
            """
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

# Create the GKE DevOps agent
root_agent = Agent(
    model="gemini-2.0-flash",
    name="gke_devops_agent",
    description="GKE DevOps agent for cluster monitoring and management via web chat interface",
    instruction=(
        "You are a GKE DevOps assistant that can monitor and manage Kubernetes clusters. "
        "When users ask about cluster health, pod status, deployments, or issues, use the appropriate tools to get real-time information. "
        "IMPORTANT: Always return the complete formatted_response from the tools exactly as provided. "
        "Never summarize or paraphrase the formatted dashboard output. Show the full dashboard with emojis, dividers, and detailed metrics."
    ),
    tools=[check_cluster_health, get_pod_status, list_deployments, diagnose_issues]
)