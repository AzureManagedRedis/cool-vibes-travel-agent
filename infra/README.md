# Infrastructure Deployment Guide

This directory contains the Infrastructure as Code (IaC) for deploying the Cool Vibes Travel Agent application to Azure using Azure Developer CLI (azd).

## Architecture

The deployment includes:
- **Azure OpenAI Service** - GPT-4 model for the AI agent
- **Azure Managed Redis** - Persistent storage for user preferences
- **Azure Container Apps** - Hosting the Python application
- **Azure Container Registry** - Storing the container image
- **Log Analytics** - Monitoring and diagnostics

## Prerequisites

1. **Install Azure Developer CLI (azd)**
   ```bash
   # macOS
   brew tap azure/azd && brew install azd
   
   # Windows (PowerShell)
   powershell -ex AllSigned -c "Invoke-RestMethod 'https://aka.ms/install-azd.ps1' | Invoke-Expression"
   
   # Linux
   curl -fsSL https://aka.ms/install-azd.sh | bash
   ```

2. **Install Azure CLI**
   ```bash
   # macOS
   brew install azure-cli
   
   # Windows
   winget install Microsoft.AzureCLI
   
   # Linux
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   ```

3. **Install Docker** (for building container images)
   - Download from https://www.docker.com/products/docker-desktop

4. **Azure Subscription** with permissions to create resources

## Deployment Steps

### 1. Initialize azd environment

```bash
# Login to Azure
azd auth login

# Initialize the environment (first time only)
azd init
```

When prompted:
- Environment name: Choose a name (e.g., `dev`, `prod`)
- Location: Choose an Azure region (e.g., `eastus`, `westus2`)

### 2. Deploy infrastructure and application

```bash
# Provision infrastructure and deploy application
azd up
```

This command will:
1. Create all Azure resources defined in `infra/main.bicep`
2. Build the Docker container from `Dockerfile`
3. Push the container to Azure Container Registry
4. Deploy the container to Azure Container Apps

### 3. Access the application

After deployment completes, azd will output the application URL:

```
Service web URI: https://ca-xxxxx.region.azurecontainerapps.io
```

Navigate to this URL in your browser to access the DevUI interface.

## Environment Variables

The application automatically receives these environment variables from Azure:

- `REDIS_URL` - Redis connection string
- `AZURE_OPENAI_ENDPOINT` - OpenAI service endpoint
- `AZURE_OPENAI_API_KEY` - OpenAI API key (stored as secret)
- `AZURE_OPENAI_API_VERSION` - API version (2024-08-01-preview)
- `AZURE_OPENAI_DEPLOYMENT_NAME` - Model deployment name (gpt-4)

## Customization

### Change Azure OpenAI Model

Edit `infra/main.bicep`:

```bicep
param openAiModelName string = 'gpt-4'          // Change model
param openAiModelVersion string = '0613'         // Change version
param openAiModelCapacity int = 10               // Change capacity
```

### Change Redis SKU

Edit `infra/main.bicep`:

```bicep
param redisSku string = 'Balanced_B1'  // Options: Balanced_B0-B50, ComputeOptimized_X5-X50, MemoryOptimized_M10-M50
```

**Available SKU Tiers:**
- **Balanced**: B0, B1, B3, B5, B10, B20, B50 (general purpose)
- **Compute Optimized**: X5, X10, X20, X50 (high CPU performance)
- **Memory Optimized**: M10, M20, M50 (large cache sizes)

**Note**: AMR SKUs do not have a separate capacity parameter - capacity is determined by the SKU tier.

### Change Container Resources

Edit `infra/main.bicep`:

```bicep
param containerCpuCoreCount string = '1.0'       // CPU cores
param containerMemory string = '2.0Gi'           // Memory
param containerMinReplicas int = 1               // Min instances
param containerMaxReplicas int = 10              // Max instances
```

## Useful Commands

```bash
# Deploy only infrastructure changes
azd provision

# Deploy only application code changes
azd deploy

# View deployment logs
azd monitor --logs

# View all resources in the environment
azd show

# Delete all resources
azd down
```

## Monitoring

View application logs and metrics:

```bash
# Stream logs in terminal
azd monitor --logs

# Open Azure Portal
azd show --resource-group
```

Or navigate to Azure Portal → Container Apps → Logs

## Troubleshooting

### Container won't start

Check logs:
```bash
azd monitor --logs
```

Common issues:
- Missing environment variables
- Redis connection errors
- OpenAI API key invalid

### Deployment fails

```bash
# View detailed error
azd provision --debug

# Check resource group in Azure Portal
azd show --resource-group
```

### Can't access the application

1. Verify Container App is running:
   ```bash
   az containerapp show --name <app-name> --resource-group <rg-name>
   ```

2. Check if external ingress is enabled

3. Verify firewall/network settings

## Clean Up

To delete all resources:

```bash
azd down --purge
```

This will delete:
- Resource group and all resources
- Local environment configuration
