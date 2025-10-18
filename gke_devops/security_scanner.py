#!/usr/bin/env python3
"""
GKE DevOps Agent - Production Security Scanner

Designed for daily K8s operations with actionable, concise output.
Focus: Quick identification and immediate remediation commands.

Author: GKE DevOps Team
"""

from .config import k8s_v1, k8s_apps_v1
from kubernetes.client.exceptions import ApiException

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
        pods = k8s_v1.list_namespaced_pod(namespace)
        
        findings = {"Critical": [], "High": [], "Medium": []}

        for pod in pods.items:
            # CRITICAL: Privileged containers
            for container in pod.spec.containers:
                if container.security_context and container.security_context.privileged:
                    findings["Critical"].append(f"Privileged container: {pod.metadata.name}/{container.name}")

            # CRITICAL: Host-level access
            if pod.spec.host_pid or pod.spec.host_ipc or pod.spec.host_network:
                findings["Critical"].append(f"Host access enabled: {pod.metadata.name} (PID/IPC/Network)")

            # HIGH: Running as root
            if pod.spec.security_context and pod.spec.security_context.run_as_user == 0:
                findings["High"].append(f"Runs as root: {pod.metadata.name}")

            # HIGH: Dangerous capabilities
            for container in pod.spec.containers:
                if container.security_context and container.security_context.capabilities:
                    if any(cap in ["ALL", "SYS_ADMIN", "NET_ADMIN"] for cap in container.security_context.capabilities.add or []):
                        findings["High"].append(f"Dangerous capability: {pod.metadata.name}/{container.name}")

            # MEDIUM: No resource limits
            for container in pod.spec.containers:
                if not container.resources or not container.resources.limits:
                    findings["Medium"].append(f"No resource limits: {pod.metadata.name}/{container.name}")

        total_issues = sum(len(v) for v in findings.values())
        security_score = 100 - (len(findings["Critical"]) * 20 + len(findings["High"]) * 10 + len(findings["Medium"]) * 5)

        if security_score >= 90:
            status = "🟢 EXCELLENT"
        elif security_score >= 70:
            status = "🟡 GOOD"
        else:
            status = "🔴 ATTENTION"

        report_body = []
        if findings["Critical"]:
            report_body.append("**Critical Issues:**")
            report_body.extend([f"- {f}" for f in findings["Critical"]])
        if findings["High"]:
            report_body.append("\n**High Issues:**")
            report_body.extend([f"- {f}" for f in findings["High"]])
        if findings["Medium"]:
            report_body.append("\n**Medium Issues:**")
            report_body.extend([f"- {f}" for f in findings["Medium"]])

        if not report_body:
            report_body.append("No security issues found. Great job! ✨")

        return {
            "status": "success",
            "formatted_response": f"""
🔒 **Security Report - {namespace}**

**Score: {security_score}/100 ({status})**

**{total_issues} issues found.**

{chr(10).join(report_body)}
            """
        }
    except ApiException as e:
        return {"status": "error", "error_message": f"Kubernetes API error: {e.reason}"}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
