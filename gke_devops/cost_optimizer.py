#!/usr/bin/env python3
"""
GKE DevOps Agent - Cost Optimization Analyzer

Provides actionable cost reduction recommendations for GKE clusters.
Focus: Resource right-sizing, idle detection, and cost-saving opportunities.

Author: GKE DevOps Team
"""

from .config import k8s_v1, k8s_apps_v1
from kubernetes import client
import re

def analyze_costs(namespace: str = "default") -> dict:
    """
    Analyze cluster costs and provide optimization recommendations.
    
    Performs comprehensive cost analysis including:
    - Resource over-provisioning detection
    - Idle resource identification
    - Node optimization opportunities
    - Spot instance savings calculations
    
    Args:
        namespace (str): Kubernetes namespace to analyze (default: "default")
        
    Returns:
        dict: Cost analysis with savings opportunities and optimization commands
    """
    try:
        # Fetch Kubernetes resources for cost analysis
        pods = k8s_v1.list_namespaced_pod(namespace)
        nodes = k8s_v1.list_node()
        deployments = k8s_apps_v1.list_namespaced_deployment(namespace)
        
        # Initialize cost analysis variables
        cost_issues = []                # List of cost-related issues
        savings_opportunities = []      # Potential cost savings
        total_potential_savings = 0     # Total estimated savings in USD
        
        # === GCP NODE PRICING REFERENCE ===
        # Approximate hourly costs for common GKE node types (as of 2024)
        node_costs = {
            'e2-medium': {'cpu': 1, 'memory': 4, 'hourly_cost': 0.067},
            'e2-standard-2': {'cpu': 2, 'memory': 8, 'hourly_cost': 0.134},
            'e2-standard-4': {'cpu': 4, 'memory': 16, 'hourly_cost': 0.268},
            'n1-standard-1': {'cpu': 1, 'memory': 3.75, 'hourly_cost': 0.095},
            'n1-standard-2': {'cpu': 2, 'memory': 7.5, 'hourly_cost': 0.190}
        }
        
        # === CURRENT COST CALCULATION ===
        # Estimate current cluster costs based on node count
        total_nodes = len(nodes.items)
        estimated_hourly_cost = total_nodes * 0.10  # Conservative estimate: $0.10/hour per node
        monthly_cost = estimated_hourly_cost * 24 * 30  # Convert to monthly cost
        
        # === 1. RESOURCE OVER-PROVISIONING ANALYSIS ===
        # Identify pods with excessive CPU/memory requests
        over_provisioned_pods = []
        under_utilized_resources = 0
        
        for pod in pods.items:
            if pod.spec.containers and pod.status.phase == "Running":
                for container in pod.spec.containers:
                    if container.resources and container.resources.requests:
                        cpu_req = container.resources.requests.get('cpu', '0')
                        mem_req = container.resources.requests.get('memory', '0')
                        
                        # Convert CPU to millicores
                        if 'm' in str(cpu_req):
                            cpu_millicores = int(str(cpu_req).replace('m', ''))
                        else:
                            cpu_millicores = int(float(str(cpu_req)) * 1000)
                        
                        # Check for over-provisioning (heuristic)
                        if cpu_millicores > 1000:  # More than 1 CPU
                            over_provisioned_pods.append({
                                "pod": pod.metadata.name,
                                "container": container.name,
                                "cpu_request": cpu_req,
                                "memory_request": mem_req,
                                "recommendation": "Consider reducing CPU request to 500m"
                            })
                            under_utilized_resources += 1
        
        # === 2. IDLE RESOURCE DETECTION ===
        # Find pods without resource requests (potential resource waste)
        idle_pods = []
        for pod in pods.items:
            if pod.status.phase == "Running":
                # Check for pods without resource requests (potential waste)
                has_requests = False
                if pod.spec.containers:
                    for container in pod.spec.containers:
                        if container.resources and container.resources.requests:
                            has_requests = True
                            break
                
                if not has_requests:
                    idle_pods.append({
                        "pod": pod.metadata.name,
                        "issue": "No resource requests defined",
                        "risk": "Unlimited resource consumption"
                    })
        
        # === 3. NODE OPTIMIZATION OPPORTUNITIES ===
        # Analyze node utilization and consolidation potential
        node_optimization = []
        running_pods = sum(1 for pod in pods.items if pod.status.phase == "Running")
        
        if total_nodes > 1 and running_pods < total_nodes * 5:  # Low pod density
            potential_savings = (total_nodes - 1) * 0.10 * 24 * 30  # Remove 1 node
            node_optimization.append({
                "issue": f"Low pod density: {running_pods} pods on {total_nodes} nodes",
                "recommendation": "Consider node consolidation",
                "potential_savings": f"${potential_savings:.2f}/month"
            })
            total_potential_savings += potential_savings
        
        # === 4. SPOT INSTANCE SAVINGS CALCULATION ===
        # Calculate potential savings with preemptible/spot instances
        spot_savings = monthly_cost * 0.7  # 70% savings with spot instances
        savings_opportunities.append({
            "type": "Spot Instances",
            "description": "Use preemptible nodes for non-critical workloads",
            "potential_savings": f"${spot_savings:.2f}/month (70% reduction)",
            "action": "gcloud container node-pools create spot-pool --preemptible"
        })
        
        # 5. STORAGE OPTIMIZATION
        storage_issues = []
        # Note: This would require additional APIs for persistent volumes
        storage_issues.append({
            "type": "Storage Class",
            "recommendation": "Use standard storage instead of SSD for non-performance critical workloads",
            "potential_savings": "30-50% storage costs"
        })
        
        # === COST OPTIMIZATION SCORING ===
        # Calculate overall optimization score based on identified issues
        total_issues = len(over_provisioned_pods) + len(idle_pods) + len(node_optimization)
        if total_issues == 0:
            optimization_score = 100
            status = "🟢 OPTIMIZED"
        elif total_issues <= 3:
            optimization_score = 80
            status = "🟡 GOOD"
        else:
            optimization_score = 50
            status = "🔴 NEEDS OPTIMIZATION"
        
        # Build recommendations
        recommendations = []
        
        # High-impact recommendations
        if over_provisioned_pods:
            recommendations.append("💰 **HIGH IMPACT**:")
            for pod in over_provisioned_pods[:3]:
                recommendations.append(f"   • {pod['pod']}: Over-provisioned CPU ({pod['cpu_request']})")
                recommendations.append(f"     └─ {pod['recommendation']}")
        
        if node_optimization:
            recommendations.append("🏗️ **INFRASTRUCTURE**:")
            for opt in node_optimization:
                recommendations.append(f"   • {opt['issue']}")
                recommendations.append(f"     └─ {opt['recommendation']} - Save {opt['potential_savings']}")
        
        # Quick wins
        if idle_pods:
            recommendations.append(f"⚡ **QUICK WINS**: {len(idle_pods)} pods without resource limits")
        
        if not recommendations:
            recommendations = ["✅ **Cluster is well-optimized!**"]
        
        # Removed verbose commands section
        
        # Build focused output
        key_actions = []
        if over_provisioned_pods:
            key_actions.append(f"Right-size {len(over_provisioned_pods)} over-provisioned pods")
        if idle_pods:
            key_actions.append(f"Add resource limits to {len(idle_pods)} pods")
        if node_optimization:
            key_actions.append("Consolidate nodes for better density")
        
        if not key_actions:
            key_actions = ["No immediate optimizations needed"]
        
        return {
            "status": "success",
            "formatted_response": f"""
💰 **Cost Analysis** - {namespace}

**${monthly_cost:.0f}/month** • **{optimization_score}/100** • **${total_potential_savings + spot_savings:.0f} savings available**

🎯 **Action Items**:
{chr(10).join([f"   • {action}" for action in key_actions])}

💡 **Top Savings**:
   • **Spot Instances**: ${spot_savings:.0f}/month (70% off)
   • **Autoscaling**: gcloud container clusters update --enable-autoscaling
            """
        }
        
    except Exception as e:
        return {"status": "error", "error_message": str(e)}