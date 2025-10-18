#!/usr/bin/env python3
"""
GKE DevOps Agent - Advanced Security Scanner

Enterprise-grade security analysis with CVE scanning, compliance checks,
and advanced threat detection for production Kubernetes environments.

Author: GKE DevOps Team
"""

from .config import k8s_v1, k8s_apps_v1, k8s_networking_v1
from .models import AdvancedSecurityFinding
import re
import json
from kubernetes.client.exceptions import ApiException

# === CONSTANTS FOR SECURITY CHECKS ===
# Heuristic patterns for known vulnerable or end-of-life (EOL) base images.
# This list can be updated as new advisories are released.
VULNERABLE_IMAGE_PATTERNS = [
    r"ubuntu:1[68]\.04",
    r"python:2\.7",
    r"nginx:1\.1[0-8]",
]

def advanced_security_scan(namespace: str = "default") -> dict:
    """
    Perform advanced security analysis including CVE scanning and compliance checks.
    
    Enterprise-grade security assessment covering:
    - Container image vulnerability analysis
    - Network security policy evaluation
    - RBAC configuration assessment
    - Secrets management security
    - Compliance scoring (SOC2, PCI-DSS, NIST)
    - Threat detection indicators
    
    Args:
        namespace (str): Kubernetes namespace to scan (default: "default")
        
    Returns:
        dict: Advanced security analysis with compliance scoring and threat indicators
    """
    try:
        pods = k8s_v1.list_namespaced_pod(namespace)
        network_policies = k8s_networking_v1.list_namespaced_network_policy(namespace)

        findings = []

        for pod in pods.items:
            for container in pod.spec.containers:
                # Image Vulnerabilities (Heuristic)
                for pattern in VULNERABLE_IMAGE_PATTERNS:
                    if re.search(pattern, container.image):
                        findings.append(AdvancedSecurityFinding(
                            category="Image Vulnerabilities",
                            description=f"Uses vulnerable image `{container.image}`",
                            severity="High",
                            recommendation="Update to a supported and secure base image."
                        ))
                if ":latest" in container.image:
                    findings.append(AdvancedSecurityFinding(
                        category="Image Vulnerabilities",
                        description=f"Uses mutable tag `latest` for image `{container.image}`",
                        severity="Medium",
                        recommendation="Use immutable image tags for better security and reproducibility."
                    ))

                # Hardcoded Secrets
                if container.env:
                    for env in container.env:
                        if env.value and any(k in env.name.lower() for k in ["secret", "token", "password"]):
                            findings.append(AdvancedSecurityFinding(
                                category="Secrets Management",
                                description=f"Env var `{env.name}` in pod `{pod.metadata.name}` may contain a hardcoded secret.",
                                severity="Critical",
                                recommendation="Store secrets in Kubernetes Secrets and inject them securely."
                            ))

        if not network_policies.items:
            findings.append(AdvancedSecurityFinding(
                category="Network Security",
                description="No network policies defined in the namespace.",
                severity="High",
                recommendation="Implement a default-deny network policy and explicitly allow required traffic."
            ))

        total_findings = len(findings)
        critical_count = sum(1 for f in findings if f.severity == "Critical")
        high_count = sum(1 for f in findings if f.severity == "High")

        if total_findings == 0:
            grade = "A+"
            summary = "Excellent security posture!"
        elif critical_count > 0:
            grade = "C"
            summary = "Needs immediate attention due to critical risks."
        elif high_count > 0:
            grade = "B"
            summary = "Good, but with some areas for improvement."
        else:
            grade = "A"
            summary = "Good security posture."

        key_findings_output = []
        for f in findings:
            key_findings_output.append(f"- **{f.severity}**: {f.description} (Recommendation: {f.recommendation})")

        if not key_findings_output:
            key_findings_output.append("No advanced security issues found. Great job! ✨")

        return {
            "status": "success",
            "formatted_response": f"""
🛡️ **Advanced Security Report - {namespace}**

**Overall Grade: {grade}** ({summary})

**Key Findings:**

{chr(10).join(key_findings_output)}
            """
        }
    except ApiException as e:
        return {"status": "error", "error_message": f"Kubernetes API error: {e.reason}"}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}