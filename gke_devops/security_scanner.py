#!/usr/bin/env python3
"""
GKE DevOps Agent - Production Security Scanner

Designed for daily K8s operations with actionable, concise output.
Focus: Quick identification and immediate remediation commands.

Author: GKE DevOps Team
"""

from .config import k8s_v1, k8s_apps_v1
import base64

def security_scan(namespace: str = "default") -> dict:
    """
    Production-grade security scan optimized for daily K8s operations.
    
    Performs comprehensive security analysis based on:
    - CIS Kubernetes Benchmark
    - NSA/CISA Kubernetes Hardening Guide
    - Pod Security Standards (PSS)
    
    Args:
        namespace (str): Kubernetes namespace to scan (default: "default")
        
    Returns:
        dict: Security analysis with actionable findings and remediation commands
    """
    try:
        # Fetch all Kubernetes resources for security analysis
        pods = k8s_v1.list_namespaced_pod(namespace)
        secrets = k8s_v1.list_namespaced_secret(namespace)
        services = k8s_v1.list_namespaced_service(namespace)
        deployments = k8s_apps_v1.list_namespaced_deployment(namespace)
        
        # Initialize security findings by severity level
        critical_findings = []  # Immediate security threats
        high_findings = []      # High-priority security issues
        medium_findings = []    # Medium-priority improvements
        
        # === CRITICAL SECURITY CHECKS ===
        # Check for privileged containers and dangerous Linux capabilities
        for pod in pods.items:
            if pod.spec.containers:
                for container in pod.spec.containers:
                    if (container.security_context and container.security_context.privileged):
                        critical_findings.append({
                            "resource": pod.metadata.name,
                            "issue": "Privileged container",
                            "fix": f"kubectl delete pod {pod.metadata.name} # Recreate without privileged access"
                        })
                    
                    if (container.security_context and container.security_context.capabilities and 
                        container.security_context.capabilities.add):
                        dangerous = ['SYS_ADMIN', 'NET_ADMIN', 'SYS_TIME', 'SYS_MODULE']
                        for cap in container.security_context.capabilities.add:
                            if cap in dangerous:
                                critical_findings.append({
                                    "resource": f"{pod.metadata.name}/{container.name}",
                                    "issue": f"Dangerous capability: {cap}",
                                    "fix": f"Remove {cap} from capabilities.add in pod spec"
                                })
        
        # === HIGH PRIORITY SECURITY CHECKS ===
        # Check for root user execution and insecure service account usage
        for pod in pods.items:
            # Root user check
            if (pod.spec.security_context and 
                (pod.spec.security_context.run_as_user == 0 or not pod.spec.security_context.run_as_user)):
                high_findings.append({
                    "resource": pod.metadata.name,
                    "issue": "Running as root",
                    "fix": f"kubectl delete pod {pod.metadata.name} # Recreate with runAsUser: 1000"
                })
            
            # Default service account
            sa_name = pod.spec.service_account_name or "default"
            if sa_name == "default":
                high_findings.append({
                    "resource": pod.metadata.name,
                    "issue": "Using default ServiceAccount",
                    "fix": f"kubectl create sa {pod.metadata.name}-sa -n {namespace}"
                })
        
        # HIGH: Open LoadBalancers
        for service in services.items:
            if (service.spec.type == "LoadBalancer" and 
                not service.spec.load_balancer_source_ranges):
                high_findings.append({
                    "resource": f"svc/{service.metadata.name}",
                    "issue": "LoadBalancer without IP restrictions",
                    "fix": f"kubectl edit svc {service.metadata.name} # Add loadBalancerSourceRanges"
                })
        
        # === MEDIUM PRIORITY SECURITY CHECKS ===
        # Check for missing security contexts and resource constraints
        for pod in pods.items:
            if pod.spec.containers:
                for container in pod.spec.containers:
                    # Missing security context
                    if (not container.security_context or 
                        not container.security_context.read_only_root_filesystem):
                        medium_findings.append({
                            "resource": f"{pod.metadata.name}/{container.name}",
                            "issue": "Writable root filesystem",
                            "fix": "Add readOnlyRootFilesystem: true to container securityContext"
                        })
                    
                    # Missing resource limits
                    if not container.resources or not container.resources.limits:
                        medium_findings.append({
                            "resource": f"{pod.metadata.name}/{container.name}",
                            "issue": "No resource limits",
                            "fix": "Add resources.limits.memory/cpu to container spec"
                        })
        
        # === SECURITY SCORING ALGORITHM ===
        # Calculate overall security score based on weighted issue severity
        total_issues = len(critical_findings) + len(high_findings) + len(medium_findings)
        penalty = len(critical_findings) * 30 + len(high_findings) * 20 + len(medium_findings) * 10
        security_score = max(0, 100 - penalty)  # Score: 0-100
        
        # Determine security status based on score thresholds
        if security_score >= 85:
            status = "🟢 SECURE"
        elif security_score >= 70:
            status = "🟡 REVIEW"
        else:
            status = "🔴 ACTION REQUIRED"
        
        # Build actionable output
        action_items = []
        
        # Critical actions (immediate)
        if critical_findings:
            action_items.append("🚨 **IMMEDIATE ACTION**:")
            for finding in critical_findings[:3]:
                action_items.append(f"   • {finding['resource']}: {finding['issue']}")
                action_items.append(f"     └─ {finding['fix']}")
        
        # High priority actions
        if high_findings:
            action_items.append("⚠️ **HIGH PRIORITY**:")
            for finding in high_findings[:3]:
                action_items.append(f"   • {finding['resource']}: {finding['issue']}")
                action_items.append(f"     └─ {finding['fix']}")
        
        # Medium priority summary
        if medium_findings:
            action_items.append(f"🔧 **MEDIUM PRIORITY**: {len(medium_findings)} items (security context, resource limits)")
        
        if not action_items:
            action_items = ["✅ **All security checks passed!**"]
        
        # Removed verbose quick fixes section
        
        # === OUTPUT FORMATTING ===
        # Build concise, actionable security summary for K8s experts
        top_issues = []
        if critical_findings:
            top_issues.extend([f"CRITICAL: {f['issue']}" for f in critical_findings[:2]])
        if high_findings:
            top_issues.extend([f"HIGH: {f['issue']}" for f in high_findings[:2]])
        if medium_findings and not critical_findings and not high_findings:
            top_issues.append(f"MEDIUM: {len(medium_findings)} security improvements needed")
        
        if not top_issues:
            top_issues = ["All security checks passed"]
        
        return {
            "status": "success",
            "formatted_response": f"""
🔒 **Security Scan** - {namespace}

**{security_score}/100** • **{total_issues} Issues** • **CIS + NSA Standards**

🎯 **Top Issues**:
{chr(10).join([f"   • {issue}" for issue in top_issues])}

🔧 **Quick Fixes**:
   • **Pod Security**: kubectl label namespace {namespace} pod-security.kubernetes.io/enforce=restricted
   • **Service Accounts**: kubectl create sa secure-sa
            """
        }
        
    except Exception as e:
        return {"status": "error", "error_message": str(e)}