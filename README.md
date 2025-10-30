# Build Tools

Centralized, reusable GitHub Actions for the mesh ecosystem.

## 📦 Available Actions

### Container Build Actions

#### `.github/actions/build-app`
Builds and pushes a single-architecture container image to a registry.

**Usage:**
```yaml
- uses: hydn-co/build-tools/.github/actions/build-app@main
  with:
    app: authd              # App name (matches cmd/<app>/)
    arch: amd64            # Architecture: amd64 or arm64
    semver: v1.2.3         # Semantic version tag
    registry: ghcr.io      # Container registry
    org: hydn-co           # Organization/namespace
```

**Features:**
- ✅ Idempotent (skips if image already exists)
- ✅ Uses Dockerfile from `cmd/<app>/Dockerfile`
- ✅ Tags with `registry/org/mesh-<app>:semver-arch`
- ✅ Automatic build arg injection (SEMVER)

#### `.github/actions/build-manifest`
Creates a multi-architecture manifest combining amd64 and arm64 images.

**Usage:**
```yaml
- uses: hydn-co/build-tools/.github/actions/build-manifest@main
  with:
    registry: ghcr.io
    org: hydn-co
    app: authd
    semver: v1.2.3
```

**Features:**
- ✅ Combines `semver-amd64` and `semver-arm64` into single `semver` tag
- ✅ Validates both architectures exist before creating manifest
- ✅ Idempotent (skips if manifest already exists)
- ✅ Returns manifest reference as output

### Deployment Actions

#### `.github/actions/deploy-bicep`
Deploys Azure Bicep templates using subscription-scoped deployment.

**Usage:**
```yaml
- uses: hydn-co/build-tools/.github/actions/deploy-bicep@main
  with:
    environment: dev1      # Environment name
    name: mesh-auth        # Deployment name
    semver: v1.2.3        # Version to deploy
    applyCerts: "false"   # Optional: Apply certificates
```

**Features:**
- ✅ Subscription-scoped deployment
- ✅ Loads parameters from `.deploy/bicep/parameters/<environment>.bicepparam`
- ✅ Template from `.deploy/bicep/main.bicep`
- ✅ Automatic parameter override (semver, applyCerts)

#### `.github/actions/deploy-image`
Imports container images from GitHub Container Registry (GHCR) to Azure Container Registry (ACR).

**Usage:**
```yaml
- uses: hydn-co/build-tools/.github/actions/deploy-image@main
  with:
    org: hydn-co
    package: mesh-authd    # GHCR package name
    semver: v1.2.3
    acr_name: hydnacr      # ACR short name (not FQDN)
    ghcr_user: ${{ github.actor }}
    ghcr_token: ${{ secrets.GITHUB_TOKEN }}
```

**Features:**
- ✅ Idempotent (skips if image already exists in ACR)
- ✅ Imports multi-arch manifests
- ✅ Uses Azure CLI `az acr import`
- ✅ Automatic authentication to GHCR

#### `.github/actions/create-tag`
Creates an annotated Git tag for a release. Safe to run multiple times.

**Usage:**
```yaml
- uses: hydn-co/build-tools/.github/actions/create-tag@main
  with:
    semver: v1.2.3
    message: "Release v1.2.3 deployed to prod1"  # Optional
    push: true                                    # Optional, default: true
```

**Features:**
- ✅ Idempotent (not an error if tag exists)
- ✅ Validates semver format
- ✅ Annotated tags with custom messages
- ✅ Automatic push to remote with retry logic
- ✅ Warns if tag points to different commit

#### `.github/actions/prune-tags`
Removes old pre-release Git tags, keeping only the latest N. Never removes stable releases.

**Usage:**
```yaml
- uses: hydn-co/build-tools/.github/actions/prune-tags@main
  with:
    keep-count: 10        # Optional, default: 10
    dry-run: false        # Optional, default: false
    push: true            # Optional, default: true
```

**Features:**
- ✅ Distinguishes pre-release (v1.2.3-alpha) from stable (v1.2.3)
- ✅ Never deletes stable release tags
- ✅ Keeps N most recent pre-release tags
- ✅ Dry-run mode to preview deletions
- ✅ Automatic remote cleanup
- ✅ Outputs: deleted-count, deleted-tags, kept-count

**Tag Classification:**
- **Stable:** `v1.2.3` (no suffix) - **NEVER DELETED**
- **Pre-release:** `v1.2.3-alpha.1`, `v1.2.3-dev.20241030` - kept only latest N

#### `.github/actions/prune-packages`
Removes old pre-release container images from GHCR, keeping only the latest N. Never removes stable releases.

**Usage:**
```yaml
- uses: hydn-co/build-tools/.github/actions/prune-packages@main
  with:
    org: hydn-co
    package-prefix: mesh-    # Optional, filter packages
    keep-count: 10           # Optional, default: 10
    dry-run: false           # Optional, default: false
    token: ${{ secrets.GITHUB_TOKEN }}
```

**Features:**
- ✅ Processes multiple packages in one run
- ✅ Distinguishes pre-release from stable container tags
- ✅ Never deletes stable release images
- ✅ Keeps N most recent pre-release images per package
- ✅ Package prefix filtering (e.g., `mesh-` matches mesh-authd, mesh-brokerd)
- ✅ Dry-run mode to preview deletions
- ✅ Outputs: deleted-count, packages-processed, total-versions

**Image Classification:**
- **Stable:** `v1.2.3` tag - **NEVER DELETED**
- **Pre-release:** `v1.2.3-alpha.1`, `v1.2.3-dev.20241030` - kept only latest N per package

## 🔄 Migration Guide

### From Local Actions to Centralized

**Before** (in each repository):
```yaml
- uses: ./.github/actions/build-app
  with:
    app: authd
    # ... inputs
```

**After** (using centralized):
```yaml
- uses: hydn-co/build-tools/.github/actions/build-app@main
  with:
    app: authd
    # ... inputs
```

### Benefits
- ✅ **Single source of truth**: Update once, applies everywhere
- ✅ **Consistency**: All projects use identical, tested actions
- ✅ **Maintainability**: Bug fixes and improvements in one place
- ✅ **Versioning**: Pin to specific versions with `@main`, `@v1`, or commit SHA
- ✅ **Resilient**: Input validation and error handling with clear diagnostics
- ✅ **Fail-fast**: Pre-flight checks catch issues before expensive operations

## 📚 Documentation

- **[ERROR_HANDLING.md](./.github/actions/ERROR_HANDLING.md)** - Error handling, validation, and diagnostics
- **[ADVANCED_FEATURES.md](./.github/actions/ADVANCED_FEATURES.md)** - Outputs, retry logic, caching, and health checks
- **[SECURITY.md](./.github/actions/SECURITY.md)** - Security best practices, OIDC, and compliance
- **[MIGRATION.md](./MIGRATION.md)** - Migration guide from local to centralized actions
- **[QUICKSTART.md](./QUICKSTART.md)** - Quick start guide for new services
- **[COMPARISON.md](./COMPARISON.md)** - Before/after comparison

## 📋 Action Details

### Common Inputs

Most actions share these common inputs:

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `app` | Application name (e.g., authd, brokerd) | ✅ | - |
| `semver` | Semantic version tag | ✅ | - |
| `registry` | Container registry URL | ✅ | - |
| `org` | Organization/namespace | ✅ | - |

### Environment Requirements

These actions expect:
- **Docker**: BuildKit enabled for multi-platform builds
- **Azure CLI**: For deployment actions (OIDC authentication preferred)
- **Repository Structure**:
  ```
  repo/
  ├── cmd/
  │   └── <app>/
  │       └── Dockerfile
  └── .deploy/
      └── bicep/
          ├── main.bicep
          └── parameters/
              └── <environment>.bicepparam
  ```

## 🏷️ Versioning

This repository follows semantic versioning:

- **`@main`**: Latest development version (recommended for getting latest features)
- **`@v1`**: Latest stable v1.x.x (for production stability)
- **`@v1.2.3`**: Specific version (maximum stability)

**Recommendation**: Use `@main` for most workflows to get the latest features and improvements.

## 🤝 Contributing

When updating actions:

1. Make changes in the appropriate `actions/<name>/` directory
2. Test in a development repository first
3. Update this README with any new inputs or behavior
4. Create a PR with clear description of changes
5. Tag a new version after merge if breaking changes

## 📝 Examples

### Complete Container Build Workflow

```yaml
name: Build Containers

on:
  push:
    branches: [main]
    paths:
      - 'cmd/**'
      - 'internal/**'

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      packages: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Get Version
        id: version
        run: echo "semver=v1.0.0" >> $GITHUB_OUTPUT
      
      - name: Build amd64
        uses: hydn-co/build-tools/.github/actions/build-app@main
        with:
          app: authd
          arch: amd64
          semver: ${{ steps.version.outputs.semver }}
          registry: ghcr.io
          org: hydn-co
      
      - name: Build arm64
        uses: hydn-co/build-tools/.github/actions/build-app@main
        with:
          app: authd
          arch: arm64
          semver: ${{ steps.version.outputs.semver }}
          registry: ghcr.io
          org: hydn-co
      
      - name: Create Manifest
        uses: hydn-co/build-tools/.github/actions/build-manifest@main
        with:
          registry: ghcr.io
          org: hydn-co
          app: authd
          semver: ${{ steps.version.outputs.semver }}
```

### Complete Deployment Workflow

```yaml
name: Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        required: true
        type: string

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Get Version
        id: version
        run: echo "semver=v1.0.0" >> $GITHUB_OUTPUT
      
      - name: Deploy Infrastructure
        uses: hydn-co/build-tools/.github/actions/deploy-bicep@main
        with:
          environment: ${{ inputs.environment }}
          name: mesh-auth
          semver: ${{ steps.version.outputs.semver }}
      
      - name: Import Container
        uses: hydn-co/build-tools/.github/actions/deploy-image@main
        with:
          org: hydn-co
          package: mesh-authd
          semver: ${{ steps.version.outputs.semver }}
          acr_name: hydnacr
          ghcr_user: ${{ github.actor }}
          ghcr_token: ${{ secrets.GITHUB_TOKEN }}
```

## 📚 Documentation

For comprehensive documentation, see the [docs/](./docs/) directory:

- **[Advanced Features](./docs/advanced-features.md)** - Comprehensive outputs, caching, and advanced workflows
- **[Error Handling](./docs/error-handling.md)** - Validation, resilience, and troubleshooting
- **[Security](./docs/security.md)** - Best practices for secure deployments and secret handling

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Creating Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Azure Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Docker Multi-platform Builds](https://docs.docker.com/build/building/multi-platform/)
