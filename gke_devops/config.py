#!/usr/bin/env python3
"""
GKE DevOps Agent - Kubernetes Configuration Module

This module handles Kubernetes client configuration and initialization.
Supports both in-cluster and local kubeconfig authentication.

Author: GKE DevOps Team
"""

from kubernetes import client, config

def initialize_k8s_clients():
    """Initialize Kubernetes API clients with proper authentication."""
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()
    
    return client.CoreV1Api(), client.AppsV1Api()

# Initialize global clients
k8s_v1, k8s_apps_v1 = initialize_k8s_clients()