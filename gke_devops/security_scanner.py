#!/usr/bin/env python3
"""
GKE DevOps Agent - Production Security Scanner

Designed for daily K8s operations with actionable, concise output.
Focus: Quick identification and immediate remediation commands.

Author: GKE DevOps Team
"""

from .config import k8s_v1, k8s_apps_v1
from .models import SecurityFinding
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
                    findings["Critical"].append(SecurityFinding(
                        resource=f"{pod.metadata.name}/{container.name}",
                        issue="Privileged container",
                        severity="Critical",
                        recommendation=f"Remove privileged mode. Recreate pod `{pod.metadata.name}` without privileged access."
                    ))

            # CRITICAL: Host-level access
            if pod.spec.host_pid or pod.spec.host_ipc or pod.spec.host_network:
                findings["Critical"].append(SecurityFinding(
                    resource=pod.metadata.name,
                    issue="Host access enabled (PID/IPC/Network)",
                    severity="Critical",
                    recommendation=f"Disable host PID, IPC, and Network access for pod `{pod.metadata.name}`."
                ))

            # HIGH: Running as root
            if pod.spec.security_context and pod.spec.security_context.run_as_user == 0:
                findings["High"].append(SecurityFinding(
                    resource=pod.metadata.name,
                    issue="Runs as root",
                    severity="High",
                    recommendation=f"Configure pod `{pod.metadata.name}` to run as a non-root user (e.g., `runAsUser: 1000`)."
                ))

            # HIGH: Dangerous capabilities
            for container in pod.spec.containers:
                if container.security_context and container.security_context.capabilities:
                    if any(cap in ["ALL", "SYS_ADMIN", "NET_ADMIN"] for cap in container.security_context.capabilities.add or []):
                        findings["High"].append(SecurityFinding(
                            resource=f"{pod.metadata.name}/{container.name}",
                            issue="Dangerous capability",
                            severity="High",
                            recommendation=f"Remove dangerous capabilities (e.g., `SYS_ADMIN`, `NET_ADMIN`) from container `{container.name}` in pod `{pod.metadata.name}`."
                        ))

            # MEDIUM: No resource limits
            for container in pod.spec.containers:
                if not container.resources or not container.resources.limits:
                    findings["Medium"].append(SecurityFinding(
                        resource=f"{pod.metadata.name}/{container.name}",
                        issue="No resource limits",
                        severity="Medium",
                        recommendation=f"Add resource limits (CPU/Memory) to container `{container.name}` in pod `{pod.metadata.name}`."
                    ))

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
            for f in findings["Critical"]:
                report_body.append(f"- 🚨 {f.issue} (Resource: `{f.resource}`)")
                report_body.append(f"  **Recommendation:** {f.recommendation}")
        if findings["High"]:
            report_body.append("\n**High Issues:**")
            for f in findings["High"]:
                report_body.append(f"- ⚠️ {f.issue} (Resource: `{f.resource}`)")
                report_body.append(f"  **Recommendation:** {f.recommendation}")
        if findings["Medium"]:
            report_body.append("\n**Medium Issues:**")
            for f in findings["Medium"]:
                report_body.append(f"- 🔧 {f.issue} (Resource: `{f.resource}`)")
                report_body.append(f"  **Recommendation:** {f.recommendation}")

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
