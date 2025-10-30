# Security Best Practices

This document outlines security enhancements and best practices for using the centralized GitHub Actions.

## Phase 4: Security Enhancements

### 1. Secure Secrets Handling

All actions properly handle sensitive data:

#### `deploy-image`
- **GHCR Token:** Never logged or exposed in output
- **Passed via environment:** Token only in memory, not persisted
- **Scope validation:** Recommends minimum required permissions (`read:packages`)

**Best Practice:**
```yaml
- uses: hydn-co/build-tools/.github/actions/deploy-image@main
  with:
    ghcr_token: ${{ secrets.GITHUB_TOKEN }}  # ✅ Use secrets
    # ghcr_token: ${{ github.token }}        # ❌ Never hardcode
```

#### `deploy-bicep`
- **Azure credentials:** Uses OIDC (OpenID Connect) - no long-lived secrets
- **Subscription info:** Only displays subscription name, not ID in logs
- **Parameters:** Sensitive Bicep parameters not logged

**Best Practice:**
```yaml
permissions:
  id-token: write  # Required for OIDC
  contents: read   # Minimum permissions

- uses: hydn-co/build-tools/.github/actions/deploy-bicep@main
  # Azure CLI login via OIDC happens automatically in workflow
```

### 2. Container Image Security

#### Image Digest Pinning

All actions now provide image digests for verification:

```yaml
- name: Build Image
  id: build
  uses: hydn-co/build-tools/.github/actions/build-app@main
  with:
    app: authd
    # ... other inputs

- name: Verify Image
  run: |
    # Use digest instead of tag for maximum security
    DIGEST="${{ steps.build.outputs.digest }}"
    echo "Verifying image at digest: $DIGEST"
    # Deploy using digest for immutable reference
```

#### Multi-Architecture Security

Both architectures built from same source:
- **Reproducible builds:** Same Dockerfile, same build args
- **Manifest verification:** Ensures both arch images are correct
- **Digest tracking:** Each arch image has unique, verifiable digest

#### Registry Security

**GHCR (GitHub Container Registry):**
- ✅ Built-in GITHUB_TOKEN authentication
- ✅ Automatic package permissions via repository settings
- ✅ Audit logs for all push/pull operations
- ✅ Vulnerability scanning available

**ACR (Azure Container Registry):**
- ✅ OIDC authentication (no long-lived credentials)
- ✅ Microsoft Defender for Cloud integration
- ✅ Image quarantine capabilities
- ✅ Network isolation options

### 3. Least Privilege Permissions

All workflows use minimum required permissions:

#### Container Build Workflows

```yaml
permissions:
  contents: read      # Read repository code
  packages: write     # Push to GHCR
```

**Why these permissions:**
- `contents:read` - Checkout code, read Dockerfile
- `packages:write` - Push built images to GHCR

**Not needed:**
- ❌ `contents:write` - Never modify repository
- ❌ `actions:write` - No workflow modifications
- ❌ `issues:write` - No issue creation

#### Deployment Workflows

```yaml
permissions:
  id-token: write     # OIDC token for Azure
  contents: read      # Read Bicep templates
  packages: read      # Pull from GHCR
```

**Why these permissions:**
- `id-token:write` - Generate OIDC token for Azure authentication
- `contents:read` - Read Bicep templates and parameters
- `packages:read` - Pull images from GHCR for import to ACR

#### CI/Test Workflows

```yaml
permissions:
  contents: read      # Read source code only
```

**Why this permission:**
- `contents:read` - Checkout and test code

**Not needed:**
- ❌ `packages:write` - CI doesn't push images
- ❌ Any write permissions

### 4. Input Validation

All actions validate inputs to prevent injection attacks:

#### Semver Validation

```bash
if [[ ! "$SEMVER" =~ ^v[0-9]+\.[0-9]+\.[0-9]+ ]]; then
  echo "❌ ERROR: Invalid semver format"
  exit 1
fi
```

**Prevents:**
- Command injection via malformed version strings
- Path traversal attempts
- Shell escape sequences

#### Architecture Validation

```bash
if [[ ! "$ARCH" =~ ^(amd64|arm64)$ ]]; then
  echo "❌ ERROR: Invalid architecture"
  exit 1
fi
```

**Prevents:**
- Arbitrary command execution
- File system manipulation
- Registry confusion attacks

#### Boolean Validation

```bash
if [[ ! "$APPLY_CERTS" =~ ^(true|false)$ ]]; then
  echo "❌ ERROR: Invalid boolean value"
  exit 1
fi
```

**Prevents:**
- Logic bypasses
- Unexpected behavior
- Command injection

### 5. Audit Trail

All actions provide comprehensive logging for security audits:

#### What's Logged

**Build Actions:**
- ✅ Image references (registry/org/app:tag)
- ✅ Build arguments (non-sensitive)
- ✅ Cache usage
- ✅ Whether image was built or cached
- ✅ Build duration (via retry attempts)

**Deployment Actions:**
- ✅ Azure subscription name
- ✅ Deployment name and location
- ✅ Template and parameter files used
- ✅ Version being deployed
- ✅ Deployment provisioning state
- ✅ Portal link for troubleshooting

#### What's NOT Logged

**Never Logged (Security):**
- ❌ GHCR tokens
- ❌ Azure subscription IDs
- ❌ Secrets from Bicep parameters
- ❌ Connection strings
- ❌ API keys

### 6. Supply Chain Security

#### Source Verification

```yaml
# ✅ Pin to specific version or commit
- uses: hydn-co/build-tools/.github/actions/build-app@v1.0.0
- uses: hydn-co/build-tools/.github/actions/build-app@abc123def

# ⚠️  Development only - use @main for rapid iteration
- uses: hydn-co/build-tools/.github/actions/build-app@main

# ❌ Never use unpinned third-party actions
- uses: some-random-org/action  # NO VERSION = DANGEROUS
```

#### Build Provenance

Enable SLSA provenance for all builds:

```yaml
build:
  permissions:
    id-token: write  # Required for provenance
    packages: write
    attestations: write  # Required for GitHub attestations
```

Future enhancement: Add provenance generation to build-app action.

### 7. Azure OIDC Configuration

Federated credentials eliminate long-lived secrets for Azure deployments.

#### Setup Steps

1. **Create Azure AD App Registration**
2. **Create Federated Credential:**
   - Issuer: `https://token.actions.githubusercontent.com`
   - Subject: `repo:hydn-co/mesh-auth:environment:dev1`
   - Audience: `api://AzureADTokenExchange`

3. **Assign Permissions:**
   - Contributor on resource group or subscription
   - AcrPush on container registry (if using ACR tasks)

4. **Configure GitHub Secrets:**
   ```
   AZURE_CLIENT_ID: <app-registration-client-id>
   AZURE_TENANT_ID: <azure-tenant-id>
   AZURE_SUBSCRIPTION_ID: <subscription-id>
   ```

5. **Workflow Usage:**
   ```yaml
   - name: Azure Login
     uses: azure/login@v1
     with:
       client-id: ${{ secrets.AZURE_CLIENT_ID }}
       tenant-id: ${{ secrets.AZURE_TENANT_ID }}
       subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
   ```

**Benefits:**
- ✅ No passwords or service principal secrets
- ✅ Automatic token expiration (1 hour)
- ✅ Scoped to specific repositories/environments
- ✅ Full audit trail in Azure AD

## Security Checklist

Use this checklist when setting up new services:

### Repository Configuration

- [ ] **Branch protection** enabled on `main` and `develop`
  - [ ] Require pull request reviews
  - [ ] Require status checks
  - [ ] Require signed commits (recommended)

- [ ] **GitHub Actions permissions** set to least privilege
  - [ ] Read repository contents by default
  - [ ] Explicit permissions in each workflow

- [ ] **Secrets management**
  - [ ] GITHUB_TOKEN uses automatic scoping
  - [ ] Azure credentials use OIDC (no long-lived secrets)
  - [ ] Environment-specific secrets in GitHub Environments

### Workflow Configuration

- [ ] **Permissions blocks** in all workflows
  ```yaml
  permissions:
    contents: read  # Explicit, not inherited
  ```

- [ ] **Pin action versions**
  ```yaml
  uses: hydn-co/build-tools/.github/actions/build-app@v1
  # Not: @main (except during development)
  ```

- [ ] **Environment protection rules**
  - [ ] Required reviewers for production
  - [ ] Wait timer for production (optional)
  - [ ] Restrict to protected branches

### Action Usage

- [ ] **Use centralized actions** from build-tools
  - [ ] Regularly updated
  - [ ] Security reviewed
  - [ ] Input validation included

- [ ] **Never hardcode secrets**
  ```yaml
  # ❌ NEVER
  ghcr_token: ghp_abc123def456

  # ✅ ALWAYS
  ghcr_token: ${{ secrets.GITHUB_TOKEN }}
  ```

- [ ] **Verify outputs** before using in subsequent steps
  ```yaml
  - if: steps.build.outputs.digest != ''
    run: echo "Build successful with digest"
  ```

### Container Security

- [ ] **Base images** from trusted sources
  - [ ] Official images (golang, alpine, etc.)
  - [ ] Verify with digest pins in Dockerfile
  - [ ] Regular base image updates

- [ ] **Vulnerability scanning** enabled
  - [ ] GitHub Dependabot
  - [ ] Microsoft Defender for Cloud (ACR)
  - [ ] Automated PR creation for fixes

- [ ] **Image signing** (future enhancement)
  - [ ] Cosign or Notary v2
  - [ ] Verify signatures before deployment

### Azure Configuration

- [ ] **OIDC configured** for Azure deployments
  - [ ] Federated credentials created
  - [ ] Scoped to specific environments
  - [ ] No service principal secrets

- [ ] **Network isolation** where appropriate
  - [ ] Private endpoints for ACR
  - [ ] VNet integration for Container Apps
  - [ ] Firewall rules for Key Vault

- [ ] **Managed identities** for Azure resources
  - [ ] Container Apps use managed identity
  - [ ] Key Vault access via managed identity
  - [ ] No connection strings in config

## Security Contacts

- **Security Issues:** Create private security advisory in GitHub
- **Vulnerability Reports:** security@hydn.co
- **Azure Incidents:** Azure Portal support tickets

## Compliance

### GDPR
- Container logs retention: 30 days
- Build logs retention: 90 days (GitHub default)
- No personal data in container images

### SOC 2
- Audit trail: All deployments logged in Azure
- Access control: RBAC on all Azure resources
- Encryption: At rest (Azure Storage) and in transit (TLS 1.2+)

## Regular Security Reviews

Schedule quarterly reviews:
1. **Review action permissions** - Still minimal?
2. **Update base images** - Latest security patches?
3. **Rotate credentials** - Even OIDC has periodic rotation
4. **Audit access** - Who has admin on repositories?
5. **Check dependencies** - Dependabot alerts addressed?

