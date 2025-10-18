# GKE DevOps Agent Framework

A professional Google Agent Development Kit (ADK) implementation for Kubernetes cluster management through conversational AI.

## Overview

This project provides a production-ready ADK agent that enables natural language interaction with Google Kubernetes Engine (GKE) clusters. The agent offers real-time cluster monitoring, pod management, and deployment oversight through a web-based chat interface.

## Architecture

```
┌─────────────────────────────────────────┐
│           ADK Web Interface             │
│         (Chat-based UI)                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         GKE DevOps Agent                │
│    (Google ADK + Gemini 2.0 Flash)     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Kubernetes Python Client         │
│     (Real-time cluster access)         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         GKE Cluster                     │
│    (Live cluster monitoring)           │
└─────────────────────────────────────────┘
```

## Features

### Core Capabilities
- **Cluster Health Monitoring** - Real-time node and pod status with detailed metrics
- **Pod Management** - Comprehensive pod status with container readiness, restart counts, age, and node assignments
- **Deployment Oversight** - Deployment status and replica management
- **Issue Diagnostics** - Automated problem detection with actionable recommendations
- **Dashboard-Style Formatting** - Professional output with emojis, dividers, and structured layouts
- **Real-Time Metrics** - Health percentages, pod density, system reliability scores

### Technical Stack
- **Google ADK** - Agent Development Kit framework
- **Gemini 2.0 Flash** - Large language model for natural language processing
- **Kubernetes Python Client** - Direct cluster API integration
- **Enhanced Formatting** - Professional dashboard-style responses
- **Real-Time Data** - Live cluster monitoring and status updates

## Quick Start

### Prerequisites
- Google Cloud Platform account
- GKE cluster (running)
- Python 3.11+
- `kubectl` configured

### Installation

1. **Clone and Setup**
   ```bash
   cd adk_agents
   pip install -r requirements.txt
   ```

2. **Configure Kubernetes Access**
   ```bash
   gcloud container clusters get-credentials YOUR_CLUSTER --zone=YOUR_ZONE
   kubectl cluster-info  # Verify connection
   ```

3. **Start ADK Web Interface**
   ```bash
   adk web . --port=8080
   ```

4. **Access Web Chat**
   ```
   http://localhost:8080
   ```

## Usage

### Chat Commands

| Command | Description | Example |
|---------|-------------|---------|
| `"Check cluster health"` | Overall cluster status | Node and pod health summary |
| `"Show pod status"` | Pod details by namespace | Running, pending, failed pods |
| `"List deployments"` | Deployment information | Replica counts and status |
| `"Diagnose issues"` | Problem detection | Failed pods and recommendations |

### Sample Interactions

**Cluster Health Check:**
```
User: "Check my cluster health"

Agent: 🏥 **GKE Cluster Health Dashboard**

       🟢 **EXCELLENT** - All systems operational

       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

       🖥️ **Infrastructure Status**
          📍 **Nodes**: 1/1 ready (100%)
          🔧 **Node Details**:
             • gke-gemini-gke-cluster-default-pool-xxx: ✅ v1.30.5-gke.1014001

       🚀 **Workload Status**
          📊 **Pod Health**: 100% operational
          ✅ **Running**: 15 pods
          ⏳ **Pending**: 0 pods
          ❌ **Failed**: 0 pods
          📈 **Total Workloads**: 15 pods

       🎯 **Status**: 🎉 Your cluster is performing optimally!
```

**Pod Status Inquiry:**
```
User: "Show pod status in default namespace"

Agent: 📦 **Pod Status Dashboard - default namespace**

       🟢 **EXCELLENT** - All pods healthy

       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

       📊 **Pod Health Summary**:
          📈 **Health Score**: 100%
          🔢 **Total Pods**: 8
          🟢 **Running**: 8 pods

       🚀 **Detailed Pod Status** (showing first 10):
          🟢 **nginx-deployment-xxx**
             └─ Status: Running | Ready: 1/1 | Restarts: 0 | Age: 2d | Node: gke-node-xxx
          🟢 **api-service-xxx**
             └─ Status: Running | Ready: 1/1 | Restarts: 0 | Age: 1d | Node: gke-node-xxx

       🎯 **Recommendation**: 🎉 All pods are running smoothly!
```

## Project Structure

```
adk_agents/
├── gke_devops/
│   ├── __init__.py
│   ├── agent.py          # Main ADK agent
│   └── requirements.txt  # Dependencies
├── README.md            # This file
└── .env                 # Environment variables
```

## Configuration

### Environment Variables
```bash
# Optional: Custom cluster context
KUBECONFIG=/path/to/kubeconfig

# Optional: Default namespace
DEFAULT_NAMESPACE=default
```

### Agent Configuration
The agent is configured in `agent.py`:
- **Model**: `gemini-2.0-flash`
- **Tools**: 4 enhanced Kubernetes functions with dashboard formatting
- **Instruction**: Professional DevOps assistant with detailed insights
- **Output Format**: Dashboard-style with emojis, dividers, and structured metrics
- **Real-Time Data**: Live cluster monitoring with health percentages and detailed pod information

## Development

### Adding New Tools
```python
def new_tool(param: str) -> dict:
    """Tool description."""
    try:
        # Implementation
        return {"status": "success", "formatted_response": "..."}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

# Add to agent tools list
root_agent = Agent(
    # ... existing config
    tools=[existing_tools, new_tool]
)
```

### Testing
```bash
# Test agent locally
python -c "from gke_devops.agent import root_agent; print(root_agent.name)"

# Test Kubernetes connection
kubectl get nodes
```

## Deployment

### Local Development
```bash
adk web . --port=8080 --reload
```

### Production Deployment
```bash
# Build container
docker build -t gke-devops-agent .

# Deploy to GKE
kubectl apply -f k8s-deployment.yaml
```

## Security

### RBAC Permissions
The agent requires these Kubernetes permissions:
- `pods`: `get`, `list`, `watch`
- `nodes`: `get`, `list`, `watch`
- `deployments`: `get`, `list`
- `events`: `get`, `list`

### Best Practices
- Use dedicated service accounts
- Implement least privilege access
- Enable audit logging
- Regular security updates

## Monitoring

### Agent Metrics
- Response times per tool
- Success/failure rates
- User interaction patterns
- Cluster connection health
- Dashboard formatting performance

### Cluster Insights
- Real-time health scores and percentages
- Pod density and distribution metrics
- Container readiness and restart tracking
- Node assignment and resource distribution
- System reliability and uptime percentages
- Enhanced pod lifecycle with age and restart counts

## Troubleshooting

### Common Issues

**Connection Errors:**
```bash
# Verify cluster access
kubectl cluster-info
gcloud container clusters get-credentials CLUSTER_NAME --zone=ZONE
```

**Agent Not Loading:**
```bash
# Check ADK installation
pip show google-adk
pip install --upgrade google-adk
```

**Permission Denied:**
```bash
# Verify RBAC
kubectl auth can-i get pods
kubectl describe clusterrolebinding
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/enhancement`)
3. Commit changes (`git commit -m 'Add enhancement'`)
4. Push to branch (`git push origin feature/enhancement`)
5. Create Pull Request

### Development Guidelines
- Follow Google ADK patterns
- Include comprehensive docstrings
- Add error handling for all tools
- Test with real GKE clusters
- Update documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create GitHub issues for bugs
- Use discussions for questions
- Check ADK documentation: https://google.github.io/adk-docs/

---

**Built with Google ADK and Kubernetes Python Client**

### Current Status
- **Live Cluster**: `gemini-gke-cluster` in project `green-cell-474517-d5`
- **Cluster Health**: ✅ Operational (1 node, 15 pods)
- **Agent Status**: 🟢 Active on ADK web server (port 8080)
- **Enhanced Features**: Dashboard-style formatting with detailed metrics
- **Last Updated**: Enhanced pod status display with container readiness, restart counts, pod age, and node assignments