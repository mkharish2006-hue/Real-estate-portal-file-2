# CI/CD Pipeline for Real Estate Portal using Azure DevOps

## Overview
This pipeline automates build, test, and deploy for the Flask app to Azure App Service.

## Prerequisites
- Azure DevOps account
- Azure subscription (for App Service, SQL DB)
- Git repo in Azure Repos

## Pipeline Setup (YAML)

Create `azure-pipelines.yml` in repo root:

```yaml
trigger:
  branches:
    include:
    - main

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: Build
  jobs:
  - job: BuildJob
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.9'
    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
      displayName: 'Install dependencies'
    - script: python -m unittest discover tests
      displayName: 'Run tests'
    - task: PublishTestResults@2
      inputs:
        testResultsFiles: '**/test-*.xml'
        testRunTitle: 'Python Tests'

- stage: Deploy
  condition: succeeded()
  jobs:
  - deployment: DeployJob
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              azureSubscription: 'YourSubscription'
              appName: 'real-estate-portal'
              package: '$(System.DefaultWorkingDirectory)/**'
              runtimeStack: 'PYTHON|3.9'
```

## Steps to Implement
1. **Create Azure DevOps Project**: Go to dev.azure.com, new project.
2. **Import Repo**: Push code to Azure Repos.
3. **Create Pipeline**: Use YAML above.
4. **Configure Environments**: Add production environment.
5. **Azure Resources**: Create App Service, SQL DB.
6. **Secrets**: Store DB connection in Key Vault.

## Showcase for Single User Story (e.g., Registration)
- Trigger pipeline on commit.
- Build installs deps, runs tests (including registration tests).
- Deploy to Azure App Service.
- Verify: Access app, register user, check DB.

This ensures automated testing and deployment.