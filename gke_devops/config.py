#!/usr/bin/env python3
"""
GKE DevOps Agent - Kubernetes Configuration Module

This module handles Kubernetes client configuration and initialization.
Supports both in-cluster and local kubeconfig authentication.

Author: GKE DevOps Team
"""

from kubernetes import client, config

def initialize_k8s_clients():
    """
    Initialize Kubernetes API clients with proper authentication.
    
    Attempts in-cluster configuration first (for pods running in K8s),
    then falls back to local kubeconfig for development/external access.
    
    Returns:
        tuple: (CoreV1Api, AppsV1Api, NetworkingV1Api) - Kubernetes API client instances
    """
    try:
        # Try in-cluster config first (when running inside Kubernetes)
        config.load_incluster_config()
    except:
        # Fall back to local kubeconfig (for development/external access)
        config.load_kube_config()
    
    return client.CoreV1Api(), client.AppsV1Api(), client.NetworkingV1Api()

# === GLOBAL CLIENT INITIALIZATION ===
# Initialize Kubernetes API clients for use across all modules
k8s_v1, k8s_apps_v1, k8s_networking_v1 = initialize_k8s_clients()