# Infrastructure and Deployment

This directory contains all infrastructure, deployment, and operational configurations for the GAM API project.

## Directory Structure

```
infrastructure/
├── deploy/           # Deployment scripts and configurations
│   ├── cloud-run-deploy.sh    # Google Cloud Run deployment
│   ├── quick-deploy.sh        # Quick deployment script
│   ├── setup-credentials.sh   # Credential setup
│   └── setup-secrets.sh       # Secret management
├── docker/           # Docker configurations (if needed)
├── kubernetes/       # K8s manifests (if needed)
└── terraform/        # Infrastructure as Code (if needed)
```

## Deployment Guides

- [Authentication Setup](deploy/AUTHENTICATION.md)
- [Deployment Guide](deploy/DEPLOYMENT_FINAL.md)
- [Deployment Success](deploy/DEPLOYMENT_SUCCESS.md)

## Quick Start

1. **Setup credentials**:
   ```bash
   ./deploy/setup-credentials.sh
   ```

2. **Deploy to Cloud Run**:
   ```bash
   ./deploy/quick-deploy.sh
   ```

## Environment Variables

Required environment variables for deployment:
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key
- `PROJECT_ID` - Google Cloud project ID
- `REGION` - Deployment region (default: us-central1)
- `MCP_AUTH_ENABLED` - Enable MCP authentication (true/false)

## Security Notes

- Never commit credentials or secrets to the repository
- Use Google Secret Manager for production secrets
- Follow the principle of least privilege for service accounts