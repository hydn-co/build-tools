# Build Tools - Common GitHub Actions

Centralized, reusable GitHub Actions for the mesh ecosystem.

## 🎯 Purpose

This repository contains normalized, polished GitHub Actions used across all mesh services. Instead of duplicating actions in each service repository, all services reference these centralized actions.

## 📦 Actions

- **[build-app](actions/build-app)** - Build and push single-architecture container images
- **[build-manifest](actions/build-manifest)** - Create multi-architecture manifests
- **[deploy-bicep](actions/deploy-bicep)** - Deploy Azure Bicep templates
- **[deploy-image](actions/deploy-image)** - Import images from GHCR to ACR

## 🚀 Quick Start

### Using in Your Workflow

```yaml
- uses: hydn-co/build-tools/actions/build-app@v1
  with:
    app: authd
    arch: amd64
    semver: v1.2.3
    registry: ghcr.io
    org: hydn-co
```

### Version Pinning

- `@main` - Latest development version
- `@v1` - Latest stable v1.x.x (recommended for production)
- `@v1.2.3` - Specific version (maximum stability)

## 📚 Documentation

- **[README.md](README.md)** - Complete action documentation and examples
- **[MIGRATION.md](MIGRATION.md)** - Guide for migrating from local actions
- **[COMPARISON.md](COMPARISON.md)** - Detailed before/after comparison

## 🔄 Migration Status

| Repository | Status | Notes |
|------------|--------|-------|
| mesh-auth | 🟡 Pending | Ready to migrate |
| mesh-broker | 🟡 Pending | Ready to migrate |
| mesh-stream | 🟡 Pending | Ready to migrate |
| mesh-core | 🟡 Pending | Ready to migrate |

## 🤝 Contributing

1. Create feature branch
2. Make changes to actions
3. Test in at least one consumer repository
4. Create PR with clear description
5. Update version tags after merge

## 📜 License

MIT License - see [LICENSE](LICENSE) for details
