#!/usr/bin/env python3
"""
GKE DevOps Agent - Pydantic Models

This module defines the Pydantic models used by the GKE DevOps Agent.
"""

from pydantic import BaseModel

class Pod(BaseModel):
    name: str
    status: str
    ready: str
    restarts: int
    age: str
    node: str

class Deployment(BaseModel):
    name: str
    ready: str
    up_to_date: str
    available: str
    age: str

class Issue(BaseModel):
    name: str
    status: str
    reason: str
    details: str

class Node(BaseModel):
    name: str
    status: str
    version: str

class SecurityFinding(BaseModel):
    resource: str
    issue: str
    severity: str
    recommendation: str

class CostRecommendation(BaseModel):
    title: str
    issue: str
    risk_or_opportunity: str
    potential_savings: str
    action: str

class AdvancedSecurityFinding(BaseModel):
    category: str
    description: str
    severity: str
    recommendation: str
